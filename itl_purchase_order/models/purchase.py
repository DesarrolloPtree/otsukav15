# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
    def button_cancel(self):
        result = super(PurchaseOrder, self).button_cancel()
        
        for order in self:
            order.partner_ref = False
            
        return result
