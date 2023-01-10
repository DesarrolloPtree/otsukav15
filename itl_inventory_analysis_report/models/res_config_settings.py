from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_sale_account = fields.Many2one('account.account', related="company_id.itl_sale_account", help="Sale account", readonly=False)
    itl_vat_account = fields.Many2one('account.account', related="company_id.itl_vat_account", help="VAT account", readonly=False)
    itl_ar_account = fields.Many2one('account.account', related="company_id.itl_ar_account", help="AR account", readonly=False)
    itl_intransit_account = fields.Many2one('account.account', related="company_id.itl_intransit_account", help="Inv. in Transit account", readonly=False)
    itl_cogs_account = fields.Many2one('account.account', related="company_id.itl_cogs_account", help="COGS account", readonly=False)