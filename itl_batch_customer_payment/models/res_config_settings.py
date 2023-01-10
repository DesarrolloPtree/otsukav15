from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    
    itl_commission_journal_id = fields.Many2one('account.journal', string="Commission journal")