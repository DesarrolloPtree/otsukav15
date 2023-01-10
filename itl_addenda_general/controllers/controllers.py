# -*- coding: utf-8 -*-
# from odoo import http


# class ItlAddendaGeneral(http.Controller):
#     @http.route('/itl_addenda_general/itl_addenda_general/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_addenda_general/itl_addenda_general/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_addenda_general.listing', {
#             'root': '/itl_addenda_general/itl_addenda_general',
#             'objects': http.request.env['itl_addenda_general.itl_addenda_general'].search([]),
#         })

#     @http.route('/itl_addenda_general/itl_addenda_general/objects/<model("itl_addenda_general.itl_addenda_general"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_addenda_general.object', {
#             'object': obj
#         })
