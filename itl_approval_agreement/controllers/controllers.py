# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalContract(http.Controller):
#     @http.route('/itl_approval_contract/itl_approval_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_contract/itl_approval_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_contract.listing', {
#             'root': '/itl_approval_contract/itl_approval_contract',
#             'objects': http.request.env['itl_approval_contract.itl_approval_contract'].search([]),
#         })

#     @http.route('/itl_approval_contract/itl_approval_contract/objects/<model("itl_approval_contract.itl_approval_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_contract.object', {
#             'object': obj
#         })
