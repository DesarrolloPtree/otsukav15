from odoo import models, fields, api


class StockInventoryLine(models.Model):
    _name = 'stock.inventory.line'
    _inherit = ['stock.inventory.line']

    was_filled = fields.Boolean(
        string="Was filled", default=False, help="If is checked it means that the product_qty " +
        "was already filled (this field also is used to allow extra modifications when is unchecked).")

    prefilled_qty = fields.Selection(
        related='inventory_id.prefill_counted_quantity', string="Prefilled option",
        store=True, readonly=True, related_sudo=False)

    damaged_product_qty = fields.Float(
        'Damaged Products Quantity', digits=0, copy=False, store=True)
    stored_difference_qty = fields.Float(
        "Difference", digits=0, copy=False, store=True, compute="_compute_stored_diff"
    )

    # This field is just to be used on domain condition
    tracking = fields.Selection(related='product_id.tracking', String="Tracking", store=False)

    def show_all_lots(self):
        view = self.env.ref('itl_stock_adjustment.itl_view_stock_lot_all')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['product_id'] = self.product_id.id
        context['stock_inventory_line_id'] = self.id
        return {
            'name': 'More Lots',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.stock.lot.all',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        #  here we check if product_qty was already set and then protect that field
        #  for extra modification. (modifications can be done if was_filled checkbox is unchecked)
        if self.prefilled_qty == 'counted':
            if self.theoretical_qty != self.product_qty:
                self.was_filled = True
        if self.prefilled_qty == 'zero':
            if self.theoretical_qty != self.product_qty:
                self.was_filled = True

    @api.depends('product_qty', 'theoretical_qty', 'damaged_product_qty')
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.product_qty - line.theoretical_qty + line.damaged_product_qty

    @api.depends('difference_qty')
    def _compute_stored_diff(self):
        for record in self:
            record.stored_difference_qty = record.difference_qty

    #ivan_porras
class itlStockLotAll(models.TransientModel):
    _name = "itl.stock.lot.all"
    _description = "Show More Lots"
    _rec_name = "id"
    
    
    @api.model
    def default_get(self, fields):
        res = super(itlStockLotAll, self).default_get(fields)
        
        product_id = self.env['product.product'].browse(self.env.context.get('product_id'))
        sil_id = self.env['stock.inventory.line'].browse(self.env.context.get('stock_inventory_line_id'))
        
        if product_id:
            res['itl_product_id'] = product_id.id
            
        if sil_id:
            res['itl_stock_inventory_line_id'] = sil_id.id
            
        return res
    
    
    itl_lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial Number")
    itl_product_id = fields.Many2one('product.product', string="Product")
    itl_stock_inventory_line_id = fields.Many2one('stock.inventory.line', string="Stock Inventory Line")
    
    
    def use_lot(self):
        self.sudo().itl_stock_inventory_line_id.prod_lot_id = self.itl_lot_id
       
        