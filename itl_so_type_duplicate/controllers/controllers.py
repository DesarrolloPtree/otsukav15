# -*- coding: utf-8 -*-
# from odoo import http


# class ItlSoTypeDuplicate(http.Controller):
#     @http.route('/itl_so_type_duplicate/itl_so_type_duplicate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_so_type_duplicate/itl_so_type_duplicate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_so_type_duplicate.listing', {
#             'root': '/itl_so_type_duplicate/itl_so_type_duplicate',
#             'objects': http.request.env['itl_so_type_duplicate.itl_so_type_duplicate'].search([]),
#         })

#     @http.route('/itl_so_type_duplicate/itl_so_type_duplicate/objects/<model("itl_so_type_duplicate.itl_so_type_duplicate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_so_type_duplicate.object', {
#             'object': obj
#         })
