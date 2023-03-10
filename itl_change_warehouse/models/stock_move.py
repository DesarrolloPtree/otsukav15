from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import groupby

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"
    
    
    
    def action_back_to_draft(self):
        self._action_cancel()
        if self.filtered(lambda m: m.state != "cancel"):
            raise UserError(_("You can set to draft cancelled moves only"))
        self.write({"state": "draft"})
   