# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company
        warehouse_ids = company.itl_default_warehouse_id
        return warehouse_ids
    
    picking_policy = fields.Selection([
        ('direct', 'SC will deliver the product'),
        ('one', 'Product pick up')],
        string='Shipping Policy', required=True, readonly=True, default='delivered_by_sc',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
        ,help="If you deliver all products at once, the delivery order will be scheduled based on the greatest "
        "product lead time. Otherwise, it will be based on the shortest.")

    @api.onchange('picking_policy')
    def onchange_picking_policy(self):
        if self.picking_policy == 'pick_up':
            self.warehouse_id = False
        else:
            self.warehouse_id = self._default_warehouse_id()

    @api.onchange("type_id")
    def onchange_type_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        vals = {}
        for order in self:
            vals = {}
            order_type = order.type_id
            if order_type.warehouse_id:
                vals.update({"warehouse_id": order_type.warehouse_id})
            #if order_type.picking_policy:
            #    vals.update({"picking_policy": order_type.picking_policy})
            if order_type.payment_term_id:
                vals.update({"payment_term_id": order_type.payment_term_id})
            if order_type.pricelist_id:
                vals.update({"pricelist_id": order_type.pricelist_id})
            if order_type.incoterm_id:
                vals.update({"incoterm": order_type.incoterm_id})
            if vals:
                order.update(vals)