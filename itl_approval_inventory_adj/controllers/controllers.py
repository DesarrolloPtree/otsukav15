# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalInventoryAdj(http.Controller):
#     @http.route('/itl_approval_inventory_adj/itl_approval_inventory_adj/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_inventory_adj/itl_approval_inventory_adj/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_inventory_adj.listing', {
#             'root': '/itl_approval_inventory_adj/itl_approval_inventory_adj',
#             'objects': http.request.env['itl_approval_inventory_adj.itl_approval_inventory_adj'].search([]),
#         })

#     @http.route('/itl_approval_inventory_adj/itl_approval_inventory_adj/objects/<model("itl_approval_inventory_adj.itl_approval_inventory_adj"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_inventory_adj.object', {
#             'object': obj
#         })
