from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    itl_inv_adj_approval_category_id = fields.Many2one(related="company_id.itl_inv_adj_approval_category_id", string="Approval category", help="Approval category to create when send inventory adjusment.", readonly=False)