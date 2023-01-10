# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    
    itl_uom_ids = fields.Many2many('uom.uom', string="UoM available for this product", copy=False)