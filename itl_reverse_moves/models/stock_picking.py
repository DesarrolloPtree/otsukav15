
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
    
    itl_invoice_origin = fields.Many2one('account.move', string="Invoice Origin for Return")
    itl_available_invoices = fields.Many2many('account.move', compute="_get_invoices")
    itl_refund_type = fields.Selection(selection=[
            ('refund', 'Partial Refund'),
            ('cancel', 'Full Refund')
        ], string='Refund type')
    
    
    def _get_invoices(self):
        for record in self:
            record.itl_available_invoices = False
            if record.itl_is_return:
                sale_id = False
                if record.sale_id:
                    sale_id = record.sale_id
                elif record.itl_origin_sale:
                    sale_id = self.env['sale.order'].search([('name','=',record.itl_origin_sale)], limit=1)
                else:
                    sale_id = False
                
                if sale_id:
                    record.itl_available_invoices = sale_id.invoice_ids.filtered(lambda i: i.type in ['out_invoice','in_invoice'] and i.state == 'posted')
                    
    # Inherit
    def button_validate(self):
        self = self.sudo()
        
        rec = super(Picking, self).button_validate()
        sale_id = self.sale_id
        if not self.sale_id:
            sale_id = self.env['sale.order'].search([('name','=',self.origin)], limit=1)
        #if not sale_id:
        #    raise ValidationError("No se encontró la orden de venta relacionada.")
        if sale_id.invoice_ids and self.itl_is_return and self.picking_type_code in ['incoming']:
            _logger.info("==>>>> Return")
            if not self.itl_invoice_origin:
                raise ValidationError("You need to select an origin invoice to make the appropiate credit note.")
            if not self.itl_refund_type:
                raise ValidationError("You need to select a refund type.")
            
            vals = {'move_id': self.itl_invoice_origin.id,
                   'refund_method': self.itl_refund_type}
            amr = self.env['account.move.reversal'].with_context(active_ids=self.itl_invoice_origin.id, active_model='account.move').create(vals)
            amr._compute_from_moves()
            product_returns = self.compute_products_to_return()
            rev_invoice_id = amr.itl_reverse_moves(product_returns)
            if rev_invoice_id.state == 'draft':
                rev_invoice_id.post()
            msg = _("Se hizo un nota de crédito %s a la factura %s.") % (rev_invoice_id.name, self.itl_invoice_origin.name)
            self.message_post(body=msg)

            payment_id = self.env['account.payment'].search([('invoice_ids.id','=',self.itl_invoice_origin.id)])
            if payment_id:
                payment_info = self.itl_invoice_origin._get_payments_reconciled_info()
                _logger.info("===> payment_info: " + str(payment_info))
                payment_ids =  [payment['payment_id'] for payment in payment_info['content']]
                move_id = payment_info['content'][0]['move_id']
                move_id = self.env['account.move'].browse(move_id)
                move_line = self.env['account.move.line'].browse(payment_ids)
                move_line.with_context({'move_id': self.itl_invoice_origin.id}).remove_move_reconcile()

                to_reconcile = self.itl_invoice_origin._get_payments_widget_to_reconcile_info()
                m_lines = self.itl_invoice_origin._get_reversal_move_line()
                ml_to_add = m_lines.filtered(lambda i: i.move_id.id in [rev_invoice_id.id, move_id.id])
                _logger.info("===> ml_to_add: " + str(ml_to_add))
                for ml in ml_to_add:
                    self.itl_invoice_origin.js_assign_outstanding_line(ml.id)
            else:
                m_lines = self.itl_invoice_origin._get_reversal_move_line()
                ml_to_add = m_lines.filtered(lambda i: i.move_id.id in [rev_invoice_id.id])
                for ml in ml_to_add:
                    self.itl_invoice_origin.js_assign_outstanding_line(ml.id)
          
        #raise ValidationError("TESTING...")
        return rec
        
    def compute_products_to_return(self):
        return self.move_ids_without_package