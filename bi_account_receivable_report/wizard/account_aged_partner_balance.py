# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import base64
import io
import time

import xlwt
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _
from odoo.exceptions import UserError


class BiAccountAgedPartnerBalance(models.TransientModel):
    _name = 'bi.account.aged.partner.balance'

    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)
    partner_ids = fields.Many2many('res.partner')
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
   

    def print_report_aged_partner(self):
        if self.period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not self.date_from:
            raise UserError(_('You must set a start date.'))
        partner_list  = []
        for partner in self.partner_ids:
 
            partner_list.append(partner.id)
              
        start = self.date_from
        data = {}
        res = {}
        used_context = {}
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=self.period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (
                            str((5 - (i + 1)) * self.period_length) + '-' + str((5 - i) * self.period_length)) or (
                                     '+' + str(4 * self.period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'] = ({
            'target_move': self.target_move,
            'result_selection': self.result_selection,
            'period_length': self.period_length,
            'journal_ids': [a.id for a in self.env['account.journal'].search([])],
            'date_from': self.date_from,
            'partner_ids': partner_list,
        })
        used_context.update(
            {
                'state': self.target_move,
                'strict_range': True,
                'journal_ids': [a.id for a in self.env['account.journal'].search([])],
                'date_from': self.date_from,
                'partner_ids': partner_list, 
            }
        )
        data['form']['used_context'] = used_context
        data['form'].update(res)
        return self.env.ref('bi_account_receivable_report.bi_report_rec1').with_context(
                landscape=True).report_action(self, data=data)
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
