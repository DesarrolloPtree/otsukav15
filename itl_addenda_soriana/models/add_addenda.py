from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class AddAddenda(models.TransientModel):
    _name = "itl.add.addenda"
    
    
    itl_addenda = fields.Many2one('ir.ui.view',
        string='Addenda',
        help='A view representing the addenda',
        domain=[('l10n_mx_edi_addenda_flag', '=', True)], required=True)
    itl_file = fields.Binary(string="Factura Original", required=True)
    itl_file_name = fields.Char(string="Nombre del archivo")
    
    itl_partner_id = fields.Many2one("res.partner", string="Cliente", required=True)
    itl_invoice_id = fields.Many2one("account.move", string="Invoice", required=True)
    
    # Remision
    itl_proveedor = fields.Char(string="Número de Proveedor", related="itl_invoice_id.itl_proveedor")
    itl_remision = fields.Char(string="Remisión", related="itl_invoice_id.itl_remision")
    itl_fecha_remision = fields.Date(string="Fecha de Remisión", related="itl_invoice_id.itl_fecha_remision")
    itl_tienda = fields.Char(string="Tienda", related="itl_invoice_id.itl_tienda")
    itl_tipo_moneda = fields.Selection([('1','Peso'),('2','Dólares'),('3','Euros')], string="Tipo de Moneda", related="itl_invoice_id.itl_tipo_moneda")
    itl_tipo_bulto = fields.Selection([('1','Cajas'),('2','Bolsas')], string="Tipo de Bulto", related="itl_invoice_id.itl_tipo_bulto")
    itl_entrega_mercancia = fields.Char(string="Entrega de Mercancía", help="Indica el número que corresponde a lugar en que se entregará la mercancía, si entrega directamente en la Tienda (sucursal de Centros Comerciales o de City Club) se asigna el valor constante de ‘1’, si se entrega en un CEDIS el valor depende del mismo CEDIS.", default="1", related="itl_invoice_id.itl_entrega_mercancia")
    itl_cantidad_bultos = fields.Integer(string="Cantidad de Bultos", related="itl_invoice_id.itl_cantidad_bultos")
    itl_subtotal = fields.Float(string="Subtotal", related="itl_invoice_id.itl_subtotal")
    itl_descuentos = fields.Float(string="Descuentos", related="itl_invoice_id.itl_descuentos")
    itl_ieps = fields.Float(string="IESP", related="itl_invoice_id.itl_ieps")
    itl_iva = fields.Float(string="IVA", related="itl_invoice_id.itl_iva")
    itl_otros_impuestos = fields.Float(string="Otros Impuestos", related="itl_invoice_id.itl_otros_impuestos")
    itl_total = fields.Float(string="Total", related="itl_invoice_id.itl_total")
    itl_cantidad_pedidos = fields.Integer(string="Cantidad de Pedidos", related="itl_invoice_id.itl_cantidad_pedidos")
    itl_fecha_entrega_mercancia = fields.Date(string="Fecha de Entrega Mercancía", related="itl_invoice_id.itl_fecha_entrega_mercancia")
    itl_folio_nota_entrada = fields.Char(string="Folio Nota Entrada", related="itl_invoice_id.itl_folio_nota_entrada")
    
    # Pedidos
    itl_folio_pedido = fields.Char(string="Folio del Pedido", related="itl_invoice_id.itl_folio_pedido")
    itl_cantidad_articulos = fields.Integer(string="Cantidad de Artículos", related="itl_invoice_id.itl_cantidad_articulos")
    
    def itl_generar_addenda(self):
        self.check_addenda_validations()
        self.itl_append_addenda()
    
    def itl_append_addenda(self):
        addenda = (self.itl_addenda)
        attachment_id = self.itl_invoice_id.l10n_mx_edi_retrieve_last_attachment()
        if not attachment_id:
            raise UserError("La factura no contiene el XML.")
        xml_signed = attachment_id.datas
        _logger.info("====> addenda: " + str(addenda))
        if not addenda:
            return
        values = {
            'record': self,
        }
        addenda_node_str = addenda.render(values=values).strip()
        _logger.info("====> addenda_node_str: " + str(addenda_node_str))
        if not addenda_node_str:
            return
        tree = fromstring(base64.b64decode(xml_signed))
        addenda_node = fromstring(addenda_node_str)
        if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
            node = etree.Element(etree.QName(
                'http://www.sat.gob.mx/cfd/3', 'Addenda'))
            node.append(addenda_node)
            addenda_node = node
        tree.append(addenda_node)
        self.itl_invoice_id.message_post(
            body=_('Addenda has been added in the CFDI with success'),
            subtype='account.mt_invoice_validated')
        xml_signed = base64.encodestring(etree.tostring(
            tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        attachment_id = self.itl_invoice_id.l10n_mx_edi_retrieve_last_attachment().copy()
        attachment_id.write({
            'datas': xml_signed,
            'mimetype': 'application/xml'
        })
    
    @api.onchange('itl_partner_id')
    def _get_num_prov(self):
        if self.itl_partner_id:
            self.itl_proveedor = False
            if self.itl_partner_id.parent_id:
                self.itl_proveedor = self.itl_partner_id.parent_id.itl_num_prov_soriana
            else:
                self.itl_proveedor = self.itl_partner_id.itl_num_prov_soriana
                
    def check_addenda_validations(self):
        for line in self.itl_invoice_id.invoice_line_ids:
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
            
        if self.itl_total != self.itl_invoice_id.amount_total:
            raise ValidationError("El Total en la addenda es diferente al Total de la factura.")