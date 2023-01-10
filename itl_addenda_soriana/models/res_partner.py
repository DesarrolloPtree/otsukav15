# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    
    itl_num_prov_soriana = fields.Char(string="Número de Proveedor asignado por Soriana al Socio Comercial", copy=False)