from collections import Counter

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import OrderedSet
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    itl_product_available_to_return = fields.Float('Product available to return', default=0.0, digits='Product Unit of Measure', copy=False)
    
    #@api.onchange('qty_done')
    #def _onchange_qty_done(self):
    #    res = super(StockMoveLine, self)._onchange_qty_done()
    #    
    #    quantity = self.move_id.product_qty
    #    
    #    if self.picking_id.picking_type_code in ['incoming'] and self.picking_id.itl_is_return and self.qty_done > self.itl_product_available_to_return:
    #        raise ValidationError("You can't return more products that the available to return.")
    #    
    #    return res