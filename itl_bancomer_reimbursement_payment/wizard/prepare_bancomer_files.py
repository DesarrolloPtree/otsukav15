from odoo import models, fields, api
import logging, base64, unidecode, zipfile, io
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)


class PrepareBancomerFiles(models.TransientModel):
    _name = "itl.prepare.bancomer.files"
    _description = "Prepare Bancomer Files"
    
    
    itl_mismo_banco_ids = fields.One2many('itl.prepare.bancomer.mismo.banco', 'itl_bancomer_file_id')
    itl_interbancario_ids = fields.One2many('itl.prepare.bancomer.interbancario', 'itl_bancomer_file_id')
    itl_clave_pago_bnc = fields.Selection([('TNN','Marcar todo como TNN'),('PTC','Marcar todo como PTC')], string="Clave de Pago", help="TNN = Traspaso Mismo Banco, PTC = Pago Mismo Banco", default='PTC')
    itl_all_comprobante_fiscal = fields.Boolean(string="Requiere Comprobante Fiscal")
    itl_company_partner_id = fields.Many2one('res.partner', string="Ordenante", default=lambda self: self.env.user.company_id.partner_id)
    itl_cuenta_ordenante = fields.Many2one('res.partner.bank', string="Asignar cuenta ordenante a todos los registros", help="No. de cuenta definida para el cargo")
    itl_banco_ordenante = fields.Many2one('res.bank', related="itl_cuenta_ordenante.bank_id", string="Banco ordenante")
    itl_invalid_records = fields.Boolean(compute="_compute_itl_invalid_records", string="Has invalid records")
    
    itl_nomina_ids = fields.One2many('itl.prepare.bancomer.nomina', 'itl_bancomer_file_id')
    
    @api.depends('itl_mismo_banco_ids','itl_interbancario_ids')
    def _compute_itl_invalid_records(self):
        self.itl_invalid_records = False
        # Invalid records for Mismo banco
        if self.itl_mismo_banco_ids:
            invalid_records = self.itl_mismo_banco_ids.filtered(lambda i: not i.itl_asunto_beneficiario or not i.itl_rfc_beneficiario)
            if invalid_records:
                self.itl_invalid_records = True
        # Invalid records for Interbancario
        if self.itl_interbancario_ids:
            invalid_records = self.itl_interbancario_ids.filtered(lambda i: not i.itl_asunto_beneficiario or not i.itl_rfc_beneficiario)
            if invalid_records:
                self.itl_invalid_records = True
                
    
    @api.onchange('itl_clave_pago_bnc')
    def _onchange_itl_all_tnn(self):
        if self.itl_clave_pago_bnc and self.itl_clave_pago_bnc == 'TNN':
            for item in self.itl_mismo_banco_ids:
                item.itl_clave_pago_bnc = 'TNN'
        elif self.itl_clave_pago_bnc and self.itl_clave_pago_bnc == 'PTC':
            for item in self.itl_mismo_banco_ids:
                item.itl_clave_pago_bnc = 'PTC'
        else:
            for item in self.itl_mismo_banco_ids:
                item.itl_clave_pago_bnc = False
                
                
    @api.onchange('itl_all_comprobante_fiscal')
    def _onchange_itl_all_comprobante_fiscal(self):
        # Mismo banco
        if self.itl_all_comprobante_fiscal:
            for item in self.itl_mismo_banco_ids:
                item.itl_comprobante_fiscal = True
        else:
            for item in self.itl_mismo_banco_ids:
                item.itl_comprobante_fiscal = False
        # Interbancario
        if self.itl_all_comprobante_fiscal:
            for item in self.itl_interbancario_ids:
                item.itl_comprobante_fiscal = True
        else:
            for item in self.itl_interbancario_ids:
                item.itl_comprobante_fiscal = False
                
    @api.onchange('itl_cuenta_ordenante')
    def _onchange_itl_cuenta_ordenante(self):
        # For Mismo banco
        if self.itl_cuenta_ordenante:
            for item in self.itl_mismo_banco_ids:
                item.itl_asunto_ordenante = self.itl_cuenta_ordenante
        else:
            for item in self.itl_mismo_banco_ids:
                item.itl_asunto_ordenante = False
        # For Interbancario
        if self.itl_cuenta_ordenante:
            for item in self.itl_interbancario_ids:
                item.itl_asunto_ordenante = self.itl_cuenta_ordenante
        else:
            for item in self.itl_interbancario_ids:
                item.itl_asunto_ordenante = False
    
    def action_confirm(self):
        #mismo_banco = self.check_fields_validation_mismo_banco()
        #interbancario = self.check_fields_validation_interbancario()
        nomina = self.check_fields_validation_nomina()
        
        zip_stream = io.BytesIO()
        has_data = False
        with zipfile.ZipFile(zip_stream, 'w') as myzip:
            if(len(nomina) > 0):
                has_data = True
                nomina = "".join(nomina)
                myzip.writestr("BancomerPagos.txt", unidecode.unidecode(nomina))
            myzip.close()
            
        if has_data:
            values = {
                'name': 'BancomerFiles.zip',
                'type': 'binary',
                'mimetype': 'application/zip',
                'public': False,
                'db_datas': base64.b64encode(zip_stream.getvalue())
            }

            attachment = self.env['ir.attachment'].create(values)

            return {
                'type': 'ir.actions.act_url',
    #             'url': '/web/content/%s?download=true' % (attachment_id.id),
                'url': '/web/content/' + str(attachment.id) + '?download=True',
                'target': 'new',
                'nodestroy': False,
            }
        else:
            raise Warning("Nothing to process.")
    
    def check_fields_validation_nomina(self):
        # For Mismo banco
        mismo_banco = []
        i = 1
        for record in self.itl_nomina_ids:
            line = ""
            
            if not record.itl_invalid_record:
                # Número consecutivo
                line += str(i).zfill(9)
                # RFC
                line += str(record.itl_rfc_empleado).ljust(16)
                # Tipo de cuenta
                line += record.itl_tipo_cuenta
                # Número cuenta
                line += record.itl_numero_cuenta.ljust(20)
                # Importe de pago
                line += str("{:.2f}".format(record.itl_importe_pago)).replace('.','').zfill(15)
                # Nombre titular
                line += str(record.itl_nombre_titular).ljust(40)
                # Banco destino - codigo
                line += str(record.itl_banco_destino)
                # Plaza destino - codigo
                line += str(record.itl_plaza_destino)
                # Enter
                line += '\n'
                record.itl_exp_sheet_id.itl_already_printed = True
                mismo_banco.append(line)
                i += 1
        
        return mismo_banco
    
    def check_fields_validation_mismo_banco(self):
        # For Mismo banco
        mismo_banco = []
        for record in self.itl_mismo_banco_ids:
            invalid_record = False
            line = ""
            if not record.itl_clave_pago_bnc:
                invalid_record = True
            if not record.itl_asunto_beneficiario:
                invalid_record = True
            if not record.itl_asunto_ordenante:
                invalid_record = True
            if not record.itl_divisa_operacion or (record.itl_divisa_operacion and record.itl_divisa_operacion.name not in ['MXN','USD','EUR']):
                invalid_record = True
            if not record.itl_importe_operacion or record.itl_importe_operacion == 0:
                invalid_record = True
            if not record.itl_motivo_pago:
                invalid_record = True
            
            if record.itl_comprobante_fiscal:
                if not record.itl_rfc_beneficiario:
                    invalid_record = True
                if not record.itl_iva_pago:
                    invalid_record = True
            
            if not invalid_record:
                # Clave de Pago Bnc - 3
                line += record.itl_clave_pago_bnc
                # Asunto Beneficiario - 18
                line += str(record.itl_asunto_beneficiario.acc_number).zfill(18)
                # Asunto Ordenante - 18
                line += str(record.itl_asunto_ordenante.acc_number).zfill(18)
                # Divisa de la Operación - 3
                if record.itl_divisa_operacion.name == 'MXN':
                    divisa = 'MXP'
                else:
                    divisa = record.itl_divisa_operacion.name
                line += divisa
                # Importe de la Operación - 16
                line += str(record.itl_importe_operacion).zfill(16)
                # Motivo de Pago - 30
                line += str(record.itl_motivo_pago).ljust(30)
                # Comprobante fiscal - 1
                if record.itl_comprobante_fiscal:
                    comp_fiscal = '1'
                else:
                    comp_fiscal = '0'
                line += comp_fiscal
                # RFC Beneficiario - 18
                line += str(record.itl_rfc_beneficiario).ljust(18)
                # IVA del pago - 15
                line += str(record.itl_iva_pago.amount/100).zfill(15)
                # Enter
                line += '\n'
                record.itl_exp_sheet_id.itl_already_printed = True
                mismo_banco.append(line)
                
        return mismo_banco
                
    def check_fields_validation_interbancario(self):  
        # For Interbancario
        interbancario = []
        for record in self.itl_interbancario_ids:
            invalid_record = False
            line = ""
            if not record.itl_clave_pago_bnc:
                invalid_record = True
            if not record.itl_asunto_beneficiario:
                invalid_record = True
            if not record.itl_asunto_ordenante:
                invalid_record = True
            if not record.itl_divisa_operacion or (record.itl_divisa_operacion and record.itl_divisa_operacion.name not in ['MXN','USD','EUR']):
                invalid_record = True
            if not record.itl_importe_operacion or record.itl_importe_operacion == 0:
                invalid_record = True
            if not record.itl_titular_asunto:
                invalid_record = True
            if not record.itl_tipo_cuenta:
                invalid_record = True
            if not record.itl_num_banco_benef:
                invalid_record = True
            if not record.itl_motivo_pago:
                invalid_record = True
            if not record.itl_ref_numerica:
                invalid_record = True
            if not record.itl_disponibilidad:
                invalid_record = True
            
            if record.itl_comprobante_fiscal:
                if not record.itl_rfc_beneficiario:
                    invalid_record = True
                if not record.itl_iva_pago:
                    invalid_record = True
                    
            if not invalid_record:
                # Clave de Pago Bnc - 3
                line += record.itl_clave_pago_bnc
                # Asunto Beneficiario - 18
                line += str(record.itl_asunto_beneficiario.l10n_mx_edi_clabe).zfill(18)
                # Asunto Ordenante - 18
                line += str(record.itl_asunto_ordenante.l10n_mx_edi_clabe).zfill(15)
                # Divisa de la Operación - 3
                if record.itl_divisa_operacion.name == 'MXN':
                    divisa = 'MXP'
                else:
                    divisa = record.itl_divisa_operacion.name
                line += divisa
                # Importe de la Operación - 16
                line += str(record.itl_importe_operacion).zfill(16)
                # Motivo de Pago - 30
                line += str(record.itl_motivo_pago).ljust(30)
                # Comprobante fiscal - 1
                if record.itl_comprobante_fiscal:
                    comp_fiscal = '1'
                else:
                    comp_fiscal = '0'
                line += comp_fiscal
                # RFC Beneficiario - 18
                line += str(record.itl_rfc_beneficiario).ljust(18)
                # IVA del pago - 15
                line += str(record.itl_iva_pago.amount/100).zfill(15)
                # Enter
                line += '\n'
                record.itl_exp_sheet_id.itl_already_printed = True
                interbancario.append(line)
                
        return interbancario

