from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    itl_finished_sale = fields.Boolean(string="Finished Sale", default=False)
    itl_can_cancel = fields.Boolean(string="Can be cancelled", compute="_compute_can_be_cancelled")
    
    def _compute_can_be_cancelled(self):
        for sale in self:
            sale.itl_can_cancel = False
            #if sale.state in ['sale']:
            qty_invoiced = sum(sale.order_line.mapped('qty_invoiced'))
            if qty_invoiced <= 0:
                sale.itl_can_cancel = True
            
    def action_cancel(self):
        if not self.itl_can_cancel:
            raise ValidationError("No puede cancelar una orden de venta que tiene una o más facturas posteadas, cancele primero las facturas o haga una nota de crédito y después cancele la orden de venta.")
        
        return super(SaleOrder, self).action_cancel()
    
    # Inherited
    def action_done(self):
        for line in self.order_line:
            line.product_uom_qty = line.qty_invoiced
        
        return super(SaleOrder, self).action_done()
    
    
    def finish_sale(self):
        for line in self.order_line:
            line.product_uom_qty = line.qty_invoiced
        return self.write({'itl_finished_sale': True})