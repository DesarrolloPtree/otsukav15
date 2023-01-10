# -*- coding: utf-8 -*-
# from odoo import http


# class ItlUomForProduct(http.Controller):
#     @http.route('/itl_uom_for_product/itl_uom_for_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_uom_for_product/itl_uom_for_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_uom_for_product.listing', {
#             'root': '/itl_uom_for_product/itl_uom_for_product',
#             'objects': http.request.env['itl_uom_for_product.itl_uom_for_product'].search([]),
#         })

#     @http.route('/itl_uom_for_product/itl_uom_for_product/objects/<model("itl_uom_for_product.itl_uom_for_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_uom_for_product.object', {
#             'object': obj
#         })
