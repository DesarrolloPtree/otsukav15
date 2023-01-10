
from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    
    itl_encargado = fields.Many2one('res.partner', string='Encargado de almacén', required=False)