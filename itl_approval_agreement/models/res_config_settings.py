from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_agreement_approval_category_id = fields.Many2one(related="company_id.itl_agreement_approval_category_id", string="Approval category", help="Approval category to create when send agreement.", readonly=False)
    itl_agreement_tmp_approval_category_id = fields.Many2one(related="company_id.itl_agreement_tmp_approval_category_id", string="Approval category", help="Approval category to create when send agreement template.", readonly=False)