class PrepareBancomerNomina(models.TransientModel):
    _name = "itl.prepare.bancomer.nomina"
    _description = "Prepare Bancomer Nómina"
    
    
    itl_bancomer_file_id = fields.Many2one('itl.prepare.bancomer.files', string="Bancomer file")
    itl_exp_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Sheet")
    itl_rfc_empleado = fields.Char(string="RFC Empleado", readonly=True, size=16)
    itl_tipo_cuenta = fields.Selection([('01',' Cuenta de cheques'),
                                        ('03',' Tarjeta de débito'),
                                       ('40',' Cuenta CLABE'),
                                       ('98',' Tarjeta de pagos'),
                                       ('99','Otro')], string="Tipo de pagos", default="99", size=2)
    itl_numero_cuenta = fields.Char(string="Número de cuenta", size=16)
    itl_importe_pago = fields.Float(string="Importe del pago", size=15, readonly=True)
    itl_nombre_titular = fields.Char(string="Nombre del titular", size=40)
    itl_banco_destino = fields.Char(string="Banco destino", size=3)
    itl_plaza_destino = fields.Char(string="Plaza destino", size=3)
    
    itl_invalid_record = fields.Boolean(string="Invalid record", default=False)
    
    @api.onchange('itl_numero_cuenta','itl_banco_destino','itl_plaza_destino')
    def _onchange_vals(self):
        invalid_record = False
        if not self.itl_numero_cuenta or len(self.itl_numero_cuenta) > 20 or len(self.itl_numero_cuenta) != 10 or len(self.itl_numero_cuenta) != 16:
            invalid_record = True
        if len(self.itl_numero_cuenta) == 10 or len(self.itl_numero_cuenta) == 16:
            invalid_record = False
        if not self.itl_banco_destino or not self.itl_banco_destino.isdigit():
            invalid_record = True
        if not self.itl_plaza_destino or not self.itl_plaza_destino.isdigit():
            invalid_record = True
                
        self.itl_invalid_record = invalid_record
    
    
