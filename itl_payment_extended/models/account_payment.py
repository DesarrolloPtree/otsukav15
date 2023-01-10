from odoo import _, api, fields, models

from odoo.addons.l10n_mx_edi.models import account_invoice

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'l10n_mx_edi.pac.sw.mixin']
    
    # Full inherited
    def l10n_mx_edi_is_required(self):
        self.ensure_one()
        required = (
            self.payment_type == 'inbound' and
            self.company_id.country_id == self.env.ref('base.mx') and
            not self.invoice_ids.filtered(lambda i: i.type != 'out_invoice'))
        if not required:
            return required
        if self.l10n_mx_edi_pac_status != 'none':
            return True
        if self.invoice_ids and False in self.invoice_ids.mapped('l10n_mx_edi_cfdi_uuid'):
            # raise UserError(_(
                # 'Some of the invoices that will be paid with this record '
                # 'are not signed, and the UUID is required to indicate '
                # 'the invoices that are paid with this CFDI'))
            return False
        messages = []
        if not self.invoice_ids:
            messages.append(_(
                '<b>This payment <b>has not</b> invoices related.'
                '</b><br/><br/>'
                'Which actions can you take?\n'
                '<ul>'
                '<ol>If this is an payment advance, you need to create a new '
                'invoice with a product that will represent the payment in '
                'advance and reconcile such invoice with this payment. For '
                'more information please read '
                '<a href="http://omawww.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Caso_uso_Anticipo.pdf">'
                'this SAT reference.</a></ol>'
                '<ol>If you already have the invoices that are paid make the '
                'payment matching of them.</ol>'
                '</ul>'
                '<p>If you follow this steps once you finish them and the '
                'paid amount is bellow the sum of invoices the payment '
                'will be automatically signed'
                '</p>'))
        categ_force = self._l10n_mx_edi_get_force_rep_category()
        force = self._context.get('force_ref') or (
            categ_force and categ_force in self.partner_id.category_id)
        if self.invoice_ids and not self.invoice_ids.filtered(
                lambda i: i.l10n_mx_edi_get_payment_method_cfdi() == 'PPD') and not force:
            messages.append(_(
                '<b>The invoices related with this payment have the payment '
                'method as <b>PUE</b>.'
                '</b><br/><br/>'
                'When an invoice has the payment method <b>PUE</b> do not '
                'requires generate a payment complement. For more information '
                'please read '
                '<a href="http://omawww.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Guia_comple_pagos.pdf">'
                'this SAT reference.</a>, Pag. 3. Or read the '
                '<a href="https://www.odoo.com/documentation/user/11.0/es/accounting/localizations/mexico.html#payments-just-available-for-cfdi-3-3">'
                'Odoo documentation</a> to know how to indicate the payment '
                'method in the invoice CFDI.'
                ))
        if messages:
            self.message_post(body=account_invoice.create_list_html(messages))
            return force or False
        return required