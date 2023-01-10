# -*- coding: utf-8 -*-
# from odoo import http


# class ItlDayArReport(http.Controller):
#     @http.route('/itl_day_ar_report/itl_day_ar_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_day_ar_report/itl_day_ar_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_day_ar_report.listing', {
#             'root': '/itl_day_ar_report/itl_day_ar_report',
#             'objects': http.request.env['itl_day_ar_report.itl_day_ar_report'].search([]),
#         })

#     @http.route('/itl_day_ar_report/itl_day_ar_report/objects/<model("itl_day_ar_report.itl_day_ar_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_day_ar_report.object', {
#             'object': obj
#         })
