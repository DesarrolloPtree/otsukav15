
from odoo import api, fields, models
from odoo.exceptions import Warning

class sale_day_book_report_excel(models.TransientModel):
    _name = "itl.ar.report"
    
    
    excel_file = fields.Binary('AR Report')
    file_name = fields.Char('AR Report', size=64)