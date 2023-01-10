
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from lxml.objectify import fromstring
import base64
from lxml import etree
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    addenda_code = fields.Char(compute="_get_addenda_code")


    def _get_addenda_code(self):
        for move in self:
            move.addenda_code = False
            if (move.partner_id.addenda_code or move.partner_id.commercial_partner_id.addenda_code):
                move.addenda_code = move.partner_id.addenda_code or move.partner_id.commercial_partner_id.addenda_code

    # Inherited
    def l10n_mx_edi_append_addenda(self, xml_signed):
        return