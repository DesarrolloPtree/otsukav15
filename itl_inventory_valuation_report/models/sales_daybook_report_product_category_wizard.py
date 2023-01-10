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

class sale_day_book_wizard(models.TransientModel):
    _inherit = "sale.day.book.wizard"

    # Inherited full method
    def print_exl_report(self):
        if xlwt:
            data  = { 'start_date': self.start_date,
             'end_date': self.end_date,'warehouse':self.warehouse,
             'category':self.category,
             'location_id':self.location_id,
             'company_id':self.company_id.name,
             'display_sum':self.display_sum,
            'currency':self.company_id.currency_id.name,
            'product_ids': self.product_ids,
            'filter_by' : self.filter_by
            }
            filename = 'Stock Valuation Report.xls'
            get_warehouse = self.get_warehouse()
            get_warehouse_name = self._get_warehouse_name()
            l1 = []
            get_company = self.get_company()
            get_currency = self.get_currency()
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
            worksheet = workbook.add_sheet('Sheet 1')
            worksheet.write(5, 1, 'Start Date:', style_table_header)
            worksheet.write(6, 1, str(self.start_date))
            worksheet.write(5, 2, 'End Date', style_table_header)
            worksheet.write(6, 2, str(self.end_date))
            worksheet.write(5, 3, 'Company', style_table_header)
            worksheet.write(6, 3, get_company and get_company[0] or '',)
            worksheet.write(5, 4, 'Warehouse(s)', style_table_header)
            worksheet.write(5, 5, 'Currency', style_table_header)
            worksheet.write(6, 5, get_currency and get_currency[0] or '',)
            w_col_no = 7
            w_col_no1 = 8
            if get_warehouse_name:
                   # w_col_no = w_col_no + 8
                worksheet.write(6, 4,get_warehouse_name, stylePC)
                   # w_col_no1 = w_col_no1 + 9
            if self.display_sum:
                worksheet.write_merge(0, 1, 2, 9, "Inventory Valuation Report with Details", style=style_title)
                worksheet.write(8, 0, 'Default Code', style_table_header)
                worksheet.write(8, 1, 'Name', style_table_header_2)
                worksheet.write(8, 2, 'Category', style_table_header)
                worksheet.write(8, 3, 'Costing Method', style_table_header_2)
                #worksheet.write(8, 4, 'Cost', style_table_header)
                worksheet.write_merge(8, 8, 4, 6,'Beginning', style_table_header)
                worksheet.write_merge(8, 8, 7, 15,'Incoming', style_table_header_2)
                worksheet.write_merge(8, 8, 16, 25,'Outgoing', style_table_header)
                worksheet.write_merge(8, 8, 26, 28,'Ending', style_table_header_2)
                
                worksheet.write(9, 4, 'Cost', style_table_header)
                worksheet.write(9, 5, 'Qty', style_table_header)
                worksheet.write(9, 6, 'Value', style_table_header)

                worksheet.write(9, 7, 'Date', style_table_header_2)
                worksheet.write(9, 8, 'Description', style_table_header_2)
                worksheet.write(9, 9, 'Move Code', style_table_header_2)
                worksheet.write(9, 10, 'Stock Move', style_table_header_2)
                worksheet.write(9, 11, 'Journal Entry', style_table_header_2)
                worksheet.write(9, 12, 'Operation Type', style_table_header_2)
                worksheet.write(9, 13, 'Cost', style_table_header_2)
                worksheet.write(9, 14, 'Qty', style_table_header_2)
                worksheet.write(9, 15, 'Value', style_table_header_2)

                worksheet.write(9, 16, 'Date', style_table_header)
                worksheet.write(9, 17, 'Description', style_table_header)
                worksheet.write(9, 18, 'Move Code', style_table_header)
                worksheet.write(9, 19, 'Stock Move', style_table_header)
                worksheet.write(9, 20, 'Journal Entry', style_table_header)
                worksheet.write(9, 21, 'Operation Type', style_table_header)
                worksheet.write(9, 22, 'Cost', style_table_header)
                worksheet.write(9, 23, 'Qty', style_table_header)
                worksheet.write(9, 24, 'Value', style_table_header)
                worksheet.write(9, 25, 'Ref', style_table_header)

                worksheet.write(9, 26, 'Cost', style_table_header_2)
                worksheet.write(9, 27, 'Qty', style_table_header_2)
                worksheet.write(9, 28, 'Value', style_table_header_2)

                prod_row = 10
                prod_row_2 = 10
                prod_row_3 = 10
                prod_col = 0
                
                get_line = self.get_lines_details(data)
                #lines_receipt = get_line['lines_receipt']
                #lines_issue = get_line['lines_issue']
                for each in get_line:
                    worksheet.write(prod_row, prod_col, each['sku'], style)
                    worksheet.write(prod_row, prod_col+1, each['name'], style)
                    worksheet.write(prod_row, prod_col+2, each['category'], style)
                    worksheet.write(prod_row, prod_col+3, each['costing_method'], style)
                    #worksheet.write(prod_row, prod_col+4, each['cost_price'], currency_format)
                    #
                    worksheet.write(prod_row, prod_col+4, each['price_beginning'], currency_format)
                    worksheet.write(prod_row, prod_col+5, each['beginning'], qty_format)
                    worksheet.write(prod_row, prod_col+6, each['value_beginning'], currency_format)
                    #
                    for line in each['lines_receipt']:
                        move_type = ''
                        if line.move_code == 'internal':
                            move_type = 'Transfer'
                        else:
                            move_type = dict(line._fields['move_code'].selection).get(line.move_code)
                        worksheet.write(prod_row_2, prod_col+7, line.create_date.strftime("%d/%m/%Y %H:%M:%S"), style)
                        worksheet.write(prod_row_2, prod_col+8, line.description, style)
                        worksheet.write(prod_row_2, prod_col+9, move_type, style)
                        worksheet.write(prod_row_2, prod_col+10, line.stock_move_id.display_name or '', style)
                        worksheet.write(prod_row_2, prod_col+11, line.account_move_id.display_name or '', style)
                        worksheet.write(prod_row_2, prod_col+12, line.picking_type_id.display_name or '', style)
                        worksheet.write(prod_row_2, prod_col+13, line.unit_cost, currency_format)
                        worksheet.write(prod_row_2, prod_col+14, line.quantity, qty_format)
                        worksheet.write(prod_row_2, prod_col+15, line.value, currency_format)
                        prod_row_2 = prod_row_2 + 1
                    #
                    for line in each['lines_issue']:
                        move_type = ''
                        if line.move_code == 'internal':
                            move_type = 'Transfer'
                        else:
                            move_type = dict(line._fields['move_code'].selection).get(line.move_code)
                        worksheet.write(prod_row_3, prod_col+16, line.create_date.strftime("%d/%m/%Y %H:%M:%S"), style)
                        worksheet.write(prod_row_3, prod_col+17, line.description, style)
                        worksheet.write(prod_row_3, prod_col+18, move_type, style)
                        worksheet.write(prod_row_3, prod_col+19, line.stock_move_id.display_name or '', style)
                        worksheet.write(prod_row_3, prod_col+20, line.account_move_id.display_name or '', style)
                        worksheet.write(prod_row_3, prod_col+21, line.picking_type_id.display_name or '', style)
                        worksheet.write(prod_row_3, prod_col+22, line.unit_cost, currency_format)
                        worksheet.write(prod_row_3, prod_col+23, line.quantity, qty_format)
                        worksheet.write(prod_row_3, prod_col+24, line.value, currency_format)
                        worksheet.write(prod_row_3, prod_col+25, line.ref_invoices or '', style)
                        prod_row_3 = prod_row_3 + 1

                    worksheet.write(prod_row, prod_col+26, each['price_end'], currency_format)
                    worksheet.write(prod_row, prod_col+27, each['net_on_hand'], qty_format)
                    worksheet.write(prod_row, prod_col+28, each['total_value'], currency_format)

                    if prod_row_2 > prod_row_3:
                        prod_row = prod_row_2
                    else:
                        prod_row = prod_row_3

                    prod_row += 1
                    prod_row_2 = prod_row
                    prod_row_3 = prod_row
                    
                prod_row = 8
                prod_col = 7
            else:
                worksheet.write_merge(0, 1, 2, 9, "Inventory Valuation Report", style=style_title)
                worksheet.write(8, 0, 'Default Code', style_table_header)
                worksheet.write(8, 1, 'Name', style_table_header_2)
                worksheet.write(8, 2, 'Category', style_table_header)
                worksheet.write(8, 3, 'Costing Method', style_table_header_2)
                #worksheet.write(8, 4, 'Cost', style_table_header)
                worksheet.write_merge(8, 8, 4, 6,'Beginning', style_table_header)
                worksheet.write_merge(8, 8, 7, 10,'Incoming', style_table_header_2)
                worksheet.write_merge(8, 8, 11, 14,'Outgoing', style_table_header)
                worksheet.write_merge(8, 8, 15, 17,'Ending', style_table_header_2)
                
                worksheet.write(9, 4, 'Cost', style_table_header)
                worksheet.write(9, 5, 'Qty', style_table_header)
                worksheet.write(9, 6, 'Value', style_table_header)

                worksheet.write(9, 7, 'Type', style_table_header_2)
                worksheet.write(9, 8, 'Cost', style_table_header_2)
                worksheet.write(9, 9, 'Qty', style_table_header_2)
                worksheet.write(9, 10, 'Value', style_table_header_2)

                worksheet.write(9, 11, 'Type', style_table_header)
                worksheet.write(9, 12, 'Cost', style_table_header)
                worksheet.write(9, 13, 'Qty', style_table_header)
                worksheet.write(9, 14, 'Value', style_table_header)

                worksheet.write(9, 15, 'Cost', style_table_header_2)
                worksheet.write(9, 16, 'Qty', style_table_header_2)
                worksheet.write(9, 17, 'Value', style_table_header_2)

                prod_row = 10
                prod_col = 0
                
                get_line = self.get_lines(data)
                for each in get_line:
                    worksheet.write(prod_row, prod_col, each['sku'], style)
                    worksheet.write(prod_row, prod_col+1, each['name'], style)
                    worksheet.write(prod_row, prod_col+2, each['category'], style)
                    worksheet.write(prod_row, prod_col+3, each['costing_method'], style)
                    #worksheet.write(prod_row, prod_col+4, each['cost_price'], currency_format)
                    #
                    worksheet.write(prod_row, prod_col+4, each['price_beginning'], currency_format)
                    worksheet.write(prod_row, prod_col+5, each['beginning'], qty_format)
                    worksheet.write(prod_row, prod_col+6, each['value_beginning'], currency_format)
                    #
                    worksheet.write(prod_row, prod_col+7, 'Purchase', style)
                    worksheet.write(prod_row, prod_col+8, each['receipt_price'], currency_format)
                    worksheet.write(prod_row, prod_col+9, each['receipt_qty'], qty_format)
                    worksheet.write(prod_row, prod_col+10, each['receipt_value'], currency_format)

                    worksheet.write(prod_row+1, prod_col+7, 'Transfer', style)
                    worksheet.write(prod_row+1, prod_col+8, each['internal_in_price'], currency_format)
                    worksheet.write(prod_row+1, prod_col+9, each['internal_in_qty'], qty_format)
                    worksheet.write(prod_row+1, prod_col+10, each['internal_in_value'], currency_format)

                    worksheet.write(prod_row+2, prod_col+7, 'Landed Cost', style)
                    worksheet.write(prod_row+2, prod_col+8, each['landed_cost_price'], currency_format)
                    worksheet.write(prod_row+2, prod_col+9, each['landed_cost_qty'], qty_format)
                    worksheet.write(prod_row+2, prod_col+10, each['landed_cost_value'], currency_format)

                    worksheet.write(prod_row+3, prod_col+7, 'Price Adjustment', style)
                    worksheet.write(prod_row+3, prod_col+8, each['price_adj_price'], currency_format)
                    worksheet.write(prod_row+3, prod_col+9, each['price_adj_qty'], qty_format)
                    worksheet.write(prod_row+3, prod_col+10, each['price_adj_value'], currency_format)
                    #
                    worksheet.write(prod_row, prod_col+11, 'Sale', style)
                    worksheet.write(prod_row, prod_col+12, each['issue_price'], currency_format)
                    worksheet.write(prod_row, prod_col+13, each['issue_qty'], qty_format)
                    worksheet.write(prod_row, prod_col+14, each['issue_value'], currency_format)

                    worksheet.write(prod_row+1, prod_col+11, 'Transfer', style)
                    worksheet.write(prod_row+1, prod_col+12, each['internal_out_price'], currency_format)
                    worksheet.write(prod_row+1, prod_col+13, each['internal_out_qty'], qty_format)
                    worksheet.write(prod_row+1, prod_col+14, each['internal_out_value'], currency_format)

                    worksheet.write(prod_row+2, prod_col+11, 'Inv. Adjustment', style)
                    worksheet.write(prod_row+2, prod_col+12, each['adjustment_price'], currency_format)
                    worksheet.write(prod_row+2, prod_col+13, each['adjustment_qty'], qty_format)
                    worksheet.write(prod_row+2, prod_col+14, each['adjustment_value'], style)
                    #
                    worksheet.write(prod_row, prod_col+15, each['price_end'], currency_format)
                    worksheet.write(prod_row, prod_col+16, each['net_on_hand'], qty_format)
                    worksheet.write(prod_row, prod_col+17, each['total_value'], currency_format)
                    prod_row = prod_row + 4
                    
                prod_row = 8
                prod_col = 7
            self.fill_sheet(workbook)
            fp = io.BytesIO()
            workbook.save(fp)
            
            export_id = self.env['sale.day.book.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            res = {
                    'view_mode': 'form',
                    'res_id': export_id.id,
                    'res_model': 'sale.day.book.report.excel',
                    'type': 'ir.actions.act_window',
                    'target':'new'
                }
            return res
        else:
            raise Warning (""" You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")
            
    def fill_sheet(self, workbook):
        data  = { 'start_date': self.start_date,
         'end_date': self.end_date,'warehouse':self.warehouse,
         'category':self.category,
         'location_id':self.location_id,
         'company_id':self.company_id.name,
         'display_sum':self.display_sum,
        'currency':self.company_id.currency_id.name,
        'product_ids': self.product_ids,
        'filter_by' : self.filter_by
        }
        get_warehouse = self.get_warehouse()
        get_warehouse_name = self._get_warehouse_name()
        l1 = []
        get_company = self.get_company()
        get_currency = self.get_currency()
            
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
        worksheet = workbook.add_sheet('Returns')
        worksheet.write(5, 1, 'Start Date:', style_table_header)
        worksheet.write(6, 1, str(self.start_date))
        worksheet.write(5, 2, 'End Date', style_table_header)
        worksheet.write(6, 2, str(self.end_date))
        worksheet.write(5, 3, 'Company', style_table_header)
        worksheet.write(6, 3, get_company and get_company[0] or '',)
        worksheet.write(5, 4, 'Warehouse(s)', style_table_header)
        worksheet.write(5, 5, 'Currency', style_table_header)
        worksheet.write(6, 5, get_currency and get_currency[0] or '',)
        w_col_no = 7
        w_col_no1 = 8
        if get_warehouse_name:
               # w_col_no = w_col_no + 8
            worksheet.write(6, 4,get_warehouse_name, stylePC)
               # w_col_no1 = w_col_no1 + 9
        if self.display_sum:
            worksheet.write_merge(0, 1, 2, 9, "Inventory Valuation Report with Details", style=style_title)
            worksheet.write(8, 0, 'Default Code', style_table_header)
            worksheet.write(8, 1, 'Name', style_table_header_2)
            worksheet.write(8, 2, 'Category', style_table_header)
            worksheet.write(8, 3, 'Costing Method', style_table_header_2)
            #worksheet.write(8, 4, 'Cost', style_table_header)
            worksheet.write_merge(8, 8, 4, 6,'Beginning', style_table_header)
            worksheet.write_merge(8, 8, 7, 15,'Incoming', style_table_header_2)
            worksheet.write_merge(8, 8, 16, 25,'Outgoing', style_table_header)
            worksheet.write_merge(8, 8, 26, 28,'Ending', style_table_header_2)

            worksheet.write(9, 4, 'Cost', style_table_header)
            worksheet.write(9, 5, 'Qty', style_table_header)
            worksheet.write(9, 6, 'Value', style_table_header)

            worksheet.write(9, 7, 'Date', style_table_header_2)
            worksheet.write(9, 8, 'Description', style_table_header_2)
            worksheet.write(9, 9, 'Move Code', style_table_header_2)
            worksheet.write(9, 10, 'Stock Move', style_table_header_2)
            worksheet.write(9, 11, 'Journal Entry', style_table_header_2)
            worksheet.write(9, 12, 'Operation Type', style_table_header_2)
            worksheet.write(9, 13, 'Cost', style_table_header_2)
            worksheet.write(9, 14, 'Qty', style_table_header_2)
            worksheet.write(9, 15, 'Value', style_table_header_2)

            worksheet.write(9, 16, 'Date', style_table_header)
            worksheet.write(9, 17, 'Description', style_table_header)
            worksheet.write(9, 18, 'Move Code', style_table_header)
            worksheet.write(9, 19, 'Stock Move', style_table_header)
            worksheet.write(9, 20, 'Journal Entry', style_table_header)
            worksheet.write(9, 21, 'Operation Type', style_table_header)
            worksheet.write(9, 22, 'Cost', style_table_header)
            worksheet.write(9, 23, 'Qty', style_table_header)
            worksheet.write(9, 24, 'Value', style_table_header)
            worksheet.write(9, 25, 'Ref', style_table_header)

            worksheet.write(9, 26, 'Cost', style_table_header_2)
            worksheet.write(9, 27, 'Qty', style_table_header_2)
            worksheet.write(9, 28, 'Value', style_table_header_2)

            prod_row = 10
            prod_row_2 = 10
            prod_row_3 = 10
            prod_col = 0

            get_line = self.get_lines_details(data)
            #lines_receipt = get_line['lines_receipt']
            #lines_issue = get_line['lines_issue']
            for each in get_line:
                worksheet.write(prod_row, prod_col, each['sku'], style)
                worksheet.write(prod_row, prod_col+1, each['name'], style)
                worksheet.write(prod_row, prod_col+2, each['category'], style)
                worksheet.write(prod_row, prod_col+3, each['costing_method'], style)
                #worksheet.write(prod_row, prod_col+4, each['cost_price'], currency_format)
                #
                worksheet.write(prod_row, prod_col+4, each['price_beginning'], currency_format)
                worksheet.write(prod_row, prod_col+5, each['beginning'], qty_format)
                worksheet.write(prod_row, prod_col+6, each['value_beginning'], currency_format)
                #
                for line in each['return_receipt_lines']:
                    move_type = ''
                    if line.move_code == 'internal':
                        move_type = 'Transfer'
                    else:
                        move_type = dict(line._fields['move_code'].selection).get(line.move_code)
                    worksheet.write(prod_row_2, prod_col+7, line.create_date.strftime("%d/%m/%Y %H:%M:%S"), style)
                    worksheet.write(prod_row_2, prod_col+8, line.description, style)
                    worksheet.write(prod_row_2, prod_col+9, move_type, style)
                    worksheet.write(prod_row_2, prod_col+10, line.stock_move_id.display_name or '', style)
                    worksheet.write(prod_row_2, prod_col+11, line.account_move_id.display_name or '', style)
                    worksheet.write(prod_row_2, prod_col+12, line.picking_type_id.display_name or '', style)
                    worksheet.write(prod_row_2, prod_col+13, line.unit_cost, currency_format)
                    worksheet.write(prod_row_2, prod_col+14, line.quantity, qty_format)
                    worksheet.write(prod_row_2, prod_col+15, line.value, currency_format)
                    prod_row_2 = prod_row_2 + 1
                #
                for line in each['return_issue_lines']:
                    move_type = ''
                    if line.move_code == 'internal':
                        move_type = 'Transfer'
                    else:
                        move_type = dict(line._fields['move_code'].selection).get(line.move_code)
                    worksheet.write(prod_row_3, prod_col+16, line.create_date.strftime("%d/%m/%Y %H:%M:%S"), style)
                    worksheet.write(prod_row_3, prod_col+17, line.description, style)
                    worksheet.write(prod_row_3, prod_col+18, move_type, style)
                    worksheet.write(prod_row_3, prod_col+19, line.stock_move_id.display_name or '', style)
                    worksheet.write(prod_row_3, prod_col+20, line.account_move_id.display_name or '', style)
                    worksheet.write(prod_row_3, prod_col+21, line.picking_type_id.display_name or '', style)
                    worksheet.write(prod_row_3, prod_col+22, line.unit_cost, currency_format)
                    worksheet.write(prod_row_3, prod_col+23, line.quantity, qty_format)
                    worksheet.write(prod_row_3, prod_col+24, line.value, currency_format)
                    worksheet.write(prod_row_3, prod_col+25, line.ref_invoices or '', style)
                    prod_row_3 = prod_row_3 + 1

                worksheet.write(prod_row, prod_col+26, each['price_end'], currency_format)
                worksheet.write(prod_row, prod_col+27, each['net_on_hand'], qty_format)
                worksheet.write(prod_row, prod_col+28, each['total_value'], currency_format)

                if prod_row_2 > prod_row_3:
                    prod_row = prod_row_2
                else:
                    prod_row = prod_row_3

                prod_row += 1
                prod_row_2 = prod_row
                prod_row_3 = prod_row

            prod_row = 8
            prod_col = 7
        else:
            worksheet.write_merge(0, 1, 2, 9, "Inventory Valuation Report", style=style_title)
            worksheet.write(8, 0, 'Default Code', style_table_header)
            worksheet.write(8, 1, 'Name', style_table_header_2)
            worksheet.write(8, 2, 'Category', style_table_header)
            worksheet.write(8, 3, 'Costing Method', style_table_header_2)
            #worksheet.write(8, 4, 'Cost', style_table_header)
            worksheet.write_merge(8, 8, 4, 6,'Beginning', style_table_header)
            worksheet.write_merge(8, 8, 7, 10,'Incoming', style_table_header_2)
            worksheet.write_merge(8, 8, 11, 14,'Outgoing', style_table_header)
            worksheet.write_merge(8, 8, 15, 17,'Ending', style_table_header_2)

            worksheet.write(9, 4, 'Cost', style_table_header)
            worksheet.write(9, 5, 'Qty', style_table_header)
            worksheet.write(9, 6, 'Value', style_table_header)

            worksheet.write(9, 7, 'Type', style_table_header_2)
            worksheet.write(9, 8, 'Cost', style_table_header_2)
            worksheet.write(9, 9, 'Qty', style_table_header_2)
            worksheet.write(9, 10, 'Value', style_table_header_2)

            worksheet.write(9, 11, 'Type', style_table_header)
            worksheet.write(9, 12, 'Cost', style_table_header)
            worksheet.write(9, 13, 'Qty', style_table_header)
            worksheet.write(9, 14, 'Value', style_table_header)

            worksheet.write(9, 15, 'Cost', style_table_header_2)
            worksheet.write(9, 16, 'Qty', style_table_header_2)
            worksheet.write(9, 17, 'Value', style_table_header_2)

            prod_row = 10
            prod_col = 0

            get_line = self.get_lines(data)
            for each in get_line:
                worksheet.write(prod_row, prod_col, each['sku'], style)
                worksheet.write(prod_row, prod_col+1, each['name'], style)
                worksheet.write(prod_row, prod_col+2, each['category'], style)
                worksheet.write(prod_row, prod_col+3, each['costing_method'], style)
                #worksheet.write(prod_row, prod_col+4, each['cost_price'], currency_format)
                #
                worksheet.write(prod_row, prod_col+4, each['price_beginning'], currency_format)
                worksheet.write(prod_row, prod_col+5, each['beginning'], qty_format)
                worksheet.write(prod_row, prod_col+6, each['value_beginning'], currency_format)
                #
                worksheet.write(prod_row, prod_col+7, 'Purchase', style)
                worksheet.write(prod_row, prod_col+8, each['receipt_price'], currency_format)
                worksheet.write(prod_row, prod_col+9, each['receipt_qty'], qty_format)
                worksheet.write(prod_row, prod_col+10, each['receipt_value'], currency_format)

                worksheet.write(prod_row+1, prod_col+7, 'Transfer', style)
                worksheet.write(prod_row+1, prod_col+8, each['internal_in_price'], currency_format)
                worksheet.write(prod_row+1, prod_col+9, each['internal_in_qty'], qty_format)
                worksheet.write(prod_row+1, prod_col+10, each['internal_in_value'], currency_format)

                worksheet.write(prod_row+2, prod_col+7, 'Landed Cost', style)
                worksheet.write(prod_row+2, prod_col+8, each['landed_cost_price'], currency_format)
                worksheet.write(prod_row+2, prod_col+9, each['landed_cost_qty'], qty_format)
                worksheet.write(prod_row+2, prod_col+10, each['landed_cost_value'], currency_format)

                worksheet.write(prod_row+3, prod_col+7, 'Price Adjustment', style)
                worksheet.write(prod_row+3, prod_col+8, each['price_adj_price'], currency_format)
                worksheet.write(prod_row+3, prod_col+9, each['price_adj_qty'], qty_format)
                worksheet.write(prod_row+3, prod_col+10, each['price_adj_value'], currency_format)
                #
                worksheet.write(prod_row, prod_col+11, 'Sale', style)
                worksheet.write(prod_row, prod_col+12, each['issue_price'], currency_format)
                worksheet.write(prod_row, prod_col+13, each['issue_qty'], qty_format)
                worksheet.write(prod_row, prod_col+14, each['issue_value'], currency_format)

                worksheet.write(prod_row+1, prod_col+11, 'Transfer', style)
                worksheet.write(prod_row+1, prod_col+12, each['internal_out_price'], currency_format)
                worksheet.write(prod_row+1, prod_col+13, each['internal_out_qty'], qty_format)
                worksheet.write(prod_row+1, prod_col+14, each['internal_out_value'], currency_format)

                worksheet.write(prod_row+2, prod_col+11, 'Inv. Adjustment', style)
                worksheet.write(prod_row+2, prod_col+12, each['adjustment_price'], currency_format)
                worksheet.write(prod_row+2, prod_col+13, each['adjustment_qty'], qty_format)
                worksheet.write(prod_row+2, prod_col+14, each['adjustment_value'], style)
                #
                worksheet.write(prod_row, prod_col+15, each['price_end'], currency_format)
                worksheet.write(prod_row, prod_col+16, each['net_on_hand'], qty_format)
                worksheet.write(prod_row, prod_col+17, each['total_value'], currency_format)
                prod_row = prod_row + 4

            prod_row = 8
            prod_col = 7

    def get_lines(self, data):
        product_res = self.env['product.product'].search([('qty_available', '!=', 0),('type', '=', 'product')])
        category_lst = []
        if data['category'] :

            for cate in data['category'] and data['filter_by'] == 'categ':
                if cate.id not in category_lst :
                    category_lst.append(cate.id)
                    
                for child in  cate.child_id :
                    if child.id not in category_lst :
                        category_lst.append(child.id)
        
        if len(category_lst) > 0 :

            product_res = self.env['product.product'].search([('categ_id','in',category_lst),('qty_available', '!=', 0),('type', '=', 'product')])
            
        if data['product_ids'] and data['filter_by'] == 'product':
            product_res = data['product_ids']

        lines = []
        for product in  product_res :

            

            #if product.create_date.date() <= data['start_date'] :
                

            sales_value = 0.0

            incoming = 0.0
            opening = self._compute_quantities_product_quant_dic(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'),False,data['start_date'],product,data)

            



            #ending = self._compute_quantities_product_quant_dic(False,data['end_date'],product,data)

            #if opening[product.id]['qty_available'] > 0 :

            
            custom_domain = []
            if data['company_id']:
                obj = self.env['res.company'].search([('name', '=', data['company_id'])])
                
                custom_domain.append(('company_id','=',obj.id))


            if data['warehouse'] :
                warehouse_lst = [a.id for a in data['warehouse']]
                custom_domain.append(('picking_id.picking_type_id.warehouse_id','in',warehouse_lst))

            
            stock_move_line = self.env['stock.move'].search([
                ('product_id','=',product.id),
                ('picking_id.date_done','>',data['start_date']),
                ('picking_id.date_done',"<=",data['end_date']),
                ('state','=','done')
                ] + custom_domain)


            for move in stock_move_line :
                if move.picking_id.picking_type_id.code == "outgoing" :
                    if data['location_id'] :
                        locations_lst = [data['location_id'].id]
                        for i in data['location_id'].child_ids :
                            locations_lst.append(i.id)
                        if move.location_id.id in locations_lst :
                            sales_value = sales_value + move.product_uom_qty

                    else :

                        sales_value = sales_value + move.product_uom_qty


                if move.picking_id.picking_type_id.code == "incoming" :
                    if data['location_id'] :
                        locations_lst = [data['location_id'].id]
                        for i in data['location_id'].child_ids :
                            locations_lst.append(i.id)
                        if move.location_dest_id.id in locations_lst :
                            incoming = incoming + move.product_uom_qty


                    else :


                        incoming = incoming + move.product_uom_qty
            ### Beg
            stock_val_layer_beg = self.env['stock.valuation.layer'].search([
                    ('product_id','=',product.id),
                    ('create_date',"<",data['start_date']),
                    ], order='create_date desc')
            qty_beginning = sum(stock_val_layer_beg.mapped('quantity'))
            value_beginning = sum(stock_val_layer_beg.mapped('value'))
            price_beginning = 0
            if qty_beginning != 0:
                price_beginning = value_beginning / qty_beginning
            ###
            
            stock_val_layer = self.env['stock.valuation.layer'].search([
                    ('product_id','=',product.id),
                    ('create_date','>=',data['start_date']),
                    ('create_date',"<=",data['end_date']),
                    ], order='create_date desc')
            #
            issues = stock_val_layer.filtered(lambda item: item.move_code == 'outgoing')
            issue_qty = abs(sum(issues.mapped('quantity')))
            issue_value = abs(sum(issues.mapped('value')))
            issue_price = 0
            if issue_qty != 0:
                issue_price = issue_value / issue_qty
            #
            receipts = stock_val_layer.filtered(lambda item: item.move_code == 'incoming')
            receipt_qty = abs(sum(receipts.mapped('quantity')))
            receipt_value = abs(sum(receipts.mapped('value')))
            receipt_price = 0
            if receipt_qty != 0:
                receipt_price = receipt_value / receipt_qty
            #
            adjustments = stock_val_layer.filtered(lambda item: item.move_code == 'adjustment')
            adjustment_qty = abs(sum(adjustments.mapped('quantity')))
            adjustment_value = abs(sum(adjustments.mapped('value')))
            adjustment_price = 0
            if adjustment_qty != 0:
                adjustment_price = adjustment_value / adjustment_qty
            #
            landed_costs = stock_val_layer.filtered(lambda item: item.move_code == 'landed_cost')
            landed_cost_qty = abs(sum(landed_costs.mapped('quantity')))
            landed_cost_value = abs(sum(landed_costs.mapped('value')))
            landed_cost_price = 0
            if landed_cost_qty != 0:
                landed_cost_price = landed_cost_value / landed_cost_qty
            #
            price_adjs = stock_val_layer.filtered(lambda item: item.move_code == 'price_adj')
            price_adj_qty = abs(sum(price_adjs.mapped('quantity')))
            price_adj_value = abs(sum(price_adjs.mapped('value')))
            price_adj_price = 0
            if price_adj_qty != 0:
                price_adj_price = price_adj_value / price_adj_qty
            #
            internal_tranfs = stock_val_layer.filtered(lambda item: item.move_code == 'internal')
            #
            internal_out = stock_val_layer.filtered(lambda item: item.internal_transfer_type == 'internal_out')
            internal_out_qty = abs(sum(internal_out.mapped('quantity')))
            internal_out_value = abs(sum(internal_out.mapped('value')))
            internal_out_price = 0
            if internal_out_qty != 0:
                internal_out_price = internal_out_value / internal_out_qty
            #
            internal_in = stock_val_layer.filtered(lambda item: item.internal_transfer_type == 'internal_in')
            internal_in_qty = abs(sum(internal_in.mapped('quantity')))
            internal_in_value = abs(sum(internal_in.mapped('value')))
            internal_in_price = 0
            if internal_in_qty != 0:
                internal_in_price = internal_in_value / internal_in_qty
            ### End
            stock_val_layer_end = self.env['stock.valuation.layer'].search([
                    ('product_id','=',product.id),
                    ('create_date',"<=",data['end_date']),
                    ], order='create_date desc')
            qty_end = sum(stock_val_layer_end.mapped('quantity'))
            value_end = sum(stock_val_layer_end.mapped('value'))
            price_end = 0
            if qty_end != 0:
                price_end = value_end / qty_end
            ###

            cost = 0
            count = 0
            for layer in stock_val_layer : 
                if layer.stock_move_id.picking_id.picking_type_id.code == "incoming" :
                    cost = cost + layer.unit_cost
                    count = count + 1

                if not layer.stock_move_id.picking_id :
                    cost = cost + layer.unit_cost
                    count = count + 1
            size_layer = len(stock_val_layer)
            stock_layer_values = stock_val_layer.mapped('value')
            total_value = sum(stock_layer_values)
            avg_cost = 0
            if count > 0 :
                avg_cost = cost / count

            if not stock_val_layer and  avg_cost == 0:
                avg_cost = product.standard_price 

            inventory_domain = [
                ('date','>',data['start_date']),
                ('date',"<",data['end_date'])
                ]
            stock_pick_lines = self.env['stock.move'].search([('location_id.usage', '=', 'inventory'),('product_id.id','=',product.id)] + inventory_domain)
            stock_internal_lines = self.env['stock.move'].search([('location_id.usage', '=', 'internal'),('location_dest_id.usage', '=', 'internal'),('product_id.id','=',product.id)] + inventory_domain)
            stock_internal_lines_2 = self.env['stock.move'].search([('location_id.usage', '=', 'internal'),('location_dest_id.usage', '=', 'inventory'),('product_id.id','=',product.id)] + inventory_domain)
            adjust = 0
            internal = 0
            plus_picking = 0
            
            if stock_pick_lines:
                for invent in stock_pick_lines:
                    
                    adjust = invent.product_uom_qty
                    plus_picking = invent.id
            
            
            min_picking = 0
            if stock_internal_lines_2 :
                for inter in stock_internal_lines_2:
                    
                    plus_min = inter.product_uom_qty
                    min_picking = inter.id

                    

            
            if plus_picking > min_picking :
                picking_id = self.env['stock.move'].browse(plus_picking)
                adjust = picking_id.product_uom_qty

            else :
                picking_id = self.env['stock.move'].browse(min_picking)
                adjust = -int(picking_id.product_uom_qty)
            if stock_internal_lines:

                for inter in stock_internal_lines:
                    
                    internal = inter.product_uom_qty

            
            _logger.info("===> opening[product.id]['qty_available']: " + str(opening[product.id]['qty_available']))
            ending_bal = opening[product.id]['qty_available'] - sales_value + incoming + adjust
            #raise Warning("TESTING")
            method = ''
            price_used = product.standard_price
            if product.categ_id.property_cost_method == 'average' :
                method = 'Average Cost (AVCO)'
                price_used = avg_cost 

            elif product.categ_id.property_cost_method == 'standard' :
                method = 'Standard Price'
                price_used = product.standard_price


            vals = {
                    'sku': product.default_code or '',
                    'name': product.name or '',
                    'category': product.categ_id.name or '' ,
                    'cost_price': price_used or 0,
                    'costing_method' : method,
                    'available':  0 ,
                    'virtual':   0,
                    'incoming': incoming or 0,
                    'outgoing':  adjust,
                    #
                    'receipt_price': receipt_price,
                    'receipt_qty': receipt_qty,
                    'receipt_value': receipt_value,
                    'internal_in_price': internal_in_price,
                    'internal_in_qty': internal_in_qty,
                    'internal_in_value': internal_in_value,
                    'landed_cost_price': landed_cost_price,
                    'landed_cost_qty': landed_cost_qty,
                    'landed_cost_value': landed_cost_value,
                    'price_adj_price': price_adj_price,
                    'price_adj_qty': price_adj_qty,
                    'price_adj_value': price_adj_value,
                    #
                    'issue_price': issue_price,
                    'issue_qty': issue_qty,
                    'issue_value': issue_value,
                    'internal_out_price': internal_out_price,
                    'internal_out_qty': internal_out_qty,
                    'internal_out_value': internal_out_value,
                    'adjustment_price': adjustment_price,
                    'adjustment_qty': adjustment_qty,
                    'adjustment_value': adjustment_value,
                    #
                    'price_beginning': price_beginning,
                    'beginning': qty_beginning,
                    'value_beginning': value_beginning,
                    #
                    'price_end': price_end,
                    'net_on_hand':   qty_end,
                    'total_value': value_end
                }
            lines.append(vals)
            
        return lines

    def get_lines_details(self, data):
        product_res = self.env['product.product'].search([('qty_available', '!=', 0),('type', '=', 'product')])
        category_lst = []
        if data['category'] :

            for cate in data['category'] and data['filter_by'] == 'categ':
                if cate.id not in category_lst :
                    category_lst.append(cate.id)
                    
                for child in  cate.child_id :
                    if child.id not in category_lst :
                        category_lst.append(child.id)
        
        if len(category_lst) > 0 :

            product_res = self.env['product.product'].search([('categ_id','in',category_lst),('qty_available', '!=', 0),('type', '=', 'product')])
            
        if data['product_ids'] and data['filter_by'] == 'product':
            product_res = data['product_ids']

        lines = []
        for product in product_res:
            sales_value = 0.0
            incoming = 0.0

            opening = self._compute_quantities_product_quant_dic(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'),False,data['start_date'],product,data)

            custom_domain = []
            if data['company_id']:
                obj = self.env['res.company'].search([('name', '=', data['company_id'])])
                
                custom_domain.append(('company_id','=',obj.id))


            if data['warehouse'] :
                warehouse_lst = [a.id for a in data['warehouse']]
                custom_domain.append(('picking_id.picking_type_id.warehouse_id','in',warehouse_lst))

            
            stock_move_line = self.env['stock.move'].search([
                ('product_id','=',product.id),
                ('picking_id.date_done','>',data['start_date']),
                ('picking_id.date_done',"<=",data['end_date']),
                ('state','=','done')
                ] + custom_domain)


            for move in stock_move_line :
                if move.picking_id.picking_type_id.code == "outgoing" :
                    if data['location_id'] :
                        locations_lst = [data['location_id'].id]
                        for i in data['location_id'].child_ids :
                            locations_lst.append(i.id)
                        if move.location_id.id in locations_lst :
                            sales_value = sales_value + move.product_uom_qty

                    else :

                        sales_value = sales_value + move.product_uom_qty


                if move.picking_id.picking_type_id.code == "incoming" :
                    if data['location_id'] :
                        locations_lst = [data['location_id'].id]
                        for i in data['location_id'].child_ids :
                            locations_lst.append(i.id)
                        if move.location_dest_id.id in locations_lst :
                            incoming = incoming + move.product_uom_qty


                    else :


                        incoming = incoming + move.product_uom_qty
            ### Beg
            stock_val_layer_beg = self.env['stock.valuation.layer'].search([
                    ('product_id','=',product.id),
                    ('create_date',"<",data['start_date']),
                    ], order='create_date desc')
            qty_beginning = sum(stock_val_layer_beg.mapped('quantity'))
            value_beginning = sum(stock_val_layer_beg.mapped('value'))
            price_beginning = 0
            if qty_beginning != 0:
                price_beginning = value_beginning / qty_beginning
            ###
            stock_val_layer = self.env['stock.valuation.layer'].search([
                    ('product_id','=',product.id),
                    ('create_date','>=',data['start_date']),
                    ('create_date',"<=",data['end_date']),
                    ], order='create_date desc')
            #
            issues = stock_val_layer.filtered(lambda item: item.move_code == 'outgoing')
            issues_w_pickings = issues.filtered(lambda l: l.picking_id.origin != False)
            return_issue_lines = issues_w_pickings.filtered(lambda l: 'Return' in l.picking_id.origin)
            picking_names = return_issue_lines.mapped('picking_id.origin')
            picking_names = list(filter(lambda l: 'Return' in l, picking_names))
            p_names = []
            for p in picking_names:
                p_names.append(p.split(' ')[-1])
            internal_out = stock_val_layer.filtered(lambda item: item.internal_transfer_type == 'internal_out')
            adjustments = stock_val_layer.filtered(lambda item: item.move_code == 'adjustment')
            lines_issue = internal_out + issues + adjustments - return_issue_lines
            lines_issue.sorted(key=lambda r: r.create_date)
            _logger.info("===> total outgoings: " + str(internal_out + issues + adjustments))
            _logger.info("===> total return_issue_lines: " + str(return_issue_lines))
            #
            receipts = stock_val_layer.filtered(lambda item: item.move_code == 'incoming')
            return_receipt_lines = receipts.filtered(lambda l: l.picking_id.name in p_names)
            internal_in = stock_val_layer.filtered(lambda item: item.internal_transfer_type == 'internal_in')
            landed_costs = stock_val_layer.filtered(lambda item: item.move_code == 'landed_cost')
            price_adjs = stock_val_layer.filtered(lambda item: item.move_code == 'price_adj')
            lines_receipt = internal_in + receipts + landed_costs + price_adjs - return_receipt_lines
            lines_receipt.sorted(key=lambda r: r.create_date)
            
            #
            internal_tranfs = stock_val_layer.filtered(lambda item: item.move_code == 'internal')
            #
            #
            ### End
            stock_val_layer_end = self.env['stock.valuation.layer'].search([
                    ('product_id','=',product.id),
                    ('create_date',"<=",data['end_date']),
                    ], order='create_date desc')
            qty_end = sum(stock_val_layer_end.mapped('quantity'))
            value_end = sum(stock_val_layer_end.mapped('value'))
            price_end = 0
            if qty_end != 0:
                price_end = value_end / qty_end
            ###

            cost = 0
            count = 0
            for layer in stock_val_layer : 
                if layer.stock_move_id.picking_id.picking_type_id.code == "incoming" :
                    cost = cost + layer.unit_cost
                    count = count + 1

                if not layer.stock_move_id.picking_id :
                    cost = cost + layer.unit_cost
                    count = count + 1
            size_layer = len(stock_val_layer)
            stock_layer_values = stock_val_layer.mapped('value')
            total_value = sum(stock_layer_values)
            avg_cost = 0
            if count > 0 :
                avg_cost = cost / count

            if not stock_val_layer and  avg_cost == 0:
                avg_cost = product.standard_price 

            inventory_domain = [
                ('date','>',data['start_date']),
                ('date',"<",data['end_date'])
                ]
            stock_pick_lines = self.env['stock.move'].search([('location_id.usage', '=', 'inventory'),('product_id.id','=',product.id)] + inventory_domain)
            stock_internal_lines = self.env['stock.move'].search([('location_id.usage', '=', 'internal'),('location_dest_id.usage', '=', 'internal'),('product_id.id','=',product.id)] + inventory_domain)
            stock_internal_lines_2 = self.env['stock.move'].search([('location_id.usage', '=', 'internal'),('location_dest_id.usage', '=', 'inventory'),('product_id.id','=',product.id)] + inventory_domain)
            adjust = 0
            internal = 0
            plus_picking = 0
            
            if stock_pick_lines:
                for invent in stock_pick_lines:
                    
                    adjust = invent.product_uom_qty
                    plus_picking = invent.id
            
            
            min_picking = 0
            if stock_internal_lines_2 :
                for inter in stock_internal_lines_2:
                    
                    plus_min = inter.product_uom_qty
                    min_picking = inter.id

                    

            
            if plus_picking > min_picking :
                picking_id = self.env['stock.move'].browse(plus_picking)
                adjust = picking_id.product_uom_qty

            else :
                picking_id = self.env['stock.move'].browse(min_picking)
                adjust = -int(picking_id.product_uom_qty)
            if stock_internal_lines:

                for inter in stock_internal_lines:
                    
                    internal = inter.product_uom_qty

            
            ending_bal = opening[product.id]['qty_available'] - sales_value + incoming + adjust
            #raise Warning("TESTING")
            method = ''
            price_used = product.standard_price
            if product.categ_id.property_cost_method == 'average' :
                method = 'Average Cost (AVCO)'
                price_used = avg_cost 

            elif product.categ_id.property_cost_method == 'standard' :
                method = 'Standard Price'
                price_used = product.standard_price


            vals = {
                    'sku': product.default_code or '',
                    'name': product.name or '',
                    'category': product.categ_id.name or '' ,
                    'cost_price': price_used or 0,
                    'costing_method' : method,
                    'available':  0 ,
                    'virtual':   0,
                    'incoming': incoming or 0,
                    'outgoing':  adjust,
                    #
                    'lines_receipt': lines_receipt,
                    'return_receipt_lines': return_receipt_lines,
                    #
                    'lines_issue': lines_issue,
                    'return_issue_lines': return_issue_lines,
                    #
                    'price_beginning': price_beginning,
                    'beginning': qty_beginning,
                    'value_beginning': value_beginning,
                    #
                    'price_end': price_end,
                    'net_on_hand':   qty_end,
                    'total_value': value_end
                }
            lines.append(vals)
            
        return lines

    def _compute_quantities_product_quant_dic(self,lot_id, owner_id, package_id,from_date,to_date,product_obj,data):
        
        loc_list = []
        
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations()
        custom_domain = []
        if data['company_id']:
            obj = self.env['res.company'].search([('name', '=', data['company_id'])])
            
            custom_domain.append(('company_id','=',obj.id))

        if data['location_id'] :
            custom_domain.append(('location_id','=',data['location_id'].id))

        if data['warehouse'] :
            ware_check_domain = [a.id for a in data['warehouse']]
            locations = []
            for i in ware_check_domain:
                
                loc_ids = self.env['stock.warehouse'].search([('id','=',i)])
                
                locations.append(loc_ids.view_location_id.id)
                for i in loc_ids.view_location_id.child_ids :
                  locations.append(i.id)

                
               
                loc_list.append(loc_ids.lot_stock_id.id)

                
            custom_domain.append(('location_id','in',locations))

        domain_quant = [('product_id', 'in', product_obj.ids)] + domain_quant_loc + custom_domain
        #print ("dddddddddddddddddddddddddddddddddddddddddd",domain_quant)
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        #to_date = fields.Datetime.to_datetime(to_date)
        
        if to_date and to_date < date.today():

            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', product_obj.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', product_obj.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        #moves_in_res_ids = dict((item['product_id'][0], item['account_move_ids']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty', 'account_move_ids'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'value'], ['product_id'], orderby='id'))
        quants_values = dict((item['product_id'][0], item['value']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'value'], ['product_id'], orderby='id'))

        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in product_obj.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, 0.0)
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)
            res[product_id]['value'] = quants_values.get(product_id, 0.0)
 
        
        return res