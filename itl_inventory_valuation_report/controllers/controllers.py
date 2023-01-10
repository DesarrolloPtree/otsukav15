# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInventoryValuationReport(http.Controller):
#     @http.route('/itl_inventory_valuation_report/itl_inventory_valuation_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_inventory_valuation_report/itl_inventory_valuation_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_inventory_valuation_report.listing', {
#             'root': '/itl_inventory_valuation_report/itl_inventory_valuation_report',
#             'objects': http.request.env['itl_inventory_valuation_report.itl_inventory_valuation_report'].search([]),
#         })

#     @http.route('/itl_inventory_valuation_report/itl_inventory_valuation_report/objects/<model("itl_inventory_valuation_report.itl_inventory_valuation_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_inventory_valuation_report.object', {
#             'object': obj
#         })