class PrepareBancomerMismoBanco(models.TransientModel):
    _name = "itl.prepare.bancomer.mismo.banco"
    _description = "Prepare Bancomer Mimso Banco"
    
    
    itl_bancomer_file_id = fields.Many2one('itl.prepare.bancomer.files', string="Bancomer file")
    itl_exp_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Sheet")
    itl_partner_id = fields.Many2one('res.partner', string="Beneficiario")
    itl_company_partner_id = fields.Many2one('res.partner', string="Ordenante")
    itl_clave_pago_bnc = fields.Selection([('TNN', 'Traspaso Mismo Banco'),('PTC','Pago Mismo Banco')], string="Tipo", help="Valor que indicará que el archivo que se está importando es MIXTO")
    itl_asunto_beneficiario = fields.Many2one('res.partner.bank', string="Cuenta Benef.", help="No. de cuenta definida para el abono")
    itl_size_cuenta_benef = fields.Integer()
    itl_banco_beneficiario = fields.Many2one('res.bank', string="Banco Benef.")
    itl_asunto_ordenante = fields.Many2one('res.partner.bank', string="Cuenta Ordenante", help="No. de cuenta definida para el cargo")
    itl_size_cuenta_ordenante = fields.Integer()
    itl_divisa_operacion = fields.Many2one('res.currency', string="Divisa", help="MXP (pesos mexicanos) USD (Dólar Americano) EUR (Unión Europea)")
    itl_importe_operacion = fields.Monetary(string="Importe", currency_field="itl_divisa_operacion", help="Justificado a la derecha relleno con ceros Formato: ####.dd")
    itl_motivo_pago = fields.Char(string="Motivo de Pago", help="La información aquí plasmada será enviada al estado de cuenta del Ordenante y del Beneficiario")
    itl_comprobante_fiscal = fields.Boolean(string="Comp. Fiscal", help="Posibles valores 0 = Sin comprobante fiscal 1 = Con comprobante fiscal")
    itl_rfc_beneficiario = fields.Char(string="RFC Benef.", help="Cuando se activa el “Comprobante Fiscal” debe llenar el RFC del beneficiario con 18 espacios. Sólo aplica persona física")
    itl_iva_pago = fields.Many2one('account.tax', string="IVA del Pago", help="Cuando se activa el “Comprobante Fiscal”, se indica el IVA del importe pagado. Rellenar con ceros sin perder el formato ####.dd")
    itl_invalid_record = fields.Boolean(string="Invalid record", default=False)
    itl_invalid_bank = fields.Boolean(string="Invalid Bank", default=False)
    
    
    @api.onchange('itl_asunto_beneficiario','itl_clave_pago_bnc','itl_asunto_ordenante','itl_divisa_operacion','itl_importe_operacion','itl_comprobante_fiscal','itl_rfc_beneficiario')
    def _onchange_itl_asunto_beneficiario(self):
        self.itl_banco_ordenante = self.itl_asunto_beneficiario.bank_id
        self.itl_size_cuenta_benef = len(self.itl_asunto_beneficiario)
        self.itl_size_cuenta_ordenante = len(self.itl_asunto_ordenante)
        invalid_record = False
        self.itl_invalid_bank = False
        if self.itl_asunto_beneficiario and self.itl_asunto_beneficiario.bank_id and self.itl_asunto_beneficiario.bank_id.l10n_mx_edi_code != '012':
            self.itl_invalid_bank = True
        if not self.itl_clave_pago_bnc:
            _logger.info("===> itl_clave_pago_bnc")
            invalid_record = True
        if not self.itl_asunto_beneficiario:
            _logger.info("===> itl_asunto_beneficiario")
            invalid_record = True
        if not self.itl_asunto_ordenante:
            _logger.info("===> itl_asunto_ordenante")
            invalid_record = True
        if not self.itl_divisa_operacion or (self.itl_divisa_operacion and self.itl_divisa_operacion.name not in ['MXN','USD','EUR']):
            _logger.info("===> itl_divisa_operacion")
            invalid_record = True
        if not self.itl_importe_operacion or self.itl_importe_operacion == 0:
            _logger.info("===> itl_importe_operacion")
            invalid_record = True
        if not self.itl_motivo_pago:
            _logger.info("===> itl_motivo_pago")
            invalid_record = True

        if self.itl_comprobante_fiscal:
            if not self.itl_rfc_beneficiario:
                _logger.info("===> itl_rfc_beneficiario")
                invalid_record = True
            if not self.itl_iva_pago:
                _logger.info("===> itl_iva_pago")
                invalid_record = True
                
        self.itl_invalid_record = invalid_record
        
    
