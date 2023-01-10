from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class StockInventory(models.Model):
    _inherit = 'stock.inventory'
    
    
    approval_request_id = fields.Many2one('approval.request', string="Approval request", readonly=True, store=True, copy=False)
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], related="approval_request_id.request_status")
    state = fields.Selection(selection_add=[('refused','Rejected'),('to_approve','To approve'),('approved', 'Approved')])
    
    
    def send_to_approve(self):
        if not self.can_validate:
            raise ValidationError(
                'Some inventory lines need to be filled, you could bypass this turning on the bypass button.')
        if not self.env.company.itl_inv_adj_approval_category_id:
            raise ValidationError("Approval category is not configured.")

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Inventory Adjusment - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_inv_adj_approval_category_id.id,
            'stock_inventory_id': self.id
        }
        
        self.state = 'to_approve'
        if not self.approval_request_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.approval_request_id
            for p in rec.product_line_ids:
                p.unlink()
            rec.write(vals)
            rec.action_draft()
            rec.action_confirm()

        self.approval_request_id = rec.id
