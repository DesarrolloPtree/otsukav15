from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, OrderedSet

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    # Inherit from stock_account
    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        result = super(StockMove, self)._get_accounting_data_for_valuation()
        result = list(result)
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()
        
        if self._context.get('itl_from_inventory_adj', False):
            if not accounts_data.get('itl_stock_adjusment', False):
                raise UserError(_('Cannot find a inventory adjusment account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
                
            acc_src = accounts_data['itl_stock_adjusment'].id
            acc_dest = accounts_data['itl_stock_adjusment'].id
            result[1] = acc_src
            result[2] = acc_dest

        result = tuple(result)
        return result