from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    day_to_close_month = fields.Integer(related="company_id.day_to_close_month", string="Day to Close Month", default=False, readonly=False)


    @api.onchange('day_to_close_month')
    def onchange_day_to_close_month(self):
        if self.day_to_close_month > 10 or self.day_to_close_month < 1:
            raise ValidationError("El número debe ser mayor a 0 y menor que 10.")