class PrepareBancomerInterbancario(models.TransientModel):
    _name = "itl.prepare.bancomer.interbancario"
    _description = "Prepare Bancomer Interbancario"
    
    
    itl_bancomer_file_id = fields.Many2one('itl.prepare.bancomer.files', string="Bancomer file")
    itl_exp_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Sheet")
    itl_partner_id = fields.Many2one('res.partner', string="Beneficiario")
    itl_company_partner_id = fields.Many2one('res.partner', string="Ordenante")
    itl_clave_pago_bnc = fields.Selection([('TSC', 'Traspaso Interbancario'),('PSC','Pago Interbancario')], string="Tipo", help="Valor que indicará que el archivo que se está importando es MIXTO")
    itl_asunto_beneficiario = fields.Many2one('res.partner.bank', string="Cuenta Benef.", help="No. de cuenta definida para el abono")
    itl_size_cuenta_benef = fields.Integer()
    itl_banco_beneficiario = fields.Many2one('res.bank', string="Banco Benef.")
    itl_asunto_ordenante = fields.Many2one('res.partner.bank', string="Cuenta Ordenante", help="No. de cuenta definida para el cargo")
    itl_size_cuenta_ordenante = fields.Integer()
    itl_divisa_operacion = fields.Many2one('res.currency', string="Divisa", help="MXP (pesos mexicanos) USD (Dólar Americano) EUR (Unión Europea)")
    itl_importe_operacion = fields.Monetary(string="Importe", currency_field="itl_divisa_operacion", help="Justificado a la derecha relleno con ceros Formato: ####.dd")
    itl_titular_asunto = fields.Char(string="Titular")
    itl_tipo_cuenta = fields.Selection([('03','Tarjeta de Débito'),('40','Cuenta CLABE')], string="Tipo Cuenta", default="40")
    itl_num_banco_benef = fields.Char(string="Número Banco", help="Número Oficial BANXICO Consultar catálogo en Banxico, se consideran los 3 últimos campos")
    itl_motivo_pago = fields.Char(string="Motivo de Pago", help="La información aquí plasmada será enviada al estado de cuenta del Ordenante y del Beneficiario")
    itl_ref_numerica = fields.Char(string="Ref. Num.", size=7)
    itl_disponibilidad = fields.Selection([('H','Mismo día vía SPEI'),('M','Día siguiente vía CECOBAN')], string="Disponibilidad", default="H")
    itl_comprobante_fiscal = fields.Boolean(string="Comp. Fiscal", help="Posibles valores 0 = Sin comprobante fiscal 1 = Con comprobante fiscal")
    itl_rfc_beneficiario = fields.Char(string="RFC Benef.", help="Cuando se activa el “Comprobante Fiscal” debe llenar el RFC del beneficiario con 18 espacios. Sólo aplica persona física")
    itl_iva_pago = fields.Many2one('account.tax', string="IVA del Pago", help="Cuando se activa el “Comprobante Fiscal”, se indica el IVA del importe pagado. Rellenar con ceros sin perder el formato ####.dd")
    itl_invalid_record = fields.Boolean(string="Invalid record")
    
    
    @api.onchange('itl_asunto_beneficiario','itl_clave_pago_bnc','itl_asunto_ordenante','itl_divisa_operacion','itl_importe_operacion','itl_comprobante_fiscal',
                 'itl_titular_asunto','itl_tipo_cuenta','itl_num_banco_benef','itl_motivo_pago','itl_ref_numerica','itl_disponibilidad','itl_rfc_beneficiario')
    def _onchange_itl_asunto_beneficiario(self):
        self.itl_banco_ordenante = self.itl_asunto_beneficiario.bank_id
        self.itl_size_cuenta_benef = len(self.itl_asunto_beneficiario)
        self.itl_size_cuenta_ordenante = len(self.itl_asunto_ordenante)
        self.itl_num_banco_benef = self.itl_asunto_beneficiario.bank_id.c_banco
        invalid_record = False
        if not self.itl_clave_pago_bnc:
            _logger.info("####> itl_clave_pago_bnc")
            invalid_record = True
        if not self.itl_asunto_beneficiario:
            _logger.info("####> itl_asunto_beneficiario")
            invalid_record = True
        if not self.itl_asunto_ordenante:
            _logger.info("####> itl_asunto_ordenante")
            invalid_record = True
        if not self.itl_divisa_operacion or (self.itl_divisa_operacion and self.itl_divisa_operacion.name not in ['MXN','USD','EUR']):
            _logger.info("####> itl_divisa_operacion")
            invalid_record = True
        if not self.itl_importe_operacion or self.itl_importe_operacion == 0:
            _logger.info("####> itl_importe_operacion")
            invalid_record = True
        if not self.itl_titular_asunto:
            _logger.info("####> itl_titular_asunto")
            invalid_record = True
        if not self.itl_tipo_cuenta:
            _logger.info("####> itl_tipo_cuenta")
            invalid_record = True
        if not self.itl_num_banco_benef or (self.itl_num_banco_benef and len(self.itl_num_banco_benef) > 3):
            _logger.info("####> itl_num_banco_benef")
            invalid_record = True
        if not self.itl_motivo_pago:
            _logger.info("####> itl_motivo_pago")
            invalid_record = True
        if not self.itl_ref_numerica or not self.itl_ref_numerica.isdigit():
            _logger.info("####> itl_ref_numerica")
            invalid_record = True
        if not self.itl_disponibilidad:
            _logger.info("####> itl_disponibilidad")
            invalid_record = True

        if self.itl_comprobante_fiscal:
            if not self.itl_rfc_beneficiario:
                _logger.info("####> itl_rfc_beneficiario")
                invalid_record = True
            if not self.itl_iva_pago:
                _logger.info("####> itl_iva_pago")
                invalid_record = True
        _logger.info("#######> invalid_record: " + str(invalid_record))
        self.itl_invalid_record = invalid_record
    