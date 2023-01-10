from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_inv_adj_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send inventory adjusment.")