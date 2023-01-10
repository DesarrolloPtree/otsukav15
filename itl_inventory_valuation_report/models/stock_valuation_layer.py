from odoo import fields, models, tools, api
import logging
_logger = logging.getLogger(__name__)

class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""
    _inherit = 'stock.valuation.layer'


    picking_id = fields.Many2one(related="stock_move_id.picking_id", store=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", compute="_compute_warehouse")
    picking_type_id = fields.Many2one(related='picking_id.picking_type_id', store=True)
    picking_code = fields.Selection(related='picking_id.picking_type_id.code', store=True)
    move_code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer'),('adjustment','Adjustment'),('price_adj','Price Adjustment'),('landed_cost','Landed Cost')], compute="_compute_move_code", store=True)
    internal_transfer_type = fields.Selection([('internal_out','Transfer Out'),('internal_in','Transfer In')], string="Internal Transfer Type", compute="_compute_internal_transfer_type", store=True)
    ref_invoices = fields.Char(string="Ref", compute="_compute_ref_invoices")
    
    @api.depends('stock_move_id')
    def _compute_ref_invoices(self):
        for record in self:
            record.ref_invoices = False
            if record.move_code == 'outgoing' and record.stock_move_id and record.stock_move_id.origin:
                sale_id = self.env['sale.order'].search([('name','=',record.stock_move_id.origin)], limit=1)
                record.ref_invoices = ', '.join(sale_id.invoice_ids.mapped('name'))
        

    @api.depends('picking_id','picking_code')
    def _compute_internal_transfer_type(self):
        for record in self:
            record.internal_transfer_type = False
            if record.picking_code == 'internal':
                if record.picking_id.location_id.usage == 'transit' and record.picking_id.location_dest_id.usage == 'internal':
                    record.internal_transfer_type = 'internal_in'
                if record.picking_id.location_id.usage == 'internal' and record.picking_id.location_dest_id.usage == 'transit':
                    record.internal_transfer_type = 'internal_out'

    @api.depends('picking_id','picking_code')
    def _compute_move_code(self):
        for record in self:
            record.move_code = False
            if not record.picking_id and record.stock_move_id:
                if record.stock_move_id.location_id.usage == 'inventory' or record.stock_move_id.location_dest_id.usage == 'inventory':
                    record.move_code = 'adjustment'
            elif record.picking_id and not record.stock_landed_cost_id:
                record.move_code = record.picking_code
            elif record.picking_id and record.stock_landed_cost_id:
                record.move_code = 'landed_cost'
            else:
                record.move_code = 'price_adj'

    @api.depends()
    def _compute_warehouse(self):
        _logger.info("===> ENTROOOOO")
        for record in self:
            record.warehouse_id = False
            if record.picking_id.itl_warehouse_id:
                record.warehouse_id = record.picking_id.itl_warehouse_id
            if record.picking_id.itl_location_warehouse_id:
                record.warehouse_id = record.picking_id.itl_location_warehouse_id