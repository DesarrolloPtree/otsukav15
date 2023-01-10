from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_repr
from odoo.exceptions import ValidationError
from collections import defaultdict


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    
    # Inherit from stock_account
    def _get_product_accounts(self):
        """ Add the stock accounts related to product to the result of super()
        @return: dictionary which contains information regarding stock accounts and super (income+expense accounts)
        """
        accounts = super(ProductTemplate, self)._get_product_accounts()
        res = self._get_asset_accounts()
        accounts.update({
            'stock_input': res['stock_input'] or self.categ_id.property_stock_account_input_categ_id,
            'stock_output': res['stock_output'] or self.categ_id.property_stock_account_output_categ_id,
            'stock_valuation': self.categ_id.property_stock_valuation_account_id or False,
            'itl_stock_adjusment': self.categ_id.itl_property_account_inv_adj_categ_id or False
        })
        return accounts
    
class ProductCategory(models.Model):
    _inherit = "product.category"
    
    
    itl_property_account_inv_adj_categ_id = fields.Many2one('account.account', company_dependent=True,
        string="Inventory Adjusment Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account is used when a inventory adjsument is validated.")