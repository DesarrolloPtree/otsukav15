from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    _rec_name = 'itl_rec_name'
    
    
    itl_rec_name = fields.Char(compute="_compute_rec_name")
    
    
    def _compute_rec_name(self):
        for bank in self:
            _logger.info("====> self._context: " + str(self._context))
            if self._context.get('original_model'):
                name = ''
                if self._context.get('itl_mismo_banco', False):
                    if bank.acc_number and bank.bank_id.name:
                        name += '%s - %s' % (bank.acc_number, bank.bank_id.name)
                    if not bank.acc_number and bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', bank.bank_id.name)
                    if bank.acc_number and not bank.bank_id.name:
                        name += '%s - %s' % (bank.acc_number, 'Sin Banco')
                    if not bank.acc_number and not bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', 'Sin Banco')
                if self._context.get('itl_interbancario', False):
                    if bank.l10n_mx_edi_clabe and bank.bank_id.name:
                        name += '%s - %s' % (bank.l10n_mx_edi_clabe, bank.bank_id.name)
                    if not bank.l10n_mx_edi_clabe and bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', bank.bank_id.name)
                    if bank.l10n_mx_edi_clabe and not bank.bank_id.name:
                        name += '%s - %s' % (bank.l10n_mx_edi_clabe, 'Sin Banco')
                    if not bank.l10n_mx_edi_clabe and not bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', 'Sin Banco')
                bank.itl_rec_name = name
            else:
                bank.itl_rec_name = bank.acc_number
    
    @api.depends()
    def name_get(self):
        result = []
        if self._context.get('original_model', False):
            for bank in self:
                name = ''
                if self._context.get('itl_mismo_banco', False):
                    if bank.acc_number and bank.bank_id.name:
                        name += '%s - %s' % (bank.acc_number, bank.bank_id.name)
                    if not bank.acc_number and bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', bank.bank_id.name)
                    if bank.acc_number and not bank.bank_id.name:
                        name += '%s - %s' % (bank.acc_number, 'Sin Banco')
                    if not bank.acc_number and not bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', 'Sin Banco')
                if self._context.get('itl_interbancario', False):
                    if bank.l10n_mx_edi_clabe and bank.bank_id.name:
                        name += '%s - %s' % (bank.l10n_mx_edi_clabe, bank.bank_id.name)
                    if not bank.l10n_mx_edi_clabe and bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', bank.bank_id.name)
                    if bank.l10n_mx_edi_clabe and not bank.bank_id.name:
                        name += '%s - %s' % (bank.l10n_mx_edi_clabe, 'Sin Banco')
                    if not bank.l10n_mx_edi_clabe and not bank.bank_id.name:
                        name += '%s - %s' % ('Sin cuenta', 'Sin Banco')
                result.append((bank.id, name))
        else:
            result = super(ResPartnerBank, self).name_get()
        return result