from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    itl_agreement_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send agreement.", readonly=False)
    itl_agreement_tmp_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send agreement template.", readonly=False)