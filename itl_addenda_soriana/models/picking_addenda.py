from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class PickingAddenda(models.Model):
    _name = "itl.picking.addenda"
    _description = "Picking Addenda"
    #_rec_name = "itl_folio_nota_entrada"
    
    itl_picking_id = fields.Many2one("stock.picking")
    itl_invoice_related = fields.Many2one("account.move", string="Invoice related", readonly=True)
    
    # Remision
    itl_proveedor = fields.Char(string="Número de Proveedor", compute="_get_num_prov")
    itl_remision = fields.Char(string="Remisión")
    itl_fecha_remision = fields.Date(string="Fecha de Remisión")
    itl_tienda = fields.Char(string="Tienda")
    itl_tipo_moneda = fields.Selection([('1','Peso'),('2','Dólares'),('3','Euros')], string="Tipo de Moneda")
    itl_tipo_bulto = fields.Selection([('1','Cajas'),('2','Bolsas')], string="Tipo de Bulto")
    itl_entrega_mercancia = fields.Char(string="Entrega de Mercancía", help="Indica el número que corresponde a lugar en que se entregará la mercancía, si entrega directamente en la Tienda (sucursal de Centros Comerciales o de City Club) se asigna el valor constante de ‘1’, si se entrega en un CEDIS el valor depende del mismo CEDIS.", default="1")
    itl_cantidad_bultos = fields.Integer(string="Cantidad de Bultos")
    itl_subtotal = fields.Float(string="Subtotal")
    itl_descuentos = fields.Float(string="Descuentos")
    itl_ieps = fields.Float(string="IESP")
    itl_iva = fields.Float(string="IVA")
    itl_otros_impuestos = fields.Float(string="Otros Impuestos")
    itl_total = fields.Float(string="Total")
    itl_cantidad_pedidos = fields.Integer(string="Cantidad de Pedidos")
    itl_fecha_entrega_mercancia = fields.Datetime(string="Fecha de Entrega Mercancía")
    itl_folio_nota_entrada = fields.Char(string="Folio Nota Entrada")
    
    # Pedidos
    itl_folio_pedido = fields.Char(string="Folio del Pedido")
    itl_cantidad_articulos = fields.Integer(string="Cantidad de Artículos")
    
    
    def _get_num_prov(self):
        for rec in self:
            rec.itl_proveedor = False
            if rec.itl_picking_id.partner_id.parent_id:
                rec.itl_proveedor = rec.itl_picking_id.partner_id.parent_id.itl_num_prov_soriana
            else:
                rec.itl_proveedor = rec.itl_picking_id.partner_id.itl_num_prov_soriana
                
    @api.depends('itl_remision', 'itl_folio_nota_entrada')
    def name_get(self):
        result = []
        for move in self:
            name = '%s, %s' % (self.itl_remision, self.itl_folio_nota_entrada)
            result.append((move.id, name))
        return result