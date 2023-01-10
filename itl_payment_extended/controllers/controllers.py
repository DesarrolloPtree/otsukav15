# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPaymentExtended(http.Controller):
#     @http.route('/itl_payment_extended/itl_payment_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_payment_extended/itl_payment_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_payment_extended.listing', {
#             'root': '/itl_payment_extended/itl_payment_extended',
#             'objects': http.request.env['itl_payment_extended.itl_payment_extended'].search([]),
#         })

#     @http.route('/itl_payment_extended/itl_payment_extended/objects/<model("itl_payment_extended.itl_payment_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_payment_extended.object', {
#             'object': obj
#         })
