# -*- coding: utf-8 -*-
# from odoo import http


# class ItlBatchCustomerPayment(http.Controller):
#     @http.route('/itl_batch_customer_payment/itl_batch_customer_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_batch_customer_payment/itl_batch_customer_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_batch_customer_payment.listing', {
#             'root': '/itl_batch_customer_payment/itl_batch_customer_payment',
#             'objects': http.request.env['itl_batch_customer_payment.itl_batch_customer_payment'].search([]),
#         })

#     @http.route('/itl_batch_customer_payment/itl_batch_customer_payment/objects/<model("itl_batch_customer_payment.itl_batch_customer_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_batch_customer_payment.object', {
#             'object': obj
#         })
