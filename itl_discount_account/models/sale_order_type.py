from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _inherit = "sale.order.type"
    
    itl_discount_account = fields.Many2one('account.account', string="Discount Account")
    itl_is_discount_type = fields.Boolean(string="Is Discount")
    