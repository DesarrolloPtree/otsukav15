from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    stock_inventory_id = fields.Many2one('stock.inventory', string="Stock Inventory")
    
    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self).action_approve()
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        
        if len(approvals) == len(self.mapped('approver_ids')) or len(approvals) == 0:
            if self.stock_inventory_id:
                self.stock_inventory_id.sudo().state = 'confirm'
                self.stock_inventory_id.sudo().with_context(itl_from_inventory_adj=True).action_validate()
    
    # Inherit method
    #def action_withdraw(self, approver=None):
    #    super(ApprovalRequestCustom,self).action_withdraw()
    #    if self.sale_id:
    #        self.sale_id.state = 'to_approve'
            
    #Inherit method
    def action_cancel(self):
        if self.stock_inventory_id:
            self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
            self.mapped('approver_ids').write({'status': 'cancel'})
            self.stock_inventory_id.action_cancel_draft()
            self.send_email_notification_done()
        super(ApprovalRequestCustom, self).action_cancel()
        
        
    def show_inventory_adjusment_report(self):
        if self.stock_inventory_id:
            return self.stock_inventory_id.open_inventory_report()