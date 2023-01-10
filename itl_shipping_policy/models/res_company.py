from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    
    itl_default_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')