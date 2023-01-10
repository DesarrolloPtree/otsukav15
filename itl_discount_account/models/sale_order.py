# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    itl_is_discount_type = fields.Boolean(related="type_id.itl_is_discount_type")
    
    @api.onchange("type_id")
    def _onchnage_type_id(self):
        if self.state in ['draft']:
            for line in self.order_line:
                line.itl_qty_uom_discount = 0

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    itl_discount_amount = fields.Float(string="Disc. $")
    itl_qty_uom_discount = fields.Integer(string="Caja/Unidad Disc.")
    itl_is_discount_type = fields.Boolean(related="order_id.type_id.itl_is_discount_type")

    # Inherit from sale
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'itl_qty_uom_discount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            
            ####### Custom code, compute the % discount based on unit discount qty
            if line.itl_is_discount_type and line.itl_qty_uom_discount >= 0:
                # Obtiene el monto $ de multiplicar itl_qty_uom_discount x line.price_unit
                line.itl_discount_amount = line.itl_qty_uom_discount * line.price_unit
                # Obtiene el precio final descontando el precio de las unidades de descuento
                subtotal = line.product_uom_qty * line.price_unit
                new_discount = 0
                if line.itl_discount_amount > 0:
                    new_discount = (line.itl_discount_amount * 100) / subtotal
                line.discount = new_discount
                #price = price * (1 - (new_discount or 0.0) / 100.0)
            #######
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
                
    # Inherit from sale    
    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        # Add itl_qty_uom_discount field to invoice line
        if self.itl_qty_uom_discount > 0:
            res['itl_qty_uom_discount'] = self.itl_qty_uom_discount
        return res