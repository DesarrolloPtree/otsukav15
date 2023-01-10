from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import datetime

import logging
_logger = logging.getLogger(__name__)

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class account_payment(models.Model):
    _inherit = "account.payment"
    
    
    itl_is_batch_payment = fields.Boolean(string="Is batch payment", copy=False)
    itl_batch_file = fields.Binary(string="Seleccionar archivo", copy=False)
    itl_batch_file_name = fields.Char(string="Nombre del archivo", copy=False)
    
    itl_invalid_uuid_ids = fields.One2many('itl.invalid.uuid', 'payment_id', string="UUIDs", copy=False)
    
    itl_invoices_amount = fields.Monetary(string="Amount paid from file")
    
    
    def itl_process_file(self):
        if self.state != 'posted':
            raise ValidationError("You can only process a file on CONFIRMED payments.")
        txt_data = self.get_txt_data()
        lines = txt_data.split('\n')
        i = 1
        num_lines = len(lines)
        total_amount = 0
        uuid = ' '
        invoices = self.env['account.move'].search([('type','=','out_invoice'),('state','=','posted')])
        invalid_invoices = []
        exception_invoice = []
        for line in lines:
            if 'COMPRAS' in line:
                line_splited = line.split(' ')
                line_splited = ' '.join(line_splited).split()
                amount = float(line_splited[-2])
                uuid = line_splited[-1]
                        
            if 'PAGO FACTURA' in line:
                line_splited = line.split(' ')
                line_splited = ' '.join(line_splited).split()
                pago_factura_amount = float(line_splited[-1])
                pago_date = line_splited[-2]
                date_time_obj = datetime.datetime.strptime(pago_date, '%d/%m/%Y')
                invalid_invoice = False
                invoice_id = invoices.filtered(lambda i: str(i.l10n_mx_edi_cfdi_uuid).upper() == str(uuid).upper())
                reason = ''
                vals = {}
                
                if invoice_id and invoice_id.invoice_payment_state == 'paid':
                    continue
                
                if invoice_id:
                    if pago_factura_amount == invoice_id.amount_residual:
                        if invoice_id.invoice_outstanding_credits_debits_widget:
                            self.check_outstanding_credits(invoice_id, json.loads(invoice_id.invoice_outstanding_credits_debits_widget))
                            total_amount += pago_factura_amount
                            
                    else:
                        invalid_invoice = True
                        reason = "The amout in file is different that the invoice amount to pay."
                        vals['itl_invoice_id'] = invoice_id.id
                        vals['itl_pago_factura_amount'] = pago_factura_amount
                else:
                    invalid_invoice = True
                    reason = "Invoice doesn't found."
                    
                if invoice_id and invoice_id.partner_id != self.partner_id:
                    invalid_invoice = True
                    reason = "The customer of the payment doesn't match with the customer of the invoice."
                    vals['itl_invoice_id'] = invoice_id.id
                    
                if invalid_invoice:
                    vals['itl_uuid'] = uuid
                    vals['itl_reason'] = reason
                    vals['itl_pago_date'] = date_time_obj
                    invalid_invoices.append((0, 0, vals))
                    
                uuid = ' '
                
            if 'COMISN BANCARIA' in line:
                line_splited = line.split(' ')
                line_splited = ' '.join(line_splited).split()
                comision_amount = float(line_splited[-1])
            
            if 'Total proveedor' in line:
                line_splited = line.split(' ')
                total_in_batch = float(line_splited[-1])
            i += 1
        if len(invalid_invoices) > 0:
            self.itl_invalid_uuid_ids = invalid_invoices
                
        self.itl_invoices_amount = total_amount
    
    def check_outstanding_credits(self, invoice_id, credits_json):
        for record in credits_json['content']:
            journal_name = record['journal_name']
            move_line_names = self.move_line_ids.mapped('move_name')
            if journal_name in move_line_names:
                move_line_id = record['id']
                invoice_id.js_assign_outstanding_line(move_line_id)
    
    def get_txt_data(self):
        txt_data = base64.b64decode(self.itl_batch_file)
        txt_data = txt_data.decode('latin-1')
        return txt_data
    
    # Inherit
    def action_draft(self):
        result = super(account_payment, self).action_draft()
        for record in self:
            if record.itl_is_batch_payment:
                record.itl_invalid_uuid_ids.unlink()
                record.itl_invoices_amount = 0
        
        return result
    
    # Inherit
    def post(self):
        result = super(account_payment, self).post()
        for rec in self:
            if rec.itl_is_batch_payment and rec.itl_batch_file:
                #try:
                rec.itl_process_file()
                #except Exception:
                #    raise ValidationError("An error occurred while processing the file.")