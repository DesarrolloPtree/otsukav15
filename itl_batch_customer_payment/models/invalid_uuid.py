from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json


import logging
_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _name = "itl.invalid.uuid"
    
    
    itl_uuid = fields.Char(string="UUID")
    itl_reason = fields.Char(string="Reason")
    itl_pago_factura_amount = fields.Float(string="Amount in file")
    itl_pago_date = fields.Date(string="Payment date")
    itl_invoice_id = fields.Many2one('account.move', string="Invoice")
    currency_id = fields.Many2one('res.currency', related="itl_invoice_id.currency_id")
    itl_invoice_amount = fields.Monetary(related="itl_invoice_id.amount_residual", string="Amount in invoice")
    
    payment_id = fields.Many2one('account.payment', ondelete="cascade")
    
    
    def confirm_pay_invoice(self):
        _logger.info("====> confirm_pay_invoice")
        if self.itl_invoice_id.invoice_payment_state != 'paid':
            self.check_outstanding_credits(self.itl_invoice_id, json.loads(self.itl_invoice_id.invoice_outstanding_credits_debits_widget))
            if self.itl_invoice_id.amount_residual > 0:
                self.itl_create_payment(self.itl_invoice_id, self.itl_pago_date)
            if self.itl_invoice_id.invoice_payment_state == 'paid':
                self.payment_id.itl_invoices_amount = self.payment_id.itl_invoices_amount + self.itl_pago_factura_amount
                self.unlink()
        else:
            self.itl_reason = "The invoice is already paid before."
    
    
    def check_outstanding_credits(self, invoice_id, credits_json):
        if 'content' in credits_json:
            for record in credits_json['content']:
                journal_name = record['journal_name']
                move_line_names = self.payment_id.move_line_ids.mapped('move_name')
                if journal_name in move_line_names:
                    move_line_id = record['id']
                    invoice_id.js_assign_outstanding_line(move_line_id)
    
    def itl_create_payment(self, invoice, payment_date):
        commission_journal_id = self.env.user.company_id.itl_commission_journal_id
        if not commission_journal_id:
            raise ValidationError("No se econtró el diario de pago de factura.")

        payment_type = 'inbound' if invoice.type in ('out_invoice', 'in_refund') else 'outbound'
        if payment_type == 'inbound':
            payment_method = self.env.ref('account.account_payment_method_manual_in')
        else:
            payment_method = self.env.ref('account.account_payment_method_manual_out')
            
        Payment = self.env['account.payment'].with_context(default_invoice_ids=[(4, invoice.id, False)])
        payment = Payment.create({
            'payment_date': payment_date,
            'payment_method_id': payment_method.id,
            'payment_type': payment_type,
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'amount': invoice.amount_residual,
            'journal_id': commission_journal_id.id,
            'currency_id': invoice.currency_id.id,
        })
        payment.post()
    
    