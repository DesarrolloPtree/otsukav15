# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    itl_alreadyPrinted = fields.Boolean(string="Upload file", track_visibility='onchange')

    def action_prepare_bancomer_file(self):
        active_ids = self.env.context.get('active_ids')
        move_ids = self._context.get('active_model') == 'account.move' and self._context.get('active_ids') or []
        move_ids = self.env['account.move'].browse(move_ids)
        invalid_bill_ids = move_ids.filtered(lambda m: m.type != 'in_invoice' or m.state != 'posted' or m.itl_alreadyPrinted or m.invoice_payment_state == 'paid')
        if invalid_bill_ids:
            raise Warning("You can process Posted and Unpaid Bills only.")
        
        if not active_ids:
            return ''
        
        context = dict(self._context or {})
        context['original_model'] = 'itl.prepare.bancomer.files'
        
        vals = {
            'itl_clave_pago_bnc': 'PTC',
            'itl_company_partner_id': self.env.user.company_id.partner_id.id,
            'itl_cuenta_ordenante': self._default_bank_account(),
            'itl_mismo_banco_ids': self._default_mismo_banco_ids(),
            'itl_interbancario_ids': self._default_interbancario_ids()
        }
        bancomer_file = self.env['itl.prepare.bancomer.files'].create(vals)
        
        return {
            'name': _('Prepare Bancomer Payment File'),
            'res_model': 'itl.prepare.bancomer.files',
            'res_id': bancomer_file.id,
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('itl_bancomer_reimbursement_payment.itl_import_bancomer_payment_file').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def _default_bank_account(self):
        company_partner_id = self.env.user.company_id.partner_id
        bank_account_id = company_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
        if bank_account_id:
            return bank_account_id[0].id
        else:
            return False
    
    def _default_mismo_banco_ids(self):
        move_ids = self._context.get('active_model') == 'account.move' and self._context.get('active_ids') or []
        move_ids = self.env['account.move'].browse(move_ids)
        
        invalid_bill_ids = move_ids.filtered(lambda m: m.type == 'in_invoice' and m.state != 'posted')
        #if invalid_bill_ids:
        #    raise ValidationError("You can process Posted Bills only.")
        
        company_partner_id = self.env.user.company_id.partner_id
        bank_account_id = company_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
        cuenta_ordenante_name_size = 0
        if bank_account_id:
            cuenta_ordenante_name_size = len(bank_account_id[0].l10n_mx_edi_clabe)
            bank_account_id = bank_account_id[0].id
        
        lines = []
        for move in move_ids:
            banco_beneficiario_id = False
            cuenta_beneficiario_id = False
            cuenta_name_size = 0
            if '012' in move.partner_id.bank_ids.mapped('bank_id.l10n_mx_edi_code'):
                cuenta_beneficiario_id = move.partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
            else:
                continue
            if cuenta_beneficiario_id:
                cuenta_name_size = len(cuenta_beneficiario_id[0].l10n_mx_edi_clabe)
                banco_beneficiario_id = cuenta_beneficiario_id[0].bank_id.id
                cuenta_beneficiario_id = cuenta_beneficiario_id[0].id
            else:
                cuenta_beneficiario_id = False
            
            if move.partner_id.vat == move.company_id.partner_id.vat:
                itl_clave_pago_bnc = 'TNN'
            else:
                itl_clave_pago_bnc = 'PTC'
                
            if move.ref:
                itl_motivo_pago = move.name + ' | ' + move.ref
            else:
                itl_motivo_pago = move.name
            
            vals = {
                'itl_bill_id': move.id,
                'itl_clave_pago_bnc': itl_clave_pago_bnc,
                'itl_partner_id': move.partner_id.id,
                'itl_company_partner_id': move.company_id.partner_id.id,
                'itl_asunto_beneficiario': cuenta_beneficiario_id,
                'itl_size_cuenta_benef': cuenta_name_size,
                'itl_banco_beneficiario': banco_beneficiario_id,
                'itl_asunto_ordenante': bank_account_id,
                'itl_size_cuenta_ordenante': cuenta_ordenante_name_size,
                'itl_divisa_operacion': move.currency_id.id, 
                'itl_importe_operacion': move.amount_residual,
                'itl_motivo_pago': itl_motivo_pago,
                'itl_rfc_beneficiario': move.partner_id.vat,
                'itl_iva_pago': 10
            }
            vals['itl_invalid_record'] = self._check_vals_mismo_banco(vals)
            
            lines.append((0, 0, vals))
        return lines
    
    def _check_vals_mismo_banco(self, vals):
        invalid_record = False
        if not vals['itl_clave_pago_bnc']:
            _logger.info("===> itl_clave_pago_bnc")
            invalid_record = True
        if vals['itl_size_cuenta_benef'] != 18:
            _logger.info("===> itl_asunto_beneficiario")
            invalid_record = True
        if vals['itl_size_cuenta_ordenante'] != 18:
            _logger.info("===> itl_asunto_ordenante")
            invalid_record = True
        if vals['itl_divisa_operacion'] not in [33,2,1]:
            _logger.info("===> itl_divisa_operacion")
            invalid_record = True
        if vals['itl_importe_operacion'] == 0:
            _logger.info("===> itl_importe_operacion")
            invalid_record = True
        if not vals['itl_motivo_pago']:
            _logger.info("===> itl_motivo_pago")
            invalid_record = True
        _logger.info("==============> invalid_record: " + str(invalid_record))
        return invalid_record
    
    def _default_interbancario_ids(self):
        move_ids = self._context.get('active_model') == 'account.move' and self._context.get('active_ids') or []
        move_ids = self.env['account.move'].browse(move_ids)
        
        invalid_bill_ids = move_ids.filtered(lambda m: m.state != 'posted')
        #if invalid_bill_ids:
        #    raise ValidationError("You can process Posted bills only.")
        
        company_partner_id = self.env.user.company_id.partner_id
        bank_account_id = company_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
        cuenta_ordenante_name_size = 0
        if bank_account_id:
            cuenta_ordenante_name_size = len(bank_account_id[0].l10n_mx_edi_clabe)
            bank_account_id = bank_account_id[0].id
            
        lines = []
        for move in move_ids:
            banco_beneficiario_id = False
            cuenta_beneficiario_id = False
            codigo_banco = ''
            cuenta_name_size = 0
            if '012' not in move.partner_id.bank_ids.mapped('bank_id.l10n_mx_edi_code'):
                cuenta_beneficiario_id = move.partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code != '012')
            else:
                continue
            if cuenta_beneficiario_id:
                codigo_banco = cuenta_beneficiario_id[0].bank_id.c_banco
                cuenta_name_size = len(cuenta_beneficiario_id[0].l10n_mx_edi_clabe)
                banco_beneficiario_id = cuenta_beneficiario_id[0].bank_id.id
                cuenta_beneficiario_id = cuenta_beneficiario_id[0].id
            else:
                cuenta_beneficiario_id = False
            
            if move.partner_id.vat == move.company_id.partner_id.vat:
                itl_clave_pago_bnc = 'TSC'
            else:
                itl_clave_pago_bnc = 'PSC'
                
            if move.ref:
                itl_motivo_pago = move.name + ' | ' + move.ref
            else:
                itl_motivo_pago = move.name
            
            vals = {
                'itl_bill_id': move.id,
                'itl_clave_pago_bnc': itl_clave_pago_bnc,
                'itl_partner_id': move.partner_id.id,
                'itl_company_partner_id': move.company_id.partner_id.id,
                'itl_asunto_beneficiario': cuenta_beneficiario_id,
                'itl_size_cuenta_benef': cuenta_name_size,
                'itl_banco_beneficiario': banco_beneficiario_id,
                'itl_asunto_ordenante': bank_account_id,
                'itl_size_cuenta_ordenante': cuenta_ordenante_name_size,
                'itl_divisa_operacion': move.currency_id.id, 
                'itl_importe_operacion': move.amount_residual,
                'itl_titular_asunto': '',
                'itl_tipo_cuenta': '40',
                'itl_num_banco_benef': codigo_banco,
                'itl_ref_numerica': '',
                'itl_disponibilidad': 'H',
                'itl_motivo_pago': itl_motivo_pago,
                'itl_rfc_beneficiario': move.partner_id.vat,
                'itl_iva_pago': 10
            }
            vals['itl_invalid_record'] = self._check_vals_interbancario(vals)
            
            lines.append((0, 0, vals))
        return lines
    
    def _check_vals_interbancario(self, vals):
        invalid_record = False
        if not vals['itl_clave_pago_bnc']:
            _logger.info("####> itl_clave_pago_bnc")
            invalid_record = True
        if vals['itl_size_cuenta_benef'] != 18:
            _logger.info("===> itl_asunto_beneficiario")
            invalid_record = True
        if vals['itl_size_cuenta_ordenante'] != 18:
            _logger.info("===> itl_asunto_ordenante")
            invalid_record = True
        if vals['itl_divisa_operacion'] not in [33,2,1]:
            _logger.info("===> itl_divisa_operacion")
            invalid_record = True
        if vals['itl_importe_operacion'] == 0:
            _logger.info("===> itl_importe_operacion")
            invalid_record = True
        if not vals['itl_titular_asunto']:
            _logger.info("####> itl_titular_asunto")
            invalid_record = True
        if not vals['itl_tipo_cuenta']:
            _logger.info("####> itl_tipo_cuenta")
            invalid_record = True
        if not vals['itl_num_banco_benef'] or len(vals['itl_num_banco_benef']) > 3:
            _logger.info("####> itl_num_banco_benef")
            invalid_record = True
        if not vals['itl_motivo_pago']:
            _logger.info("####> itl_motivo_pago")
            invalid_record = True
        if not vals['itl_ref_numerica']:
            _logger.info("####> itl_ref_numerica")
            invalid_record = True
        if not vals['itl_disponibilidad']:
            _logger.info("####> itl_disponibilidad")
            invalid_record = True
        _logger.info("##################> invalid_record: " + str(invalid_record))
        return invalid_record