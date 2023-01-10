from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_commission_journal_id = fields.Many2one(related="company_id.itl_commission_journal_id", string="Commission journal", readonly=False)