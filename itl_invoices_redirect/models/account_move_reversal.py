# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.addons.itl_reverse_moves.models.account_move_reversal import AccountMoveReversal as AMR

import logging
_logger = logging.getLogger(__name__)

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
        context = self.env.context.copy()
        if self.normal_refund and 'financial_refund' in context:
            del context['financial_refund']
            self.env.context = context
        new_moves = moves.with_context(normal_refund=self.normal_refund)._reverse_moves(default_values_list, cancel=is_cancel_needed)
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

AMR.reverse_moves = reverse_moves

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'


    normal_refund = fields.Boolean(string="Normal Refund")