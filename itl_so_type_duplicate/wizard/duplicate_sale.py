from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class DuplicateSaleOrder(models.TransientModel):
    _name = 'itl.duplicate.sale.order'
    _description = "Duplicate Sale Order"
    
    
    def _get_sale_order(self):
        sale_order = self._context.get('active_model') == 'sale.order' and self._context.get('active_id') or []
        return sale_order
    
    itl_sale_order_type = fields.Many2one('sale.order.type', string="Type", required=True)
    itl_sale_order_id = fields.Many2one('sale.order', string="Sale order", default=_get_sale_order)

    
    def duplicate_order(self):
        new_sale = self.itl_sale_order_id.copy({'type_id': self.itl_sale_order_type.id})
        context = dict(self._context or {})
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': new_sale.id,
                'context': context,
                'target': 'main'
        }
        
    
    