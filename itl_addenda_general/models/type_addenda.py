# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TypeAddenda(models.Model):
    _name = "type.addenda"
    _description = "Tipos de addenda"

    name = fields.Char(string="Nombre de la Addenda")
    code = fields.Char(string="Código")
