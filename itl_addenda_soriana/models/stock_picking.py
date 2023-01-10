from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    itl_picking_addenda_ids = fields.One2many('itl.picking.addenda', 'itl_picking_id')