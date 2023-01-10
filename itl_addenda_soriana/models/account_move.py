from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from lxml.objectify import fromstring
import base64
from lxml import etree
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    
    itl_sale_order_id = fields.Many2one('sale.order', string="Sale Order", compute='_compute_sale_order')
    itl_picking_id = fields.Many2one('stock.picking', string="Delivery", domain="[('sale_id','=',itl_sale_order_id)]")
    itl_picking_addenda_id = fields.Many2one('itl.picking.addenda', string="Addendas disponibles", domain="[('itl_picking_id','=',itl_picking_id)]")
    itl_has_invoice = fields.Boolean(compute="_get_invoice_related")
    
    itl_addenda_soriana = fields.Boolean(compute="_get_addenda_info")
    itl_addenda = fields.Boolean(compute="_get_addenda_info")
    
    # Remision
    itl_proveedor = fields.Char(string="Número de Proveedor", compute="_compute_numero_proveedor")
    itl_remision = fields.Char(string="Remisión", related="itl_picking_addenda_id.itl_remision")
    itl_fecha_remision = fields.Date(string="Fecha de Remisión", related="itl_picking_addenda_id.itl_fecha_remision")
    itl_tienda = fields.Char(string="Tienda", related="itl_picking_addenda_id.itl_tienda")
    itl_tipo_moneda = fields.Selection([('1','Peso'),('2','Dólares'),('3','Euros')], string="Tipo de Moneda", related="itl_picking_addenda_id.itl_tipo_moneda")
    itl_tipo_bulto = fields.Selection([('1','Cajas'),('2','Bolsas')], string="Tipo de Bulto", related="itl_picking_addenda_id.itl_tipo_bulto")
    itl_entrega_mercancia = fields.Char(string="Entrega de Mercancía", help="Indica el número que corresponde a lugar en que se entregará la mercancía, si entrega directamente en la Tienda (sucursal de Centros Comerciales o de City Club) se asigna el valor constante de ‘1’, si se entrega en un CEDIS el valor depende del mismo CEDIS.", default="1", related="itl_picking_addenda_id.itl_entrega_mercancia")
    itl_cantidad_bultos = fields.Integer(string="Cantidad de Bultos", related="itl_picking_addenda_id.itl_cantidad_bultos")
    itl_subtotal = fields.Float(string="Subtotal", related="itl_picking_addenda_id.itl_subtotal")
    itl_descuentos = fields.Float(string="Descuentos", related="itl_picking_addenda_id.itl_descuentos")
    itl_ieps = fields.Float(string="IESP", related="itl_picking_addenda_id.itl_ieps")
    itl_iva = fields.Float(string="IVA", related="itl_picking_addenda_id.itl_iva")
    itl_otros_impuestos = fields.Float(string="Otros Impuestos", related="itl_picking_addenda_id.itl_otros_impuestos")
    itl_total = fields.Float(string="Total", related="itl_picking_addenda_id.itl_total")
    itl_cantidad_pedidos = fields.Integer(string="Cantidad de Pedidos", related="itl_picking_addenda_id.itl_cantidad_pedidos")
    itl_fecha_entrega_mercancia = fields.Datetime(string="Fecha de Entrega Mercancía", related="itl_picking_addenda_id.itl_fecha_entrega_mercancia")
    itl_folio_nota_entrada = fields.Char(string="Folio Nota Entrada", related="itl_picking_addenda_id.itl_folio_nota_entrada")
    
    # Pedidos
    itl_folio_pedido = fields.Char(string="Folio del Pedido", related="itl_picking_addenda_id.itl_folio_pedido")
    itl_cantidad_articulos = fields.Integer(string="Cantidad de Artículos", related="itl_picking_addenda_id.itl_cantidad_articulos")
    
    def get_itl_fecha_entrega_mercancia_datetime(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if not self.itl_fecha_entrega_mercancia:
            return ""
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(self.itl_fecha_entrega_mercancia.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y-%m-%dT%H:%M:%S")
        return display_date_result

    def _get_invoice_related(self):
        for move in self:
            move.itl_has_invoice = False
            if move.itl_picking_addenda_id and move.itl_picking_addenda_id.itl_invoice_related:
                move.itl_has_invoice = True
    
    def _get_addenda_info(self):
        for move in self:
            move.itl_addenda_soriana = False
            move.itl_addenda = False
            if (move.partner_id.itl_num_prov_soriana or move.partner_id.commercial_partner_id.itl_num_prov_soriana):
                move.itl_addenda_soriana = True
            if (move.partner_id.l10n_mx_edi_addenda or move.partner_id.commercial_partner_id.l10n_mx_edi_addenda):
                move.itl_addenda = True
    
    @api.depends('itl_picking_addenda_id')
    def _compute_numero_proveedor(self):
        for rec in self:
            if rec.itl_picking_addenda_id.itl_proveedor:
                rec.itl_proveedor = rec.itl_picking_addenda_id.itl_proveedor
            else:
                if rec.partner_id.parent_id:
                    rec.itl_proveedor = rec.partner_id.parent_id.itl_num_prov_soriana
                else:
                    rec.itl_proveedor = rec.partner_id.itl_num_prov_soriana
    
    @api.depends('invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_order(self):
        for rec in self:
            rec.itl_sale_order_id = False
            if rec.itl_addenda_soriana:
                rec.itl_sale_order_id = rec.mapped('invoice_line_ids.sale_line_ids.order_id')
                if rec.itl_sale_order_id:
                    picking_ids = self.env['stock.picking'].search([('sale_id','=',rec.itl_sale_order_id.id)])
                    if picking_ids:
                        rec.itl_picking_id = picking_ids[0]
                    
    def itl_append_addenda(self):
        self.check_addenda_validations()
        attachment_id = self.l10n_mx_edi_retrieve_first_attachment().copy()
        xml_signed = attachment_id.datas
        new_attachment_id = self.env['ir.attachment']
        if xml_signed:
            self.ensure_one()
            addenda = (
                self.partner_id.l10n_mx_edi_addenda or
                self.partner_id.commercial_partner_id.l10n_mx_edi_addenda or 
                self.partner_id.parent_id.l10n_mx_edi_addenda)
            if not addenda:
                return xml_signed
            values = {
                'record': self,
            }
            addenda_node_str = addenda.render(values=values).strip()
            if not addenda_node_str:
                return xml_signed
            tree = fromstring(base64.b64decode(xml_signed))
            addenda_node = fromstring(addenda_node_str)
            if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
                node = etree.Element(etree.QName(
                    'http://www.sat.gob.mx/cfd/3', 'Addenda'))
                node.append(addenda_node)
                addenda_node = node
            tree.append(addenda_node)
            self.message_post(
                body=_('Addenda has been added in the CFDI with success'),
                subtype='account.mt_invoice_validated')
            xml_signed = base64.encodestring(etree.tostring(
                tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
            attachment_id.write({
                'datas': xml_signed,
                'mimetype': 'application/xml'
            })
            
            self.itl_picking_addenda_id.itl_invoice_related = self
            self.itl_picking_addenda_id.itl_picking_id = self.itl_picking_id
            
    @api.model
    def l10n_mx_edi_retrieve_first_attachment(self):
        attachment_ids = self.l10n_mx_edi_retrieve_attachments()
        return attachment_ids and attachment_ids[-1] or None
            
    def check_addenda_validations(self):
        for line in self.invoice_line_ids:
            if not line.product_id.barcode:
                raise ValidationError("El producto no tiene el barcode configurado.")
                
        if not self.itl_proveedor:
            raise ValidationError("No se encontró el Número de Proveedor asignado por Soriana.")
        if not self.itl_remision:
            raise ValidationError("No se encontró la Remisión.")
        if not self.itl_fecha_remision:
            raise ValidationError("No se encontró la Fecha de Remisión.")
        if not self.itl_tienda:
            raise ValidationError("No se encontró el número de Tienda.")
        if not self.itl_tipo_moneda:
            raise ValidationError("No se encontró el Tipo de Moneda.")
        if not self.itl_tipo_bulto:
            raise ValidationError("No se encontró el Tipo de Bulto.")
        if not self.itl_entrega_mercancia:
            raise ValidationError("No se encontró el número de Entrega de Mercancía.")
        if self.itl_cantidad_bultos == 0:
            raise ValidationError("La Cantidad de Bultos es 0.")
        if self.itl_subtotal == 0:
            raise ValidationError("El Subtotal es 0.")
        if self.itl_total == 0:
            raise ValidationError("El Total es 0.")
        if self.itl_cantidad_pedidos == 0:
            raise ValidationError("La Cantidad de Pedidos es 0.")
        if not self.itl_fecha_entrega_mercancia:
            raise ValidationError("No se encontró la Fecha de Entrega de Mercancía.")
        if not self.itl_folio_nota_entrada:
            raise ValidationError("No se encontró el Folio de Nota de Entrada.")
        if not self.itl_folio_pedido:
            raise ValidationError("No se encontró el Folio del Pedido.")
        if self.itl_cantidad_articulos == 0:
            raise ValidationError("La Cantidad de Artículos es 0.")
            
        if self.itl_total != self.amount_total:
            raise ValidationError("El Total en la addenda es diferente al Total de la factura.")
            
    # Inherited
    #def l10n_mx_edi_append_addenda(self, xml_signed):
    #    if (self.partner_id.l10n_mx_edi_addenda or self.partner_id.commercial_partner_id.l10n_mx_edi_addenda) and (self.partner_id.itl_num_prov_soriana or self.partner_id.commercial_partner_id.itl_num_prov_soriana):
    #        self.check_addenda_validations()
    #    xml_signed = super(AccountMove, self).l10n_mx_edi_append_addenda(xml_signed)
    #    
    #    return xml_signed
    
    # Inherited
    #def l10n_mx_edi_append_addenda(self, xml_signed):
    #    return
        # self.ensure_one()
        # addenda = (
        #     self.partner_id.l10n_mx_edi_addenda or
        #     self.partner_id.commercial_partner_id.l10n_mx_edi_addenda)
        # if not addenda:
        #     return xml_signed
        # values = {
        #     'record': self,
        # }
        # addenda_node_str = addenda.render(values=values).strip()
        # if not addenda_node_str:
        #     return xml_signed
        # tree = fromstring(base64.b64decode(xml_signed))
        # addenda_node = fromstring(addenda_node_str)
        # if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
        #     node = etree.Element(etree.QName(
        #         'http://www.sat.gob.mx/cfd/3', 'Addenda'))
        #     node.append(addenda_node)
        #     addenda_node = node
        # tree.append(addenda_node)
        # self.message_post(
        #     body=_('Addenda has been added in the CFDI with success'),
        #     subtype='account.mt_invoice_validated')
        # xml_signed = base64.encodestring(etree.tostring(
        #     tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        # attachment_id = self.l10n_mx_edi_retrieve_last_attachment().copy()
        # attachment_id.write({
        #     'datas': xml_signed,
        #     'mimetype': 'application/xml'
        # })
        # return xml_signed

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"                    

    def _get_iva(self):
        pctiva = 0
        for impuesto in  self.tax_ids:
            if impuesto.tax_code_mx == '002':
                pctiva = impuesto.amount
                
        return pctiva
                    
    def _get_ieps(self):
        pctieps = 0
        for impuesto in  self.tax_ids:
            if impuesto.tax_code_mx == '003':
                pctieps = impuesto.amount
        
        return pctieps