from odoo import models, fields, _, api
from odoo.exceptions import UserError
from datetime import timedelta, datetime

import logging
_logger = logging.getLogger(__name__)

class AccountChangeLockDate(models.TransientModel):
    """
    This wizard is used to change the lock date
    """
    _inherit = 'account.change.lock.date'
    
    def _get_last_update_lock_date(self):
        history = self.env['lock.date.history'].search([], order='write_date desc', limit=1)
        if history:
            return history.write_date
        return False
    
    def _get_last_update_lock_date_user(self):
        history = self.env['lock.date.history'].search([], order='write_date desc', limit=1)
        if history:
            return history.write_uid
        return False
    
    last_lock_date_update_by = fields.Many2one(
        'res.users',
        string="Last lock date update by",
        default=_get_last_update_lock_date_user,
        help='This is the last user that change the lock date.')
    last_lock_date_update_date = fields.Datetime(
        string="Last lock date update date",
        default=_get_last_update_lock_date,
        help='This is the last date that the user change the lock date.')
    fiscalyear_lock_date_enable = fields.Boolean(string="Lock Date for All Users Enable", compute="_get_fiscalyear_lock_date_enable")
    tax_lock_date_enable = fields.Boolean(string="Tax Lock Date Enable", compute="_get_tax_lock_date_enable")
    is_fiscalyear_lock_date_manager = fields.Boolean(string="Is fiscalyear lock date manager", compute="_get_fiscalyear_lock_date_enable")

    
    @api.depends('fiscalyear_lock_date')
    def _get_fiscalyear_lock_date_enable(self):
        month = self.fiscalyear_lock_date.month
        year = self.fiscalyear_lock_date.year
        
        query = "SELECT * FROM fiscal_month WHERE EXTRACT(MONTH FROM fiscal_date) = {month} AND EXTRACT(YEAR FROM fiscal_date) = {year} AND state = 'closed'".format(month=month, year=year)
        
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchone()
        
        if results != None:
            self.fiscalyear_lock_date_enable = False
        else:
            self.fiscalyear_lock_date_enable = True

        self.is_fiscalyear_lock_date_manager = False
        if self.env.user.has_group("itl_change_lock_date_fiscalyear.group_fiscalyear_lock_date_manager"):
            self.is_fiscalyear_lock_date_manager = True
    
    @api.depends('tax_lock_date')
    def _get_tax_lock_date_enable(self):
        month = self.tax_lock_date.month
        year = self.tax_lock_date.year
        
        query = "SELECT * FROM fiscal_month WHERE EXTRACT(MONTH FROM fiscal_date) = {month} AND EXTRACT(YEAR FROM fiscal_date) = {year} AND state = 'closed'".format(month=month, year=year)
        
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchone()
        
        if results != None:
            self.tax_lock_date_enable = False
        else:
            self.tax_lock_date_enable = True

    #Inherit from account_accountant > wizard > account_change_lock_date.py
    def change_lock_date(self):
        result = super(AccountChangeLockDate, self).change_lock_date()
        
        self.onchnage_fiscalyear_lock_date()
        self.onchnage_tax_lock_date()
        
        self.env['lock.date.history'].create({'company_id': self.env.company.id})
        
        return result
    
    #@api.onchange('fiscalyear_lock_date')
    def onchnage_fiscalyear_lock_date(self):
        month = self.fiscalyear_lock_date.month
        year = self.fiscalyear_lock_date.year
        
        query = "SELECT * FROM fiscal_month WHERE EXTRACT(MONTH FROM fiscal_date) = {month} AND EXTRACT(YEAR FROM fiscal_date) = {year} AND state = 'closed'".format(month=month, year=year)
        
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchone()
        
        if results != None:
            raise UserError("You cannot modify the date because the month is closed.")
            
    #@api.onchange('tax_lock_date')
    def onchnage_tax_lock_date(self):
        month = self.tax_lock_date.month
        year = self.tax_lock_date.year
        query = "SELECT * FROM fiscal_month WHERE EXTRACT(MONTH FROM fiscal_date) = {month} AND EXTRACT(YEAR FROM fiscal_date) = {year} AND state = 'closed'".format(month=month, year=year)
        
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchone()
        
        if results != None:
            raise UserError("You cannot modify the date because the month is closed.")
