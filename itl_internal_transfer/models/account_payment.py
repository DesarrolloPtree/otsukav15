from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class account_payment(models.Model):
    _inherit = "account.payment"
    
    itl_destination_amount = fields.Monetary(string="Destination amount", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    itl_destination_currency = fields.Many2one('res.currency', copy=False, compute="_get_company_currency", default=lambda self: self.env.company.currency_id)
    
    itl_has_different_currencies = fields.Boolean(compute="_check_currencies")
    
    itl_pay_at_same = fields.Boolean(string="Two transfers at same time", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    itl_second_payment_id = fields.Many2one('account.payment', string='Second Transfer', readonly=True, copy=False)
    itl_journal_id = fields.Many2one('account.journal', string='From Journal', readonly=True, states={'draft': [('readonly', False)]}, tracking=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    itl_destination_journal_id = fields.Many2one('account.journal', string='To Journal', domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]", readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    
    @api.onchange('destination_journal_id')
    def _get_destination_journal(self):
        if self.destination_journal_id:
            self.itl_journal_id = self.destination_journal_id
    
    @api.depends('destination_journal_id')
    def _get_company_currency(self):
        for record in self:
            record.itl_destination_currency = False
            if record.destination_journal_id and record.destination_journal_id.currency_id:
                record.itl_destination_currency = record.destination_journal_id.currency_id
    
    @api.depends('journal_id','destination_journal_id')
    def _check_currencies(self):
        for record in self:
            record.itl_has_different_currencies = False
            if record.payment_type == 'transfer':
                if record.journal_id.currency_id == record.destination_journal_id.currency_id and record.destination_journal_id.currency_id != record.company_id.currency_id:
                    record.itl_has_different_currencies = False
                    return
                if record.destination_journal_id.currency_id and record.journal_id.currency_id != record.destination_journal_id.currency_id:
                    record.itl_has_different_currencies = True
                    return
                if record.journal_id.currency_id == record.destination_journal_id.currency_id and record.destination_journal_id.currency_id != record.company_id.currency_id:
                    record.itl_has_different_currencies = True
                    return
    
    def _prepare_payment_moves(self):
        all_move_vals = super(account_payment, self)._prepare_payment_moves()
        for payment in self:
            if payment.payment_type == 'transfer':
                if (payment.journal_id.currency_id == payment.destination_journal_id.currency_id and payment.destination_journal_id.currency_id != payment.company_id.currency_id) and not payment.itl_pay_at_same:
                    return all_move_vals
                if payment.journal_id.currency_id != payment.destination_journal_id.currency_id and payment.destination_journal_id.currency_id == payment.company_id.currency_id:
                    #pass
                    #all_move_vals[0]['line_ids'][1][2]['amount_currency'] = all_move_vals[0]['line_ids'][1][2]['amount_currency'] * -1
                    all_move_vals[0]['line_ids'][0][2]['debit'] = payment.itl_destination_amount
                    all_move_vals[0]['line_ids'][1][2]['credit'] = payment.itl_destination_amount

                    all_move_vals[1]['line_ids'][1][2]['currency_id'] = False
                    all_move_vals[1]['line_ids'][1][2]['amount_currency'] = payment.itl_destination_amount

                    all_move_vals[1]['line_ids'][0][2]['credit'] = payment.itl_destination_amount
                    all_move_vals[1]['line_ids'][1][2]['debit'] = payment.itl_destination_amount

                if payment.journal_id.currency_id != payment.destination_journal_id.currency_id and payment.destination_journal_id.currency_id != payment.company_id.currency_id:
                    all_move_vals[1]['line_ids'][1][2]['amount_currency'] = self.itl_destination_amount

                if (payment.journal_id.currency_id == payment.destination_journal_id.currency_id and payment.destination_journal_id.currency_id != payment.company_id.currency_id) and payment.itl_pay_at_same:
                    all_move_vals[0]['line_ids'][0][2]['debit'] = payment.itl_destination_amount
                    all_move_vals[0]['line_ids'][1][2]['credit'] = payment.itl_destination_amount

                    all_move_vals[1]['line_ids'][0][2]['credit'] = payment.itl_destination_amount
                    all_move_vals[1]['line_ids'][1][2]['debit'] = payment.itl_destination_amount
        
        
        return all_move_vals
    
    # Inherit
    def post(self):
        result = super(account_payment, self).post()
        for rec in self:
            if rec.itl_pay_at_same and rec.itl_second_payment_id and rec.itl_second_payment_id.state == 'draft':
                rec.itl_second_payment_id.journal_id = rec.destination_journal_id
                rec.itl_second_payment_id.destination_journal_id = rec.itl_destination_journal_id
                rec.itl_second_payment_id.itl_destination_amount = rec.itl_destination_amount
                rec.itl_second_payment_id.post()
            if rec.itl_pay_at_same and not rec.itl_second_payment_id:
                new_payment = rec.copy({'journal_id': rec.itl_journal_id.id, 
                                        'destination_journal_id': rec.itl_destination_journal_id.id, 
                                        'itl_destination_amount': rec.itl_destination_amount,
                                       'payment_date': rec.payment_date})
                new_payment.post()
                rec.itl_second_payment_id = new_payment
                
        return result
    
    # Inherit
    def action_draft(self):
        result = super(account_payment, self).action_draft()
        for record in self:
            if record.itl_pay_at_same and record.itl_second_payment_id:
                record.itl_second_payment_id.action_draft()
                
        return result