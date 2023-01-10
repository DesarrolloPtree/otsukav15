# -*- coding: utf-8 -*-
# from odoo import http


# class ItlDiscountAccount(http.Controller):
#     @http.route('/itl_discount_account/itl_discount_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_discount_account/itl_discount_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_discount_account.listing', {
#             'root': '/itl_discount_account/itl_discount_account',
#             'objects': http.request.env['itl_discount_account.itl_discount_account'].search([]),
#         })

#     @http.route('/itl_discount_account/itl_discount_account/objects/<model("itl_discount_account.itl_discount_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_discount_account.object', {
#             'object': obj
#         })
