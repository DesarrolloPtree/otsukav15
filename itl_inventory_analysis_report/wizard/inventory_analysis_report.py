import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

import io
try:
    import xlwt
except ImportError:
    xlwt = None

class InventoryAnalysisReport(models.TransientModel):
    _name = "inventory.analysis.report"

    start_date = fields.Date('Start Period')
    end_date = fields.Date('End Period')


    def print_exl_report(self):
        if xlwt:
            data = self.get_data()
            filename = 'Inventory Analysis Report.xls'
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
            qty_format.num_format_str = '#,##0.00'
            qty_format.borders = borders
            worksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)

            worksheet.write_merge(0, 1, 1, 6, "Inventory Analysis Report", style=style_title)
            worksheet.write(5, 1, 'Start Date:', style_table_header)
            worksheet.write(6, 1, str(self.start_date))
            worksheet.write(5, 2, 'End Date', style_table_header)
            worksheet.write(6, 2, str(self.end_date))

            worksheet.write_merge(8, 8, 1, 7,'Sales Orders', style_table_header)
            worksheet.write(9, 1, 'Number', style_table_header)
            worksheet.write(9, 2, 'Date', style_table_header)
            worksheet.write(9, 3, 'Quantity', style_table_header)
            worksheet.write(9, 4, 'Price', style_table_header)
            worksheet.write(9, 5, 'Subtotal', style_table_header)
            worksheet.write(9, 6, 'Taxes', style_table_header)
            worksheet.write(9, 7, 'Total', style_table_header)

            worksheet.write_merge(8, 8, 8, 12,'Delivery', style_table_header_2)
            worksheet.write(9, 8, 'Done Qty', style_table_header_2)
            worksheet.write(9, 9, 'Debit Account', style_table_header_2)
            worksheet.write(9, 10, 'Debit', style_table_header_2)
            worksheet.write(9, 11, 'Credit Account', style_table_header_2)
            worksheet.write(9, 12, 'Credit', style_table_header_2)

            #worksheet.write_merge(8, 8, 13, 24,'Invoice', style_table_header)
            #worksheet.write(9, 13, 'SAT Status', style_table_header)
            #worksheet.write(9, 14, 'PAC Status', style_table_header)
            #worksheet.write(9, 13, 'Sale Account', style_table_header)
            #worksheet.write(9, 14, 'Amount', style_table_header)
            #worksheet.write(9, 15, 'VAT Account', style_table_header)
            #worksheet.write(9, 16, 'Amount', style_table_header)
            #worksheet.write(9, 17, 'AR', style_table_header)
            #worksheet.write(9, 18, 'Amount', style_table_header)
            #worksheet.write(9, 19, 'Inv. In Transit', style_table_header)
            #worksheet.write(9, 20, 'Amount', style_table_header)
            #worksheet.write(9, 21, 'COGS', style_table_header)
            #worksheet.write(9, 22, 'Amount', style_table_header)

            prod_row = 10
            prod_row_2 = 10
            prod_row_3 = 10
            prod_col = 1
            len_accounts = 0
            len_accounts_end = 0
            for sale in data:
                worksheet.write(prod_row, prod_col, sale.name, style)
                worksheet.write(prod_row, prod_col+1, sale.date_order.strftime("%d/%m/%Y %H:%M:%S"), style)
                if len(sale.order_line) > 0:
                    uom = sale.order_line[0].product_uom
                    unit_uom = self.env['uom.uom'].browse(1)
                    product_uom_qty = uom._compute_quantity(sum(sale.order_line.mapped('product_uom_qty')), unit_uom)
                    worksheet.write(prod_row, prod_col+2, product_uom_qty, qty_format)
                worksheet.write(prod_row, prod_col+3, sum(sale.order_line.mapped('price_unit')) / len(sale.order_line), currency_format)
                worksheet.write(prod_row, prod_col+4, sale.amount_untaxed, currency_format)
                worksheet.write(prod_row, prod_col+5, sale.amount_tax, currency_format)
                worksheet.write(prod_row, prod_col+6, sale.amount_total, currency_format)
                pickings = sale.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing' and p.state == 'done')
                for picking in pickings:
                    worksheet.write(prod_row_2, prod_col+7, sum(picking.move_ids_without_package.mapped('quantity_done')), qty_format)

                    move = self.env['account.move'].search([('ref','ilike',picking.name)], limit=1)

                    if move:
                        for line in move.line_ids:
                            if line.debit > 0:
                                worksheet.write(prod_row_2, prod_col+8, line.account_id.display_name, currency_format)
                                worksheet.write(prod_row_2, prod_col+9, line.debit, currency_format)
                            if line.credit > 0:
                                worksheet.write(prod_row_2, prod_col+10, line.account_id.display_name, currency_format)
                                worksheet.write(prod_row_2, prod_col+11, line.credit, currency_format)
                            #prod_row_3 = prod_row_3 + 1
                    if len(pickings) > 1:
                        prod_row_2 = prod_row_2 + 1
                invoices = sale.invoice_ids.filtered(lambda i: i.type == 'out_invoice' and i.state == 'posted')
                prod_col2 = prod_col + 12
                for invoice in invoices:
                    len_accounts = len(invoice.line_ids)
                    if len_accounts > len_accounts_end:
                        len_accounts_end = len_accounts
                    worksheet.write(prod_row_3, prod_col2, invoice.l10n_mx_edi_sat_status, currency_format)
                    prod_col2 += 1
                    worksheet.write(prod_row_3, prod_col2, invoice.l10n_mx_edi_pac_status, currency_format)
                    for line in invoice.line_ids:
                        prod_col2 += 1
                        worksheet.write(prod_row_3, prod_col2, line.account_id.display_name, currency_format)
                        if line.debit > 0:
                            prod_col2 += 1
                            worksheet.write(prod_row_3, prod_col2, line.debit, currency_format)
                        if line.credit > 0:
                            prod_col2 += 1
                            worksheet.write(prod_row_3, prod_col2, line.credit, currency_format)
                    
                    if len(invoices) > 1:
                        prod_row_3 = prod_row_3 + 1

                if prod_row_2 > prod_row_3:
                    prod_row = prod_row_2
                else:
                    prod_row = prod_row_3

                prod_row += 1
                prod_row_2 = prod_row
                prod_row_3 = prod_row
            len_table = len_accounts_end*2 + 14
            worksheet.write_merge(8, 8, 13, len_table,'Invoice', style_table_header)
            worksheet.write(9, 13, 'SAT Status', style_table_header)
            worksheet.write(9, 14, 'PAC Status', style_table_header)
            m = 0
            for n in range(1,len_accounts_end + 1):
                worksheet.write(9, 14 + n + m, 'Account ' + str(n), style_table_header)
                worksheet.write(9, 14 + n + 1 + m, 'Amount', style_table_header)
                m += 1
            
            fp = io.BytesIO()
            workbook.save(fp)
            
            export_id = self.env['inventory.analysis.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            res = {
                    'view_mode': 'form',
                    'res_id': export_id.id,
                    'res_model': 'inventory.analysis.report.excel',
                    'type': 'ir.actions.act_window',
                    'target':'new'
                }
            return res
        else:
            raise Warning (""" You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")


    def get_data(self):
        sales = self.env['sale.order'].search([('date_order','>=',self.start_date),('date_order','<=',self.end_date),('state','in',['sale','done'])])

        return sales

class InventoryAnalysisReportExcel(models.TransientModel):
    _name = "inventory.analysis.report.excel"
    
    
    excel_file = fields.Binary('Excel Report ')
    file_name = fields.Char('Excel File', size=64)