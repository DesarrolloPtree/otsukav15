# -*- coding: utf-8 -*-

import base64
from itertools import groupby
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import requests
from pytz import timezone

from lxml import etree
from lxml.objectify import fromstring
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr

_logger = logging.getLogger(__name__)

CFDI_TEMPLATE_33 = 'itl_l10n_mx_edi_extended.cfdiv33_v2'
CFDI_XSLT_CADENA = 'l10n_mx_edi/data/%s/cadenaoriginal.xslt'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_edi/data/xslt/3.3/cadenaoriginal_TFD_1_1.xslt'

def create_list_html(array):
    '''Convert an array of string to a html list.
    :param array: A list of strings
    :return: an empty string if not array, an html list otherwise.
    '''
    if not array:
        return ''
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    l10n_mx_edi_usage = fields.Selection(selection_add=[('S01','Sin efectos fiscales'),
                                                       ('CP01','Pagos'),
                                                       ('CN01','Nómina')])
    
    def _l10n_mx_edi_create_taxes_cfdi_values(self):
        '''Create the taxes values to fill the CFDI template.
        '''
        self.ensure_one()
        values = {
            'total_withhold': 0,
            'total_transferred': 0,
            'withholding': [],
            'transferred': [],
        }
        taxes = {}
        itl_include_in_tax = False
        itl_ieps_tax = False
        tax_included_ids = False
        for line in self.invoice_line_ids:
            for tax in line.tax_ids.flatten_taxes_hierarchy().filtered(lambda r: r.l10n_mx_cfdi_tax_type != 'Exento'):
                if tax.itl_include_in_tax:
                    itl_include_in_tax = True
                    itl_ieps_tax = tax
                    tax_included_ids = tax.itl_taxes.mapped('id')
        for line in self.invoice_line_ids.filtered('price_subtotal'):
            price = line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)
            tax_line = {tax['id']: tax for tax in line.tax_ids.with_context(force_sign=line.move_id._get_tax_force_sign()).compute_all(
                price, line.currency_id, line.quantity, line.product_id, line.partner_id, self.type in ('in_refund', 'out_refund'))['taxes']}
            for tax in line.tax_ids.flatten_taxes_hierarchy().filtered(lambda r: r.l10n_mx_cfdi_tax_type != 'Exento'):
                tax_dict = tax_line.get(tax.id, {})
                amount = round(abs(tax_dict.get(
                    'amount', tax.amount / 100 * float("%.2f" % line.price_subtotal))), 2)
                if itl_include_in_tax and tax.id == itl_ieps_tax.id:
                    ieps_amount = amount
                    continue
                if itl_include_in_tax and tax.id in tax_included_ids:
                    amount = amount - ieps_amount
                rate = round(abs(tax.amount), 6)
                if tax.id not in taxes:
                    taxes.update({tax.id: {
                        'name': (tax.invoice_repartition_line_ids.tag_ids[0].name
                                 if tax.mapped('invoice_repartition_line_ids.tag_ids') else tax.name).upper(),
                        'amount': amount,
                        'rate': rate if tax.amount_type == 'fixed' else rate / 100.0,
                        'type': tax.l10n_mx_cfdi_tax_type,
                        'tax_amount': tax_dict.get('amount', tax.amount),
                    }})
                else:
                    taxes[tax.id].update({
                        'amount': taxes[tax.id]['amount'] + amount
                    })
                if tax.amount >= 0:
                    values['total_transferred'] += amount
                else:
                    values['total_withhold'] += amount
        values['transferred'] = [tax for tax in taxes.values() if tax['tax_amount'] >= 0]
        values['withholding'] = self._l10n_mx_edi_group_withholding(
            [tax for tax in taxes.values() if tax['tax_amount'] < 0])
        return values
    
    def _l10n_mx_edi_create_cfdi(self):
        '''Creates and returns a dictionnary containing 'cfdi' if the cfdi is well created, 'error' otherwise.
        '''
        self.ensure_one()
        qweb = self.env['ir.qweb']
        error_log = []
        company_id = self.company_id
        pac_name = company_id.l10n_mx_edi_pac
        if self.l10n_mx_edi_external_trade:
            # Call the onchange to obtain the values of l10n_mx_edi_qty_umt
            # and l10n_mx_edi_price_unit_umt, this is necessary when the
            # invoice is created from the sales order or from the picking
            self.invoice_line_ids.onchange_quantity()
            self.invoice_line_ids._set_price_unit_umt()
        values = self._l10n_mx_edi_create_cfdi_values()

        # -----------------------
        # Check the configuration
        # -----------------------
        # -Check certificate
        certificate_ids = company_id.l10n_mx_edi_certificate_ids
        certificate_id = certificate_ids.sudo().get_valid_certificate()
        if not certificate_id:
            error_log.append(_('No valid certificate found'))

        # -Check PAC
        if pac_name:
            pac_test_env = company_id.l10n_mx_edi_pac_test_env
            pac_password = company_id.l10n_mx_edi_pac_password
            if not pac_test_env and not pac_password:
                error_log.append(_('No PAC credentials specified.'))
        else:
            error_log.append(_('No PAC specified.'))

        if error_log:
            return {'error': _('Please check your configuration: ') + create_list_html(error_log)}

        # -Compute date and time of the invoice
        time_invoice = datetime.strptime(self.l10n_mx_edi_time_invoice,
                                         DEFAULT_SERVER_TIME_FORMAT).time()
        # -----------------------
        # Create the EDI document
        # -----------------------
        version = self.l10n_mx_edi_get_pac_version()

        # -Compute certificate data
        values['date'] = datetime.combine(
            fields.Datetime.from_string(self.invoice_date), time_invoice).strftime('%Y-%m-%dT%H:%M:%S')
        values['certificate_number'] = certificate_id.serial_number
        values['certificate'] = certificate_id.sudo().get_data()[0]
        ################################# Customization ##########################################
        # Recalculate taxes values for special ieps
        if self.itl_iesp_special:
            values['itl_iesp_special'] = self.itl_iesp_special
            values['itl_transferred'] = self.get_new_taxes()
            lines, tax_ieps_id = self.get_extra_line_ieps()
            ieps_line = [x for x in lines if 'IEPS' in x['name']]
            for tax in values['itl_transferred']:
                if tax['tax'].id in tax_ieps_id.itl_taxes.ids:
                    if self.type == 'out_invoice':
                        tax['tax_dict']['base'] = round(self.amount_untaxed - ieps_line[0]['credit'], 2)
                    if self.type == 'out_refund':
                        tax['tax_dict']['base'] = round(self.amount_untaxed - ieps_line[0]['debit'], 2)
                    tax['tax_amount'] = round(float(tax['tax_dict']['base']) * float(tax['tasa']), 2)
                    tax['tax_dict']['amount'] = tax['tax_amount']
        #raise UserError("Testing..")
        ###########################################################################################
        # -Compute cfdi
        cfdi = qweb.render(CFDI_TEMPLATE_33, values=values)
        cfdi = cfdi.replace(b'xmlns__', b'xmlns:')
        node_sello = 'Sello'
        attachment = self.sudo().env.ref('l10n_mx_edi.xsd_cached_cfdv33_xsd', False)
        xsd_datas = base64.b64decode(attachment.datas) if attachment else b''
        # -Compute cadena
        tree = self.l10n_mx_edi_get_xml_etree(cfdi)
        cadena = self.l10n_mx_edi_generate_cadena(CFDI_XSLT_CADENA % version, tree)
        tree.attrib[node_sello] = certificate_id.sudo().get_encrypted_cadena(cadena)

        # Check with xsd
        if xsd_datas:
            try:
                with BytesIO(xsd_datas) as xsd:
                    _check_with_xsd(tree, xsd)
            except (IOError, ValueError):
                _logger.info(
                    _('The xsd file to validate the XML structure was not found'))
            except Exception as e:
                return {'error': (_('The cfdi generated is not valid') +
                                    create_list_html(str(e).split('\\n')))}
        
        return {'cfdi': etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')}