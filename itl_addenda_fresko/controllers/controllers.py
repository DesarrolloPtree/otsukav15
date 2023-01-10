# -*- coding: utf-8 -*-
# from odoo import http


# class ItlAddendaFresko(http.Controller):
#     @http.route('/itl_addenda_fresko/itl_addenda_fresko/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_addenda_fresko/itl_addenda_fresko/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_addenda_fresko.listing', {
#             'root': '/itl_addenda_fresko/itl_addenda_fresko',
#             'objects': http.request.env['itl_addenda_fresko.itl_addenda_fresko'].search([]),
#         })

#     @http.route('/itl_addenda_fresko/itl_addenda_fresko/objects/<model("itl_addenda_fresko.itl_addenda_fresko"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_addenda_fresko.object', {
#             'object': obj
#         })
