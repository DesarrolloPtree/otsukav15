import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

import logging
_logger = logging.getLogger(__name__)

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    
    itl_already_printed = fields.Boolean(string="Upload file", track_visibility='onchange')
    
    def action_prepare_bancomer_file(self):
        active_ids = self.env.context.get('active_ids')
        expense_sheet_ids = self._context.get('active_model') == 'hr.expense.sheet' and self._context.get('active_ids') or []
        expense_sheet_ids = self.env['hr.expense.sheet'].browse(expense_sheet_ids)
        invalid_exp_sheet_ids = expense_sheet_ids.filtered(lambda e: e.state not in ['approve','post'])
        if invalid_exp_sheet_ids:
            raise ValidationError("You can process only Posted and Approved expense sheets.")
        
        if not active_ids:
            return ''
        
        context = dict(self._context or {})
        context['original_model'] = 'itl.prepare.bancomer.files'
        
        vals = {
            'itl_clave_pago_bnc': 'PTC',
            'itl_company_partner_id': self.env.user.company_id.partner_id.id,
            'itl_cuenta_ordenante': self._default_bank_account(),
            #'itl_mismo_banco_ids': self._default_mismo_banco_ids(),
            'itl_nomina_ids': self._default_nomina_ids()
            #'itl_interbancario_ids': self._default_interbancario_ids()
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
    
    def _default_nomina_ids(self):
        _logger.info("===>> _default_nomina_ids")
        expense_sheet_ids = self._context.get('active_model') == 'hr.expense.sheet' and self._context.get('active_ids') or []
        expense_sheet_ids = self.env['hr.expense.sheet'].browse(expense_sheet_ids)
        
        company_partner_id = self.env.user.company_id.partner_id
        bank_account_id = company_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
        cuenta_ordenante_name_size = 0
        if bank_account_id:
            cuenta_ordenante_name_size = len(bank_account_id[0].acc_number)
            bank_account_id = bank_account_id[0].id
        
        lines = []
        i = 1
        for exp_sheet in expense_sheet_ids:
            banco_beneficiario_id = False
            cuenta_beneficiario_id = False
            cuenta_name_size = 0
            num_cuenta = False
            if '012' in exp_sheet.employee_id.user_partner_id.bank_ids.mapped('bank_id.l10n_mx_edi_code'):
                cuenta_beneficiario_id = exp_sheet.employee_id.user_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
            #else:
            #    continue
            if cuenta_beneficiario_id:
                num_cuenta = cuenta_beneficiario_id[0].acc_number
                cuenta_name_size = len(num_cuenta)
                banco_beneficiario_id = cuenta_beneficiario_id[0].bank_id.id
                cuenta_beneficiario_id = cuenta_beneficiario_id[0].id
            else:
                cuenta_beneficiario_id = False
            
            vals = {
                'itl_exp_sheet_id': exp_sheet.id,
                'itl_rfc_empleado': exp_sheet.employee_id.user_partner_id.vat if exp_sheet.employee_id.user_partner_id.vat else "",
                'itl_tipo_cuenta': '99',
                'itl_numero_cuenta': num_cuenta,
                'itl_importe_pago': exp_sheet.total_amount,
                'itl_nombre_titular': exp_sheet.employee_id.name,
                'itl_banco_destino': '012',
                'itl_plaza_destino': '000'
            }
            vals['itl_invalid_record'] = self._check_vals_nomina(vals)
            
            lines.append((0, 0, vals))
            i += 1
        return lines
    
    def _check_vals_nomina(self, vals):
        invalid_record = False
        if vals['itl_rfc_empleado'] and len(vals['itl_rfc_empleado']) != 16:
            invalid_record = True
        if not vals['itl_tipo_cuenta'] or len(vals['itl_tipo_cuenta']) != 2:
            invalid_record = True
        if not vals['itl_numero_cuenta'] or len(vals['itl_numero_cuenta']) > 20 or len(vals['itl_numero_cuenta']) != 10 or len(vals['itl_numero_cuenta']) != 16:
            invalid_record = True
        if vals['itl_numero_cuenta'] and (len(vals['itl_numero_cuenta']) == 10 or len(vals['itl_numero_cuenta']) == 16):
            invalid_record = False
        if not vals['itl_importe_pago']:
            invalid_record = True
        if not vals['itl_nombre_titular']:
            invalid_record = True
        if not vals['itl_banco_destino']:
            invalid_record = True
        if not vals['itl_plaza_destino']:
            invalid_record = True
        
        return invalid_record
    
    def _default_mismo_banco_ids(self):
        expense_sheet_ids = self._context.get('active_model') == 'hr.expense.sheet' and self._context.get('active_ids') or []
        expense_sheet_ids = self.env['hr.expense.sheet'].browse(expense_sheet_ids)
        
        company_partner_id = self.env.user.company_id.partner_id
        bank_account_id = company_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
        cuenta_ordenante_name_size = 0
        if bank_account_id:
            cuenta_ordenante_name_size = len(bank_account_id[0].acc_number)
            bank_account_id = bank_account_id[0].id
        
        lines = []
        for exp_sheet in expense_sheet_ids:
            banco_beneficiario_id = False
            cuenta_beneficiario_id = False
            cuenta_name_size = 0
            if '012' in exp_sheet.employee_id.user_partner_id.bank_ids.mapped('bank_id.l10n_mx_edi_code'):
                cuenta_beneficiario_id = exp_sheet.employee_id.user_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
            else:
                continue
            if cuenta_beneficiario_id:
                cuenta_name_size = len(cuenta_beneficiario_id[0].acc_number)
                banco_beneficiario_id = cuenta_beneficiario_id[0].bank_id.id
                cuenta_beneficiario_id = cuenta_beneficiario_id[0].id
            else:
                cuenta_beneficiario_id = False
            
            if exp_sheet.employee_id.user_partner_id.vat == exp_sheet.company_id.partner_id.vat:
                itl_clave_pago_bnc = 'TNN'
            else:
                itl_clave_pago_bnc = 'PTC'
                
            itl_motivo_pago = exp_sheet.name
            
            vals = {
                'itl_exp_sheet_id': exp_sheet.id,
                'itl_clave_pago_bnc': itl_clave_pago_bnc,
                'itl_partner_id': exp_sheet.employee_id.user_partner_id.id,
                'itl_company_partner_id': exp_sheet.company_id.partner_id.id,
                'itl_asunto_beneficiario': cuenta_beneficiario_id,
                'itl_size_cuenta_benef': cuenta_name_size,
                'itl_banco_beneficiario': banco_beneficiario_id,
                'itl_asunto_ordenante': bank_account_id,
                'itl_size_cuenta_ordenante': cuenta_ordenante_name_size,
                'itl_divisa_operacion': exp_sheet.currency_id.id, 
                'itl_importe_operacion': exp_sheet.total_amount,
                'itl_motivo_pago': itl_motivo_pago,
                'itl_rfc_beneficiario': exp_sheet.employee_id.user_partner_id.vat if exp_sheet.employee_id.user_partner_id.vat else "",
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
        #if vals['itl_size_cuenta_benef'] != 18:
        #    _logger.info("===> itl_asunto_beneficiario")
        #    invalid_record = True
        #if vals['itl_size_cuenta_ordenante'] != 18:
        #    _logger.info("===> itl_asunto_ordenante")
        #    invalid_record = True
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
        expense_sheet_ids = self._context.get('active_model') == 'hr.expense.sheet' and self._context.get('active_ids') or []
        expense_sheet_ids = self.env['hr.expense.sheet'].browse(expense_sheet_ids)

        company_partner_id = self.env.user.company_id.partner_id
        bank_account_id = company_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code == '012')
        cuenta_ordenante_name_size = 0
        if bank_account_id:
            cuenta_ordenante_name_size = len(bank_account_id[0].l10n_mx_edi_clabe)
            bank_account_id = bank_account_id[0].id
            
        lines = []
        for exp_sheet in expense_sheet_ids:
            banco_beneficiario_id = False
            cuenta_beneficiario_id = False
            codigo_banco = ''
            cuenta_name_size = 0
            if '012' not in exp_sheet.employee_id.user_partner_id.bank_ids.mapped('bank_id.l10n_mx_edi_code'):
                cuenta_beneficiario_id = exp_sheet.employee_id.user_partner_id.bank_ids.filtered(lambda bank: bank.bank_id.l10n_mx_edi_code != '012')
            else:
                continue
            if cuenta_beneficiario_id:
                codigo_banco = cuenta_beneficiario_id[0].bank_id.c_banco
                cuenta_name_size = len(cuenta_beneficiario_id[0].l10n_mx_edi_clabe)
                banco_beneficiario_id = cuenta_beneficiario_id[0].bank_id.id
                cuenta_beneficiario_id = cuenta_beneficiario_id[0].id
            else:
                cuenta_beneficiario_id = False
            
            if exp_sheet.employee_id.user_partner_id.vat == exp_sheet.company_id.partner_id.vat:
                itl_clave_pago_bnc = 'TSC'
            else:
                itl_clave_pago_bnc = 'PSC'
                
            itl_motivo_pago = exp_sheet.name
            
            vals = {
                'itl_exp_sheet_id': exp_sheet.id,
                'itl_clave_pago_bnc': itl_clave_pago_bnc,
                'itl_partner_id': exp_sheet.employee_id.user_partner_id.id,
                'itl_company_partner_id': exp_sheet.company_id.partner_id.id,
                'itl_asunto_beneficiario': cuenta_beneficiario_id,
                'itl_size_cuenta_benef': cuenta_name_size,
                'itl_banco_beneficiario': banco_beneficiario_id,
                'itl_asunto_ordenante': bank_account_id,
                'itl_size_cuenta_ordenante': cuenta_ordenante_name_size,
                'itl_divisa_operacion': exp_sheet.currency_id.id, 
                'itl_importe_operacion': exp_sheet.total_amount,
                'itl_titular_asunto': exp_sheet.employee_id.user_partner_id.name,
                'itl_tipo_cuenta': '40',
                'itl_num_banco_benef': codigo_banco,
                'itl_ref_numerica': '',
                'itl_disponibilidad': 'H',
                'itl_motivo_pago': itl_motivo_pago,
                'itl_rfc_beneficiario': exp_sheet.employee_id.user_partner_id.vat if exp_sheet.employee_id.user_partner_id.vat else "",
                'itl_iva_pago': 10
            }
            vals['itl_invalid_record'] = self._check_vals_interbancario(vals)
            
            lines.append((0, 0, vals))
        return lines
    
    def _check_vals_interbancario(self, vals):
        invalid_record = False
        if not vals['itl_clave_pago_bnc']:
            _logger.info("###> itl_clave_pago_bnc")
            invalid_record = True
        #if vals['itl_size_cuenta_benef'] != 18:
        #    _logger.info("###> itl_asunto_beneficiario")
        #    invalid_record = True
        #if vals['itl_size_cuenta_ordenante'] != 18:
        #    _logger.info("###> itl_asunto_ordenante")
        #    invalid_record = True
        if vals['itl_divisa_operacion'] not in [33,2,1]:
            _logger.info("###> itl_divisa_operacion")
            invalid_record = True
        if vals['itl_importe_operacion'] == 0:
            _logger.info("###> itl_importe_operacion")
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