from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    # Inherit
    def js_assign_outstanding_line(self, line_id):
        self.ensure_one()
        result = super(AccountMove, self).js_assign_outstanding_line(line_id)
        
        exception_id = self.env['itl.invalid.uuid'].search([('itl_invoice_id','=',self.id)], limit=1)
        
        if exception_id:
            exception_id.payment_id.itl_invoices_amount += exception_id.itl_pago_factura_amount
            exception_id.unlink()
        
        return result
    
    