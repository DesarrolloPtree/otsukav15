import base64
from itertools import groupby
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import requests
from pytz import timezone

from lxml import etree
from lxml.objectify import fromstring
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr
import json
import ast

from odoo.addons.l10n_mx_edi.tools.run_after_commit import run_after_commit

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    itl_subtype_refund = fields.Selection([('financial_refund','Financial Refund'),('inventory_refund','Inventory Refund'),('none','None')], string="Subtype refund", default='none')
    #itl_invoice_origin_id = fields.Many2one('account.move', string="Invoice Origin of Refund")

    #def l10n_mx_edi_request_cancellation(self):
    #    if self.env.context.get('l10n_mx_edi_request_cancellation'):
    #        if self.l10n_mx_motivo_cancelacion == 'none':
    #            raise UserError("No puedes cancelar un CFDI sin motivo de cancelación")
    #        return super(AccountMove, self.with_context(financial_refund=True)).l10n_mx_edi_request_cancellation()
    #    else:
    #        return self.action_reverse()
        
    def action_reverse(self):
        action = super(AccountMove, self).action_reverse()
        context = {}
        if 'context' in action:
            #context = json.loads(action['context'])
            context = ast.literal_eval(action['context'])
            context['financial_refund'] = True
        action['context'] = context
        return action
            
    # Inherited
    def _get_sequence(self):
        self.ensure_one()
        
        if self.itl_subtype_refund == 'inventory_refund':
            sequence = self.env.ref('itl_reverse_moves.sequence_inventory_invoice_refund')
            return sequence
        if self.itl_subtype_refund == 'financial_refund':
            sequence = self.env.ref('itl_reverse_moves.sequence_financial_invoice_refund')
            return sequence
        
        sequence = super(AccountMove, self)._get_sequence()
        
        return sequence
    
    # Inherited
    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        lines_vals_list = super(AccountMove, self)._stock_account_prepare_anglo_saxon_out_lines_vals()
        lines_vals_list = []
        for move in self:
            # Code added
            #raise UserError("TEST")
            if move.itl_subtype_refund in [False, 'financial_refund']:
                continue
            # Make the loop multi-company safe when accessing models like product.product
            move = move.with_context(force_company=move.company_id.id)

            if not move.is_sale_document(include_receipts=True) or not move.company_id.anglo_saxon_accounting:
                continue

            for line in move.invoice_line_ids:

                # Filter out lines being not eligible for COGS.
                if line.product_id.type != 'product' or line.product_id.valuation != 'real_time':
                    continue

                # Retrieve accounts needed to generate the COGS.
                accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)
                debit_interim_account = accounts['stock_output']
                credit_expense_account = accounts['expense']
                if not credit_expense_account:
                    if move.type == 'out_refund':
                        credit_expense_account = move.journal_id.default_credit_account_id
                    else: # out_invoice/out_receipt
                        credit_expense_account = move.journal_id.default_debit_account_id
                if not debit_interim_account or not credit_expense_account:
                    continue

                # Compute accounting fields.
                sign = -1 if move.type == 'out_refund' else 1
                price_unit = line._stock_account_get_anglo_saxon_price_unit()
                balance = sign * line.quantity * price_unit

                # Add interim account line.
                lines_vals_list.append({
                    'name': line.name[:64],
                    'move_id': move.id,
                    'partner_id': move.commercial_partner_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'quantity': line.quantity,
                    'price_unit': price_unit,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'account_id': debit_interim_account.id,
                    'exclude_from_invoice_tab': True,
                    'is_anglo_saxon_line': True,
                })

                # Add expense account line.
                lines_vals_list.append({
                    'name': line.name[:64],
                    'move_id': move.id,
                    'partner_id': move.commercial_partner_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'quantity': line.quantity,
                    'price_unit': -price_unit,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'account_id': credit_expense_account.id,
                    'analytic_account_id': line.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                    'exclude_from_invoice_tab': True,
                    'is_anglo_saxon_line': True,
                })
            
        return lines_vals_list
    
    def _stock_account_prepare_anglo_saxon_out_lines_accounts(self):
        lines_vals_list = []
        for move in self:
            # Make the loop multi-company safe when accessing models like product.product
            move = move.with_context(force_company=move.company_id.id)

            if not move.is_sale_document(include_receipts=True) or not move.company_id.anglo_saxon_accounting:
                continue

            for line in move.invoice_line_ids:

                # Filter out lines being not eligible for COGS.
                if line.product_id.type != 'product' or line.product_id.valuation != 'real_time':
                    continue

                # Retrieve accounts needed to generate the COGS.
                accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)
                debit_interim_account = accounts['stock_output']
                credit_expense_account = accounts['expense']
                if not credit_expense_account:
                    if move.type == 'out_refund':
                        credit_expense_account = move.journal_id.default_credit_account_id
                    else: # out_invoice/out_receipt
                        credit_expense_account = move.journal_id.default_debit_account_id
                if not debit_interim_account or not credit_expense_account:
                    continue

                # Add interim account line.
                lines_vals_list.append(debit_interim_account.id)

                # Add expense account line.
                lines_vals_list.append(credit_expense_account.id)
            
        return lines_vals_list
    
    # Inherited
    def _reverse_move_vals(self, default_values, cancel=True):
        self.ensure_one()
        move_vals = super(AccountMove, self)._reverse_move_vals(default_values, cancel)
        if self.env.context.get('inventory_refund'):
            move_vals['itl_subtype_refund'] = 'inventory_refund'
        if self.env.context.get('financial_refund'):
            move_vals['itl_subtype_refund'] = 'financial_refund'
            accounts = self._stock_account_prepare_anglo_saxon_out_lines_accounts()
            lines_to_remove = []
            if 'line_ids' in move_vals:
                for line in move_vals['line_ids']:
                    if line[2]['account_id'] in accounts:
                        lines_to_remove.append(line)
                for line in lines_to_remove:
                    move_vals['line_ids'].remove(line)
                    
        return move_vals
    
    # Cloned from account
    def _itl_reverse_moves(self, product_returns=False, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
        }

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'type': reverse_type_map[move.type],
                'reversed_entry_id': move.id,
            })
            move_vals_list.append(move.with_context(move_reverse_cancel=cancel)._reverse_move_vals(default_values, cancel=cancel))

        reverse_moves = self.env['account.move'].create(move_vals_list)
        
        # ITL code
        lines_to_update = []
        for l in reverse_moves.invoice_line_ids:
            if product_returns and l.product_id.id in product_returns.mapped('product_id.id'):
                if l.price_subtotal == 0:
                    raise UserError("The subtotal is 0 in invoice line where product is " + str(l.product_id.name))
                unit_uom_id = self.env['uom.uom'].browse(1)
                unit_quantity = l.product_uom_id._compute_quantity(l.quantity, unit_uom_id)
                price_unit = l.price_subtotal / unit_quantity
                product_id = product_returns.filtered(lambda p: p.product_id == l.product_id)[0]
                lines_to_update.append((1,l.id,{
                    'quantity': product_id.quantity_done,
                    'product_uom_id': product_id.product_uom.id,
                    'price_unit': price_unit
                }))
                l._onchange_mark_recompute_taxes()
                l._onchange_price_subtotal()
        reverse_moves.invoice_line_ids = lines_to_update
        reverse_moves._compute_invoice_taxes_by_group()
        #

        for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False)):
            # Update amount_currency if the date has changed.
            if move.date != reverse_move.date:
                for line in reverse_move.line_ids:
                    if line.currency_id:
                        line._onchange_currency()
            reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
        reverse_moves._check_balanced()

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel).post()
            for move, reverse_move in zip(self, reverse_moves):
                accounts = move.mapped('line_ids.account_id') \
                    .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
                for account in accounts:
                    (move.line_ids + reverse_move.line_ids)\
                        .filtered(lambda line: line.account_id == account and line.balance)\
                        .reconcile()

        return reverse_moves

    # Inherited
    def post(self):
        for move in self:
            if 'refund' in move.type:
                for line in move.invoice_line_ids:
                    line._recompute_accounts()
                    
        rec = super(AccountMove, self).post()
        
        for move in self:
            if move.itl_subtype_refund == 'financial_refund' and move.ref and ':' in move.ref:
                ref = str(move.ref.split(':')[1]).strip()
                origin_move_id = self.env['account.move'].search([('name','=',ref)], limit=1)
                if origin_move_id:
                    payment_id = self.env['account.payment'].search([('invoice_ids.id','=',origin_move_id.id)])
                    if payment_id:
                        payment_info = origin_move_id._get_payments_reconciled_info()
                        if not payment_info:
                            return
                        payment_ids = [payment['payment_id'] for payment in payment_info['content']]
                        move_id = payment_info['content'][0]['move_id']
                        move_id = self.env['account.move'].browse(move_id)
                        move_line = self.env['account.move.line'].browse(payment_ids)
                        move_line.with_context({'move_id': origin_move_id.id}).remove_move_reconcile()
                        to_reconcile = origin_move_id._get_payments_widget_to_reconcile_info()
                        m_lines = origin_move_id._get_reversal_move_line()
                        ml_to_add = m_lines.filtered(lambda i: i.move_id.id in [move.id, move_id.id])
                        for ml in ml_to_add:
                            origin_move_id.js_assign_outstanding_line(ml.id)
                    else:
                        m_lines = origin_move_id._get_reversal_move_line()
                        ml_to_add = m_lines.filtered(lambda i: i.move_id.id in [move.id])
                        for ml in ml_to_add:
                            origin_move_id.js_assign_outstanding_line(ml.id)
                
        
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    # inherited from account.move
    def _get_computed_account(self):
        self.ensure_one()
        self = self.with_context(force_company=self.move_id.journal_id.company_id.id)
        
        if self.move_id.itl_subtype_refund in ['financial_refund','inventory_refund']:
            if not self.product_id:
                return

            fiscal_position = self.move_id.fiscal_position_id
            accounts = self.product_id.product_tmpl_id.with_context(is_refund=True).get_product_accounts(fiscal_pos=fiscal_position)
            if self.move_id.is_sale_document(include_receipts=True):
                # Out invoice.
                return accounts['income'] or self.account_id
            elif self.move_id.is_purchase_document(include_receipts=True):
                # In invoice.
                return accounts['expense'] or self.account_id
        else:
            return super(AccountMoveLine, self)._get_computed_account()
        
    
    def _recompute_accounts(self):
        for line in self:
            line.name = line._get_computed_name()
            accounts = line._get_computed_account()
            line.account_id = accounts
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(taxes, partner=line.partner_id)
            line.tax_ids = taxes

