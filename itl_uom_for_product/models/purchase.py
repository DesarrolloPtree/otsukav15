from odoo import fields, osv, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

import datetime
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    
    itl_uom_ids = fields.Many2many('uom.uom', related="product_id.itl_uom_ids", string="UoM available for this product")
    
    
    @api.onchange('product_id')
    def _itl_onchange_product_id(self):
        for rec in self:
            if rec.itl_uom_ids:
                return {
                    'domain': {
                        'product_uom': [('id','in',rec.itl_uom_ids.ids)]
                    }
                }
            else:
                return {
                    'domain': {
                        'product_uom': []
                    }
                }