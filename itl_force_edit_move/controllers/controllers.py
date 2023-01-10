# -*- coding: utf-8 -*-
# from odoo import http


# class ItlForceEditMove(http.Controller):
#     @http.route('/itl_force_edit_move/itl_force_edit_move/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_force_edit_move/itl_force_edit_move/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_force_edit_move.listing', {
#             'root': '/itl_force_edit_move/itl_force_edit_move',
#             'objects': http.request.env['itl_force_edit_move.itl_force_edit_move'].search([]),
#         })

#     @http.route('/itl_force_edit_move/itl_force_edit_move/objects/<model("itl_force_edit_move.itl_force_edit_move"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_force_edit_move.object', {
#             'object': obj
#         })
