# -*- coding: utf-8 -*-
import base64
from itertools import groupby
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import requests
from pytz import timezone

from lxml import etree
from lxml.objectify import fromstring
from suds.client import Client

from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr

from odoo.addons.l10n_mx_edi.tools.run_after_commit import run_after_commit

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.move'
    
    
    l10n_mx_uuid_sustituto =  fields.Char(string="UUID Sustituto")
    l10n_mx_motivo_cancelacion = fields.Selection(
        selection=[
            ('none', "Seleccionar motivo de Cancelacion"),
            ('01', "Comprobante emitido con errores con relación"),
            ('02', "Comprobante emitido con errores sin relación"),
            ('03', "No se llevó a cabo la operación"),
            ('04', "Operación nominativa relacionada en la factura global"),
        ],
        string="Motivo de Cancelación", copy=False,
        default='none',
        help="Al cancelar un CFDI es necesario elegir cual es el motivo de la cancelacion apartir del 1 de enero del 2022.")

    
    def _l10n_mx_edi_prodigia_cancel(self, pac_info):
        '''CANCEL Prodigia.
        '''
        url = pac_info['url']
        username = pac_info['username']
        password = pac_info['password']
        contract = pac_info['contract']
        test = pac_info['test']
        rfc_receptor = self.partner_id.vat
        rfc_emisor = self.company_id
        if self:
            certificate_id = self[0].company_id.l10n_mx_edi_certificate_ids[0].sudo(
            )
        for inv in self:

            # uuids = [inv.l10n_mx_edi_cfdi_uuid]
            rfc_receptor = inv.partner_id
            rfc_rec = ""
            if rfc_receptor.vat is False:
                rfc_rec = "XAXX010101000"
            else:
                rfc_rec = rfc_receptor.vat
                
            # Cancellation reason
            monto = f"{inv.amount_total or 0 :.6f}"
            motivo = inv.l10n_mx_motivo_cancelacion

            uuid_susitituto = inv.l10n_mx_uuid_sustituto
            
            if motivo != "none":
                uuid = inv.l10n_mx_edi_cfdi_uuid
                uuids = [inv.l10n_mx_edi_cfdi_uuid+"|"+rfc_rec +
                         "|"+rfc_emisor.vat+"|" + str(inv.amount_total)]
                
                if motivo == "01":
                    if uuid_susitituto == "":
                        cancelled = False
                        msg = 'No puedes cancelar un CFDI sin motivo de cancelación'
                        code = '0'
                        inv._l10n_mx_edi_post_cancel_process(cancelled, code, msg)
                        continue
                    
                    uuids = [uuid+"|"+rfc_rec +
                            "|"+rfc_emisor.vat+"|" + str(monto)+ "|"+ motivo+ "|"+ uuid_susitituto]
                    _logger.info(uuid+"|"+rfc_rec + "|"+rfc_emisor.vat+"|" + str(monto)+ "|"+ motivo+ "|"+ uuid_susitituto)
                else:
                    uuids = [uuid+"|"+rfc_rec +
                            "|"+rfc_emisor.vat+"|" + str(monto)+ "|"+ motivo]

                    _logger.info(uuid+"|"+rfc_rec + "|"+rfc_emisor.vat+"|" + str(monto)+ "|"+ motivo)

                if not certificate_id:
                    certificate_id = inv.l10n_mx_edi_cfdi_certificate_id.sudo()
                cer_pem = base64.encodestring(certificate_id.get_pem_cer(
                    certificate_id.content)).decode('UTF-8')
                key_pem = base64.encodestring(certificate_id.get_pem_key(
                    certificate_id.key, certificate_id.password)).decode('UTF-8')
                key_password = certificate_id.password
                rfc_emisor = self.company_id
                cancelled = False
                
                if(test):
                    cancelled = True
                    msg = 'Este comprobante se cancelo en modo pruebas'
                    code = '201'
                    inv._l10n_mx_edi_post_cancel_process(cancelled, code, msg)
                    continue
                try:
                    client = Client(url, timeout=50)
                    response = client.service.cancelar(
                        contract, username, password, rfc_emisor.vat, uuids, cer_pem, key_pem, key_password)
                except Exception as e:
                    inv.l10n_mx_edi_log_error(str(e))
                    continue
                code = getattr(response, 'codigo', None)
                cancelled = code in ('201', '202')
                msg = '' if cancelled else getattr(response, 'mensaje', None)
                code = '' if cancelled else code
                inv._l10n_mx_edi_post_cancel_process(cancelled, code, msg)
            else:
                cancelled = False
                msg = 'No puedes cancelar un CFDI sin motivo de cancelación'
                code = '0'
                inv._l10n_mx_edi_post_cancel_process(cancelled, code, msg)