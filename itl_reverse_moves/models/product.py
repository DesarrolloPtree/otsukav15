from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    
    # Inherited from account->product
    def get_product_accounts(self, fiscal_pos=None):
        if self.env.context.get('is_refund'):
            accounts = self.with_context(is_refund=True)._get_product_accounts()
            if not fiscal_pos:
                fiscal_pos = self.env['account.fiscal.position']
            return fiscal_pos.map_accounts(accounts)
        else:
            return super(ProductTemplate, self).get_product_accounts(fiscal_pos)
        
    
    def _get_product_accounts(self):
        if self.env.context.get('is_refund'):
            return {
                'income': self.env.company.itl_account_refund_id,
                'expense': self.property_account_expense_id or self.categ_id.property_account_expense_categ_id
            }
        else:
            return super(ProductTemplate, self)._get_product_accounts()
        