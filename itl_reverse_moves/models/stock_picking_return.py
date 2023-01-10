from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

import logging
_logger = logging.getLogger(__name__)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    
    
    def _create_returns(self):
        res = super(ReturnPicking, self)._create_returns()
        move_obj = self.env['stock.move.line']
        assigned_moves = self.env['stock.move']
        origin_picking_id = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        pick_id = self.env['stock.picking'].browse(res[0])
        pick_id.itl_is_return = True
        pick_id.itl_delivery_by = False
        pick_id.itl_transfer_origin = False
        pick_id.itl_driver_name = False
        pick_id.itl_type_of_car = False
        pick_id.itl_plate_of_car = False
        pick_id.itl_delivery_by = False
        pick_id.itl_pickup_date = False
        pick_id.itl_delivery_date = False
        pick_id.itl_logistic_company_id = False
        pick_id.itl_logistic_company_email = False
        pick_id.itl_employee_partner_id = False
        pick_id.itl_purchase_id = False
        pick_id.immediate_transfer = True
        pick_id.itl_origin_sale = self.picking_id.origin
        pick_id._get_address()
        pick_id._get_warehouse()
        pick_id.group_id = origin_picking_id.group_id
        pick_id.sale_id = origin_picking_id.sale_id
        for move in pick_id.mapped('move_lines').filtered(lambda x:x.state == 'assigned' and x.origin_returned_move_id and x.product_id.tracking == 'lot'):
            move.move_line_ids.unlink()
            for line in move.origin_returned_move_id.move_line_ids:
                qty = move.product_uom_qty
                qty_todo = min(qty , line.qty_done)
                vals = move._prepare_move_line_vals(qty_todo)
                val = {'picking_id': vals['picking_id'],
                        'product_id': line.product_id.id,
                        'move_id':move.id,
                        'location_id':origin_picking_id.location_dest_id.id,
                        'location_dest_id':vals['location_dest_id'],
                        'qty_done':line.qty_done,
                        'itl_product_available_to_return': line.qty_done,
                        'product_uom_id':vals['product_uom_id'],
                        'lot_id':line.lot_id and line.lot_id.id or False,
                        'lot_name':line.lot_id and line.lot_id.name or False
                       }
                move_obj.create(val)
            assigned_moves |= move
        
        if assigned_moves:
            assigned_moves.write({'state': 'draft'})
        
        return res