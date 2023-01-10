from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime

class ALockDateHistory(models.Model):
    _name = 'lock.date.history'
    _description = 'Lock Date History'
    _rec_name = 'write_uid'
    
    company_id = fields.Many2one('res.company', string="Company")