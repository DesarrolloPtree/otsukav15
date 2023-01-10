# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPostWithAccount(http.Controller):
#     @http.route('/itl_post_with_account/itl_post_with_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_post_with_account/itl_post_with_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_post_with_account.listing', {
#             'root': '/itl_post_with_account/itl_post_with_account',
#             'objects': http.request.env['itl_post_with_account.itl_post_with_account'].search([]),
#         })

#     @http.route('/itl_post_with_account/itl_post_with_account/objects/<model("itl_post_with_account.itl_post_with_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_post_with_account.object', {
#             'object': obj
#         })
