# -*- coding: utf-8 -*-
# from odoo import http


# class ItlShippingPolicy(http.Controller):
#     @http.route('/itl_shipping_policy/itl_shipping_policy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_shipping_policy/itl_shipping_policy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_shipping_policy.listing', {
#             'root': '/itl_shipping_policy/itl_shipping_policy',
#             'objects': http.request.env['itl_shipping_policy.itl_shipping_policy'].search([]),
#         })

#     @http.route('/itl_shipping_policy/itl_shipping_policy/objects/<model("itl_shipping_policy.itl_shipping_policy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_shipping_policy.object', {
#             'object': obj
#         })
