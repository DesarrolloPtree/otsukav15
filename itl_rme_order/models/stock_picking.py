from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"
    
    
    itl_is_rme = fields.Boolean(related="sale_id.itl_is_rme")
    itl_exchange_receipt_id = fields.Many2one('stock.picking', string="Exchange receipt") 
    
    # Inherit
    def button_validate(self):
        self = self.sudo()
        
        rec = super(Picking, self).button_validate()
        sale_id = self.sale_id
        if not self.sale_id:
            sale_id = self.env['sale.order'].search([('name','=',self.origin)], limit=1)
        #if not sale_id:
        #    raise ValidationError("No se encontró la orden de venta relacionada.")
        if self.picking_type_code in ['outgoing'] and sale_id.itl_is_rme:
            _logger.info("===##> RME outgoing")
            picking_type_id = self.env['stock.picking.type'].search([('warehouse_id','=',sale_id.itl_warehouse_return_id.id),('code','=','incoming')])
            
            defaults = {'location_dest_id': sale_id.itl_warehouse_return_id.lot_stock_id.id,
                       'picking_type_id': picking_type_id.id}
            vals = {
                'partner_id': self.partner_id.id,
                'picking_type_id': picking_type_id.id,
                'location_dest_id': sale_id.itl_warehouse_return_id.lot_stock_id.id,
                'immediate_transfer': True,
                'origin': self.origin,
                'sale_id': sale_id.id,
                'group_id': self.group_id.id
            }
            lines = []
            origin_picking = sale_id.itl_sale_origin_id.picking_ids.filtered(lambda i: i.picking_type_code == 'outgoing')
            lot_id = False
            if origin_picking and origin_picking[0].move_line_ids_without_package:
                lot_id = origin_picking[0].move_line_ids_without_package[0].lot_id.id
            customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
            for line in self.move_line_ids_without_package:
                val_line = {
                    'product_id': line.product_id.id,
                    'location_id': customerloc.id,
                    'location_dest_id': sale_id.itl_warehouse_return_id.lot_stock_id.id,
                    'qty_done': line.qty_done,
                    'product_uom_id': line.product_uom_id.id,
                    'lot_id': lot_id
                }
                lines.append((0, 0, val_line))
            
            vals.update(move_line_ids_without_package=lines)
            
            new_recepit = self.env['stock.picking'].create(vals)
            new_recepit.location_id = customerloc
            new_recepit.state = 'assigned'
            
            sale_id.picking_ids = [(4, new_recepit.id)]
            self.itl_exchange_receipt_id = new_recepit
            
        return rec
        
    def send_receiving_return_rme_email(self):
        #self.email_validations()
        receiving_template_id = self.env.ref('itl_rme_order.email_template_receiving_return_rme_picking', False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        email_values = {'base_url': base_url}
        if receiving_template_id:
            self.env['mail.template'].browse(receiving_template_id.id).with_context(email_values).send_mail(self.id, force_send=True)