# -*- coding: utf-8 -*-
# from odoo import http


# class ItlAddendaSoriana(http.Controller):
#     @http.route('/itl_addenda_soriana/itl_addenda_soriana/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_addenda_soriana/itl_addenda_soriana/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_addenda_soriana.listing', {
#             'root': '/itl_addenda_soriana/itl_addenda_soriana',
#             'objects': http.request.env['itl_addenda_soriana.itl_addenda_soriana'].search([]),
#         })

#     @http.route('/itl_addenda_soriana/itl_addenda_soriana/objects/<model("itl_addenda_soriana.itl_addenda_soriana"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_addenda_soriana.object', {
#             'object': obj
#         })
