from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    type_addenda = fields.Many2one('type.addenda', string="Tipo de Addenda")