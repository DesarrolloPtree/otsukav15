# -*- coding: utf-8 -*-
# from odoo import http


# class ItlRmeOrder(http.Controller):
#     @http.route('/itl_rme_order/itl_rme_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_rme_order/itl_rme_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_rme_order.listing', {
#             'root': '/itl_rme_order/itl_rme_order',
#             'objects': http.request.env['itl_rme_order.itl_rme_order'].search([]),
#         })

#     @http.route('/itl_rme_order/itl_rme_order/objects/<model("itl_rme_order.itl_rme_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_rme_order.object', {
#             'object': obj
#         })
