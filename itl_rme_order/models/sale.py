from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    itl_is_rme = fields.Boolean(related="type_id.itl_is_rme")
    itl_warehouse_return_id = fields.Many2one('stock.warehouse', string="Return Warehouse")
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    itl_is_rme = fields.Boolean(related="order_id.itl_is_rme")
    
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if self.itl_is_rme:
            return
            
        super(SaleOrderLine, self).product_uom_change()