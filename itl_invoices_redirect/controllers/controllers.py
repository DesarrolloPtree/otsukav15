# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInvoicesRedirect(http.Controller):
#     @http.route('/itl_invoices_redirect/itl_invoices_redirect/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_invoices_redirect/itl_invoices_redirect/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_invoices_redirect.listing', {
#             'root': '/itl_invoices_redirect/itl_invoices_redirect',
#             'objects': http.request.env['itl_invoices_redirect.itl_invoices_redirect'].search([]),
#         })

#     @http.route('/itl_invoices_redirect/itl_invoices_redirect/objects/<model("itl_invoices_redirect.itl_invoices_redirect"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_invoices_redirect.object', {
#             'object': obj
#         })
