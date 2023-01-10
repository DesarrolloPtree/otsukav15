from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_account_refund_origin_id = fields.Many2one('account.account', related="company_id.itl_account_refund_origin_id", readonly=False)
    itl_account_refund_id = fields.Many2one('account.account', related="company_id.itl_account_refund_id", readonly=False)