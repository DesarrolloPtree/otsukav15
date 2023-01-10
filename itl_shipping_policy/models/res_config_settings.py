from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    itl_default_warehouse_id = fields.Many2one('stock.warehouse', related="company_id.itl_default_warehouse_id", string='Warehouse', readonly=False)