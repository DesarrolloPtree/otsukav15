from operator import inv
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)
import io
import base64
try:
    import xlwt
except ImportError:
    xlwt = None


class AccountMove(models.Model):
    _inherit = 'account.move'


    def itl_ar_report(self):
        if xlwt:
            filename = 'AR Report.xls'
            workbook = xlwt.Workbook()
            stylePC = xlwt.XFStyle()
            alignment = xlwt.Alignment()
            alignment.horz = xlwt.Alignment.HORZ_CENTER
            fontP = xlwt.Font()
            fontP.bold = True
            fontP.height = 200
            stylePC.font = fontP
            stylePC.num_format_str = '@'
            stylePC.alignment = alignment
            style_title = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on; align: horiz center")
            style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center; border : bottom thin,right thin,top thin,left thin; pattern: pattern solid, fore_colour pale_blue;")
            style_table_header_2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center; border : bottom thin,right thin,top thin,left thin; pattern: pattern solid, fore_colour tan;")
            style = xlwt.easyxf('border : bottom thin,right thin,top thin,left thin;')
            borders = xlwt.Borders()
            borders.bottom = borders.top = borders.left = borders.right = xlwt.Borders.THIN
            #Format Currency
            currency_format = xlwt.XFStyle()
            currency_format.num_format_str = '$#,##0.00'
            currency_format.borders = borders
            qty_format = xlwt.XFStyle()
            qty_format.num_format_str = '#,##0'
            qty_format.borders = borders
            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'mm/dd/yyyy'
            date_format.borders = borders
            worksheet = workbook.add_sheet('Sheet 1')

            common_width = 367
            worksheet.write(1, 1, 'No.', style_table_header)
            worksheet.col(1).width = 3 * common_width
            worksheet.write(1, 2, 'Customer', style_table_header)
            worksheet.col(2).width = 25 * common_width
            worksheet.write(1, 3, 'Sale Order', style_table_header)
            worksheet.col(3).width = 8 * common_width
            worksheet.write(1, 4, 'Amount', style_table_header)
            worksheet.col(4).width = 10 * common_width
            worksheet.write(1, 5, 'Channel', style_table_header)
            worksheet.col(5).width = 20 * common_width
            worksheet.write(1, 6, 'Customer Payment Terms', style_table_header)
            worksheet.col(6).width = 20 * common_width
            worksheet.write(1, 7, 'Customer Credit Limit', style_table_header)
            worksheet.col(7).width = 15 * common_width
            worksheet.write(1, 8, 'Invoice Number', style_table_header)
            worksheet.col(8).width = 12 * common_width
            worksheet.write(1, 9, 'Payment State', style_table_header)
            worksheet.col(9).width = 10 * common_width
            worksheet.write(1, 10, 'Invoice Payment Terms', style_table_header)
            worksheet.col(10).width = 20 * common_width
            worksheet.write(1, 11, 'Day of AR', style_table_header)
            worksheet.col(11).width = 8 * common_width
            worksheet.write(1, 12, 'Invoice Date', style_table_header)
            worksheet.col(12).width = 10 * common_width
            worksheet.write(1, 13, 'Due Date', style_table_header)
            worksheet.col(13).width = 10 * common_width
            worksheet.write(1, 14, 'Today', style_table_header)
            worksheet.col(14).width = 10 * common_width

            number = 1
            row = 2
            for invoice in self:
                worksheet.write(row, 1, number, style)
                worksheet.write(row, 2, str(invoice.partner_id.name or invoice.partner_id.parent_id.name or ""), style)
                # if len(sale.partner_id.name) > name_len:
                #     name_len = len(sale.partner_id.name)
                #     worksheet.col(2).width = name_len * 367
                worksheet.write(row, 3, str(invoice.invoice_origin or ""), style)
                worksheet.write(row, 4, invoice.amount_total, currency_format)
                worksheet.write(row, 5, str(invoice.partner_id.sale_channel_id.name or ""), style)
                # if len(str(sale.partner_id.sale_channel_id.name)) > channel_len:
                #     channel_len = len(sale.partner_id.sale_channel_id.name)
                #     worksheet.col(5).width = channel_len * 367
                worksheet.write(row, 6, str(invoice.partner_id.property_payment_term_id.name or ""), style)
                # if len(str(sale.partner_id.property_payment_term_id.name)) > paymnt_len:
                #     paymnt_len = len(sale.partner_id.property_payment_term_id.name)
                #     worksheet.col(6).width = paymnt_len * 367
                worksheet.write(row, 7, invoice.partner_id.credit_limit, currency_format)
                # if len(str(sale.partner_id.credit_limit)) > credit_len:
                #     credit_len = len(str(sale.partner_id.credit_limit))
                #     worksheet.col(7).width = credit_len * 367
                
                worksheet.write(row, 8, str(invoice.name), style)
                worksheet.write(row, 9, str(dict(invoice._fields['invoice_payment_state'].selection).get(invoice.invoice_payment_state)), style)
                # if len(invoice_id[0].name) > invoice_len:
                #     invoice_len = len(invoice_id[0].name)
                #     worksheet.col(9).width = invoice_len * 367
                worksheet.write(row, 10, str(invoice.invoice_payment_term_id.name or ""), style)
                if invoice.invoice_date:
                    worksheet.write(row, 11, (fields.Date.today() - invoice.invoice_date).days, qty_format)
                else:
                    worksheet.write(row, 11, "", qty_format)
                # if len(invoice_id[0].invoice_payment_term_id.name) > paymnt_len2:
                #     paymnt_len2 = len(invoice_id[0].name)
                #     worksheet.col(10).width = paymnt_len2 * 367
                worksheet.write(row, 12, invoice.invoice_date or "", date_format)
                worksheet.write(row, 13, invoice.invoice_date_due or "", date_format)
                worksheet.write(row, 14, fields.Date.today(), date_format)

                row += 1
                number += 1

            fp = io.BytesIO()
            workbook.save(fp)
            
            gentextfile = base64.encodestring(fp.getvalue())

            export_id = self.env['itl.ar.report'].create({'excel_file': gentextfile, 'file_name': filename})
            res = {
                    'view_mode': 'form',
                    'res_id': export_id.id,
                    'res_model': 'itl.ar.report',
                    'type': 'ir.actions.act_window',
                    'target':'new'
                }
            return res
        else:
            raise Warning (""" You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")