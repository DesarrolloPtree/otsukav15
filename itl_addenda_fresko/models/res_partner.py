# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    
    gnl_fresko = fields.Char(string="GNL Fresko", help="Se indica el número global de localización (GLN), puede ser del vendedor, comprador, dirección de entrega, dirección de facturación.", copy=False)
    contacto_compras_fresko = fields.Char(string="Nombre de la persona del departamento de compras Fresko", copy=False)
    identif_secundaria_tipo_fresko = fields.Selection([('SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY','Número interno del proveedor'),
                                                        ('IEPS_REFERENCE','Referencia signada')], string="Tipo de identificación secundaria", copy=False)
    identif_secundaria_valor_fresko = fields.Char(string="Número de identificación secundaria", copy=False)
    addenda_code = fields.Char(related="type_addenda.code")