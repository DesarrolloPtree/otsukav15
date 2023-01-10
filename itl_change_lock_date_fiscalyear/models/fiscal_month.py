from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class LockDateSecurity(models.Model):
    _name = 'fiscal.month'
    _description = 'Fiscal Months'
    
    state = fields.Selection([('open','Open'),('closed','Closed')], state="Status", required=True)
    fiscal_date = fields.Date(string="Fiscal Date", required=True)
    
    
    #def name_get(self):
    #    result = []
    #    for record in self:
    #        result.append((record.id, "{} {}".format(record.fiscal_date.month, record.year)))
    #    return result