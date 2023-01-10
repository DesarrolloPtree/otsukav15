from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    itl_sale_origin_id = fields.Many2one('sale.order', string="Sale Origin")
    itl_delivery_date = fields.Date("Actual Delivery Date", compute='_compute_delivery_date', help="Delivery date set by user of the first delivery order.")
    
    @api.depends('picking_ids.itl_delivery_date')
    def _compute_delivery_date(self):
        for order in self:
            pickings = order.picking_ids.filtered(lambda x: x.state == 'done' and x.location_dest_id.usage == 'customer')
            dates_list = [date for date in pickings.mapped('itl_delivery_date') if date]
            order.itl_delivery_date = fields.Date.context_today(order, min(dates_list)) if dates_list else False
    
    @api.depends('order_line.qty_delivered')
    def _get_delivery_status(self):
        """ compute over all delivery status From line.
        """
        for order in self:
            deliver_quantity = sum(
                order.mapped('order_line').filtered(lambda r: r.product_id.type != 'service').mapped('qty_delivered'))
            order_quantity = sum(
                order.mapped('order_line').filtered(lambda r: r.product_id.type != 'service').mapped('product_uom_qty'))
            if order_quantity > deliver_quantity > 0:
                order.itl_delivery_status = 'partially delivered'
            elif order_quantity <= deliver_quantity > 0:
                order.itl_delivery_status = 'delivered'
            else:
                order.itl_delivery_status = 'not delivered'


    itl_delivery_status = fields.Selection([
        ('not delivered', 'Not Delivered'),
        ('partially delivered', 'Partially Delivered'),
        ('delivered', 'Fully Delivered')
    ], string='Delivery Status', compute="_get_delivery_status", store=True, readonly=True)