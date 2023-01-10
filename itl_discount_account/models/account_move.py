from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    def post(self):
        res = super(AccountMove, self).post()
        for move in self:
            if move.type in ['out_invoice']:
                # Check if invoice is comming from discount type sale order
                if move.sale_type_id.itl_is_discount_type:
                    # Find cost line
                    expense_line_ids = move.line_ids.filtered(lambda i: i.product_id and i.debit > 0)
                    cost_account_id = False
                    for line in expense_line_ids:
                        cost_account_id = line
                        break
                    # Create two extra lines in journal items, Discount 501.01.004 as debit and Cost account as credit
                    line_ids = move.get_extra_line_discount(move.sale_type_id.itl_discount_account, cost_account_id)
                    if line_ids:
                        move_line = self.env['account.move.line'].create(line_ids)
        return res

    # New method to get extra lines
    def get_extra_line_discount(self, itl_discount_account, cost_account_id):
        line_ids = []
        for move in self:
            for line in move.invoice_line_ids:
                # Convert the current UoM to units of total qty
                uom_id = self.env['uom.uom'].browse(1)
                qty_units = line.product_uom_id._compute_quantity(line.quantity, uom_id)
                cost_amount = cost_account_id.debit
                if qty_units == 0:
                    raise ValidationError("The quantity in units is equal to 0. Please, contact your administrator.")
                if cost_amount == 0:
                    raise ValidationError("The total cost is equal to 0. Please, contact your administrator.")
                # Get unit cost
                cost_unit = cost_amount / qty_units
                # Get discount units
                qty_discount_units = line.product_uom_id._compute_quantity(line.itl_qty_uom_discount, uom_id)
                # Get discount amount
                discount_amount = cost_unit * qty_discount_units
                
                line_ids.append({
                    'account_id':itl_discount_account.id,
                    'name': itl_discount_account.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'debit': discount_amount,
                    'exclude_from_invoice_tab': True,
                    'is_anglo_saxon_line': True,
                })
                
                line_ids.append({
                    'account_id': cost_account_id.account_id.id,
                    'name': cost_account_id.account_id.name,
                    'move_id': self.id,
                    'partner_id': cost_account_id.partner_id.id,
                    'company_id': cost_account_id.company_id.id,
                    'company_currency_id': cost_account_id.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'credit': discount_amount,
                    'exclude_from_invoice_tab': True,
                    'is_anglo_saxon_line': True,
                })
                
        return line_ids
        
        
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    itl_qty_uom_discount = fields.Integer(string="Caja/Unidad Disc.", readonly=True, copy=False)