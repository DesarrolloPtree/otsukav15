# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    
    # Inherited
    @api.model
    def default_get(self, fields):
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.env['account.move']
        # Modification
        #res['move_type'] = len(move_ids) == 1 and move_ids.type or False
        types = move_ids.mapped('type')
        if len(types) == 0:
            same_value = False
        else:
            same_value = types.count(types[0]) == len(types)
        if same_value:
            res['move_type'] = types[0]
            res['residual'] = 1
        else:
            res['move_type'] = len(move_ids) == 1 and move_ids.type or False
        return res
    
    # Inherited
    @api.depends('move_id')
    def _compute_from_moves(self):
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id
        for record in self:
            record.currency_id = len(move_ids.currency_id) == 1 and move_ids.currency_id or False
            # Modification
            #record.move_type = len(move_ids) == 1 and move_ids.type or False
            types = move_ids.mapped('type')
            same_value = types.count(types[0]) == len(types)
            if same_value:
                record.move_type = types[0]
                record.residual = 1
            else:
                record.move_type = len(move_ids) == 1 and move_ids.type or False
                record.residual = len(move_ids) == 1 and move_ids.amount_residual or 0
    
    # Inherited
    def reverse_moves(self):
        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id
        moves_orig = moves
        
        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = bool(default_vals.get('auto_post'))
            is_cancel_needed = not is_auto_post and self.refund_method in ('cancel', 'modify')
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
            new_moves_rorig = new_moves
            if self.refund_method == 'modify':
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date': self.date or move.date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)
            moves_to_redirect |= new_moves
        # Code added
        for move in moves_to_redirect:
            move.l10n_mx_edi_payment_method_id = move.partner_id.itl_payment_method_id.id
            move.l10n_mx_edi_usage = move.partner_id.itl_usage
            move.invoice_payment_term_id = move.partner_id.property_payment_term_id
        #raise UserError("TTTTTESTING...")
        
        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
                'context':{'default_type':  moves_to_redirect.type},
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
            if len(set(moves_to_redirect.mapped('type'))) == 1:
                action['context'] = {'default_type':  moves_to_redirect.mapped('type').pop()}
        return action
        
        
    def itl_reverse_moves(self, product_returns=None):
        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = bool(default_vals.get('auto_post'))
            is_cancel_needed = not is_auto_post and self.refund_method in ('cancel', 'modify')
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            if len(default_values_list) > 0:
                default_values_list[0]['itl_subtype_refund'] = 'inventory_refund'
            new_moves = moves._itl_reverse_moves(product_returns, default_values_list, cancel=is_cancel_needed)

            if self.refund_method == 'modify':
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date': self.date or move.date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves
        #raise UserError("TESTING***Ñ--")
        return moves_to_redirect