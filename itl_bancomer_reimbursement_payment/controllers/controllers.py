# -*- coding: utf-8 -*-
# from odoo import http


# class ItlBancomerReimbursementPayment(http.Controller):
#     @http.route('/itl_bancomer_reimbursement_payment/itl_bancomer_reimbursement_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_bancomer_reimbursement_payment/itl_bancomer_reimbursement_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_bancomer_reimbursement_payment.listing', {
#             'root': '/itl_bancomer_reimbursement_payment/itl_bancomer_reimbursement_payment',
#             'objects': http.request.env['itl_bancomer_reimbursement_payment.itl_bancomer_reimbursement_payment'].search([]),
#         })

#     @http.route('/itl_bancomer_reimbursement_payment/itl_bancomer_reimbursement_payment/objects/<model("itl_bancomer_reimbursement_payment.itl_bancomer_reimbursement_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_bancomer_reimbursement_payment.object', {
#             'object': obj
#         })
