import base64
from datetime import datetime
from itertools import groupby
import logging
import requests

from lxml import etree
from lxml.objectify import fromstring
from zeep import Client
from zeep.transports import Transport
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT, float_is_zero
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import html_escape
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'l10n_mx_edi.pac.sw.mixin']
    
    
    # Inherited from l10n_mx_edi
    def l10n_mx_edi_is_required(self):
        required = super(AccountPayment, self).l10n_mx_edi_is_required()
        
        if not self.partner_id:
            required = False
        
        _logger.info("====> required: " + str(required))
        return required