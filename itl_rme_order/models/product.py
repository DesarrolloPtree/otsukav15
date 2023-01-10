from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)
        
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    # Full inherited from stock_account > product.py
    def _prepare_out_svl_vals(self, quantity, company):
        """Prepare the values for a stock valuation layer created by a delivery.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        self.ensure_one()
        if self.env.context.get('is_rme', False):
            # Quantity is negative for out valuation layers.
            quantity = -1 * quantity
            vals = {
                'product_id' : self.id,
                'value': quantity * self.standard_price,
                'unit_cost': self.standard_price,
                'quantity': quantity,
            }
            if self.cost_method in ('average', 'fifo'):
                fifo_vals = self._run_fifo(abs(quantity), company)
                vals['remaining_qty'] = fifo_vals.get('remaining_qty')
                # In case of AVCO, fix rounding issue of standard price when needed.
                if self.cost_method == 'average':
                    currency = self.env.company.currency_id
                    rounding_error = currency.round(self.standard_price * self.quantity_svl - self.value_svl)
                    #### Adding condition to avoid rounding adjustment when is RME process
                    if rounding_error and not self.env.context.get('is_rme', False):
                        # If it is bigger than the (smallest number of the currency * quantity) / 2,
                        # then it isn't a rounding error but a stock valuation error, we shouldn't fix it under the hood ...
                        if abs(rounding_error) <= (abs(quantity) * currency.rounding) / 2:
                            vals['value'] += rounding_error
                            vals['rounding_adjustment'] = '\nRounding Adjustment: %s%s %s' % (
                                '+' if rounding_error > 0 else '',
                                float_repr(rounding_error, precision_digits=currency.decimal_places),
                                currency.symbol
                            )
                if self.cost_method == 'fifo':
                    vals.update(fifo_vals)
        else:
            vals = super(ProductProduct, self)._prepare_out_svl_vals(quantity, company)
        
        return vals