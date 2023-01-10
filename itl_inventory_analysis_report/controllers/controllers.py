# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInventoryAnalysisReport(http.Controller):
#     @http.route('/itl_inventory_analysis_report/itl_inventory_analysis_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_inventory_analysis_report/itl_inventory_analysis_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_inventory_analysis_report.listing', {
#             'root': '/itl_inventory_analysis_report/itl_inventory_analysis_report',
#             'objects': http.request.env['itl_inventory_analysis_report.itl_inventory_analysis_report'].search([]),
#         })

#     @http.route('/itl_inventory_analysis_report/itl_inventory_analysis_report/objects/<model("itl_inventory_analysis_report.itl_inventory_analysis_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_inventory_analysis_report.object', {
#             'object': obj
#         })
