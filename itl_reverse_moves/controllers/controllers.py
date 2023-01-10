# -*- coding: utf-8 -*-
# from odoo import http


# class ItlReverseMoves(http.Controller):
#     @http.route('/itl_reverse_moves/itl_reverse_moves/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_reverse_moves/itl_reverse_moves/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_reverse_moves.listing', {
#             'root': '/itl_reverse_moves/itl_reverse_moves',
#             'objects': http.request.env['itl_reverse_moves.itl_reverse_moves'].search([]),
#         })

#     @http.route('/itl_reverse_moves/itl_reverse_moves/objects/<model("itl_reverse_moves.itl_reverse_moves"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_reverse_moves.object', {
#             'object': obj
#         })
