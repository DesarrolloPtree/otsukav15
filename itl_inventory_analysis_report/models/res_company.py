from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_sale_account = fields.Many2one('account.account', help="Sale account")
    itl_vat_account = fields.Many2one('account.account', help="VAT account")
    itl_ar_account = fields.Many2one('account.account', help="AR account")
    itl_intransit_account = fields.Many2one('account.account', help="Inv. in Transit account")
    itl_cogs_account = fields.Many2one('account.account', help="COGS account")