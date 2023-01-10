from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    

    itl_account_refund_origin_id = fields.Many2one('account.account')
    itl_account_refund_id = fields.Many2one('account.account')