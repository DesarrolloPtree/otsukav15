# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    def itl_duplicate_sale_order(self):
        view = self.env.ref('itl_so_type_duplicate.itl_duplicate_sale_order_form')
        view_id = view and view.id or False
        context = dict(self._context or {})

        return {
            'name': 'Select Order Type',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.duplicate.sale.order',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }
        
        
        #default = dict(default or {})
        #rec = super(SaleOrder, self).copy(default)
        #return rec