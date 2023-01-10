# -*- coding: utf-8 -*-
# from odoo import http


# class ItlProdigiaCfdiCancellation(http.Controller):
#     @http.route('/itl_prodigia_cfdi_cancellation/itl_prodigia_cfdi_cancellation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_prodigia_cfdi_cancellation/itl_prodigia_cfdi_cancellation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_prodigia_cfdi_cancellation.listing', {
#             'root': '/itl_prodigia_cfdi_cancellation/itl_prodigia_cfdi_cancellation',
#             'objects': http.request.env['itl_prodigia_cfdi_cancellation.itl_prodigia_cfdi_cancellation'].search([]),
#         })

#     @http.route('/itl_prodigia_cfdi_cancellation/itl_prodigia_cfdi_cancellation/objects/<model("itl_prodigia_cfdi_cancellation.itl_prodigia_cfdi_cancellation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_prodigia_cfdi_cancellation.object', {
#             'object': obj
#         })
