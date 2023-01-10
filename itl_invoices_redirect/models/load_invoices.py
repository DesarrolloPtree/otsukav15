from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64

import logging
_logger = logging.getLogger(__name__)


class LoadInvoicesWizard(models.TransientModel):
    _name = 'load.invoices'
    _description = "Load Invoices"

    itl_file = fields.Binary(string="Seleccione un archivo")
    itl_filename = fields.Char()
    itl_show_mode = fields.Selection([('all','All'),('signed','Signed'),('not_signed','Not Signed')], string="Show", default="all")

    @api.onchange('itl_file')
    def _onchnage_itl_filename(self):
        if self.itl_file:
            file_ext = self.get_file_ext(self.itl_filename)
            if file_ext.lower() not in ('txt'):
                raise ValidationError('Solo se permiten archivo con extensión .txt')
            
    def get_file_ext(self, filename):
        """
        obtiene extencion de archivo, si este lo tiene
        fdevuelve false, si no cuenta con una aextension
        (no es archivo entonces)
        """
        file_ext = filename.split('.')
        if len(file_ext) > 1:
            file_ext = filename.split('.')[1]
            return file_ext
        return False
    
    def load_invoices(self):
        if not self.itl_file:
            raise ValidationError("You need to select a file.")
        file_content = base64.decodestring(self.itl_file)
        file_content = file_content.decode("utf-8")
        file_lines = file_content.split("\r\n")
        
        invoices = self.env['account.move'].search([('name','in',file_lines)])
        if self.itl_show_mode == 'all':
            show_invoices = invoices
        if self.itl_show_mode == 'signed':
            show_invoices = invoices.filtered(lambda i: i.l10n_mx_edi_cfdi_uuid != False)
        if self.itl_show_mode == 'not_signed':
            show_invoices = invoices.filtered(lambda i: i.l10n_mx_edi_cfdi_uuid == False)
        #signed_invoices = invoices.filtered(lambda i: i.l10n_mx_edi_cfdi_uuid == False)
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action['domain'] = [('id', 'in', show_invoices.ids)]
        
        return action