# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import datetime
import dateutil.relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import pytz

_logger = logging.getLogger(__name__)

class Company(models.Model):
    _inherit = 'res.company'
    

    day_to_close_month = fields.Integer(string="Day to Close Month", default=1)

    @api.onchange('day_to_close_month')
    def onchange_day_to_close_month(self):
        if self.day_to_close_month > 10 or self.day_to_close_month < 1:
            raise ValidationError("El número debe ser mayor a 0 y menor que 10.")
    
    def write(self, vals):
        record = super(Company, self).write(vals)
        if 'day_to_close_month' in vals:
            day_to_close_month = vals['day_to_close_month']
            cron_id = self.env.ref('itl_change_lock_date_fiscalyear.ir_cron_lock_date_for_all_user')
            schedule_date = cron_id.nextcall
            cron_id.nextcall = schedule_date.replace(day=day_to_close_month)

        return record
     
    def _validate_fiscalyear_lock(self, values):
        if values.get('fiscalyear_lock_date'):
            nb_draft_entries = self.env['account.move'].search([
                ('company_id', 'in', [c.id for c in self]),
                ('date', '<=', values['fiscalyear_lock_date'])])
            if nb_draft_entries:
                pass
                #raise ValidationError(_('There are still unposted entries in the period you want to lock. You should either post or delete them.'))

    def _cron_change_lock_date_for_all_users_and_tax(self):
        cron_id = self.env.ref('itl_change_lock_date_fiscalyear.ir_cron_lock_date_for_all_user')
        today = cron_id.nextcall
        tz = pytz.timezone('Mexico/General')
        time = pytz.utc.localize(today).astimezone(tz)
        today = time + dateutil.relativedelta.relativedelta(months=-1)
        last_day_month = self.lom(today.year, today.month, today.day)
        self.env.company.sudo().write({
                'fiscalyear_lock_date': last_day_month,
                'tax_lock_date': last_day_month
            })
        self.env['fiscal.month'].sudo().create({'state': 'closed', 'fiscal_date': last_day_month})

    def _cron_change_period_lock_date(self):
        cron_id = self.env.ref('itl_change_lock_date_fiscalyear.ir_cron_lock_fiscal_date')
        today = cron_id.nextcall
        tz = pytz.timezone('Mexico/General')
        time = pytz.utc.localize(today).astimezone(tz)
        last_day_month = self.lom(time.year, time.month, time.day)
        self.env.company.sudo().write({
                'period_lock_date': last_day_month
            })

    def lom(self, year, month, day):
        d = datetime.date(year + int(month/12), month%12+1, 1)-datetime.timedelta(days=1)
        return d