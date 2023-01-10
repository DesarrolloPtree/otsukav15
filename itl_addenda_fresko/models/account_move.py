from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from lxml.objectify import fromstring
import base64
from lxml import etree
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"


    order_date = fields.Date(string="Fecha de la Orden", copy=False)
    numero_aprobacion = fields.Char(string="Número de aprobación", copy=False, default="0")

    def addenda_fresko_validations(self):
        if not self.order_date:
            raise ValidationError("Debe colocar la Fecha de la Orden")
        if not self.ref:
            raise ValidationError("Debe colocar la referencia a la Orden de Compra")
        if not self.numero_aprobacion:
            raise ValidationError("Debe colocar el Número de Aprobación, sino lo conoce coloque un '0'.")
        if not self.partner_id.gnl_fresko:
            raise ValidationError("Falta colocar el GLN del cliente.")
        if not self.company_id.partner_id.gnl_fresko:
            raise ValidationError("Falta colocar el GLN de la compañía.")
        if not self.company_id.partner_id.identif_secundaria_valor_fresko:
            raise ValidationError("Falta colocar el Número de Proveedor en la compañía.")
        if not self.partner_shipping_id.gnl_fresko:
            raise ValidationError("Falta colocar el GLN en la dirección de entrega.")


    def itl_append_addenda_fresko(self):
        self.addenda_fresko_validations()
        attachment_id = self.l10n_mx_edi_retrieve_first_attachment().copy()
        xml_signed = attachment_id.datas
        new_attachment_id = self.env['ir.attachment']
        if xml_signed:
            self.ensure_one()
            addenda = (
                self.partner_id.l10n_mx_edi_addenda or
                self.partner_id.commercial_partner_id.l10n_mx_edi_addenda or 
                self.partner_id.parent_id.l10n_mx_edi_addenda)
            if not addenda:
                return xml_signed
            values = {
                'record': self,
            }
            addenda_node_str = addenda.render(values=values).strip()
            if not addenda_node_str:
                return xml_signed
            tree = fromstring(base64.b64decode(xml_signed))
            addenda_node = fromstring(addenda_node_str)
            if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
                node = etree.Element(etree.QName(
                    'http://www.sat.gob.mx/cfd/3', 'Addenda'))
                node.append(addenda_node)
                addenda_node = node
            tree.append(addenda_node)
            self.message_post(
                body=_('Addenda has been added in the CFDI with success'),
                subtype='account.mt_invoice_validated')
            xml_signed = base64.encodestring(etree.tostring(
                tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
            attachment_id.write({
                'datas': xml_signed,
                'mimetype': 'application/xml'
            })
            
    def itl_get_taxes(self):
        taxes = self._l10n_mx_edi_create_taxes_cfdi_values()['transferred']

        tax_group = ''
        tax_name = lambda t: {'ISR': '001', 'IVA': '002', 'IEPS': '003'}.get(t, False)

        for tax in taxes:
            tax_group = tax_group + tax_name(tax['name']) + '|' + str(tax['rate']) + '|tras|' + tax['type'] + '|' + str(tax['amount']) + ','

        tax_ids = self.get_tax_ids(tax_group)

        return tax_ids

    def get_tax_ids(self, tax_group, version='3.3'):
        #print('get_tax_ids: ',tax_group)
        '''
        obtiene los ids de los impuestos
        a partir de nombres de grupos de impuestos
        estructura:
        000|0.16,001|0.0,
        regresa [(6, None, ids)]
        '''
        tax_ids = []
        AccountTax = self.env['account.tax'].sudo()
        
        if self.type == 'out_invoice' or self.type == 'out_refund':
            type_tax_use = 'sale'
        else:
            type_tax_use = 'purchase'

        #se elimina ultima ,
        tax_group = tax_group[:-1]
        taxes = tax_group.split(',')
        #raise ValidationError(str(taxes))
        for tax in taxes:
            #print('tax: ', tax)
            if tax:
                tax_data = tax.split('|')
                tax_number = tax_data[0]
                tax_type = tax_data[2]

                
                domain = [
                    #('tax_code_mx','=',tax_number),
                    #('amount','=',rate),
                    ('type_tax_use','=',type_tax_use),
                    ('company_id','=',self.company_id.id),
                    #('l10n_mx_cfdi_tax_type','=',tax_factor),
                    ]
                tax_factor = False
                if len(tax_data) == 4: #si es 3.3 tendra 4 elementos
                    tax_factor = tax_data[3]
                    domain.append(('l10n_mx_cfdi_tax_type','=',tax_factor))

                if version == '3.3':
                    #3.3
                    if tax_factor != 'Exento':
                        tax_rate = float(tax_data[1])
                        if tax_type == 'tras':
                            rate = (tax_rate*100)
                        else:
                            rate = -(tax_rate*100)
                        domain.append(('amount','=',rate))

                    domain.append(('tax_code_mx','=',tax_number))
                else:
                    #   3.2
                    if tax_data[1] != 'xxx':
                        tax_rate = float(tax_data[1])
                        if tax_type == 'tras':
                            rate = tax_rate
                        else:
                            rate = -(tax_rate)
                        domain.append(('amount','=',rate))
                    domain.append(('name','ilike',tax_number))
                #print('DOMAIN: ',domain)
                tax_id = AccountTax.search(domain)
                #raise ValidationError(str(domain))
                if tax_id:
                    if tax_number == '001':
                        tax_type = 'LAC'
                    if tax_number == '002':
                        tax_type = 'VAT'
                    if tax_number == '003':
                        tax_type = 'GST'
                    tax_ids.append([tax_id, tax_type, tax_data[4]])
        if tax_ids:
            #print('tax_ids: ',tax_ids)
            return tax_ids
        return False

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    def _get_qty_in_units(self):
        uom_id = self.env['uom.uom'].browse(1)
        qty_units = self.product_uom_id._compute_quantity(self.quantity, uom_id)

        return qty_units