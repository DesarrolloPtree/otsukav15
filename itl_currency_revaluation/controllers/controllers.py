# -*- coding: utf-8 -*-
# from odoo import http


# class ItlCurrencyRevaluation(http.Controller):
#     @http.route('/itl_currency_revaluation/itl_currency_revaluation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_currency_revaluation/itl_currency_revaluation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_currency_revaluation.listing', {
#             'root': '/itl_currency_revaluation/itl_currency_revaluation',
#             'objects': http.request.env['itl_currency_revaluation.itl_currency_revaluation'].search([]),
#         })

#     @http.route('/itl_currency_revaluation/itl_currency_revaluation/objects/<model("itl_currency_revaluation.itl_currency_revaluation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_currency_revaluation.object', {
#             'object': obj
#         })
