
from collections import namedtuple, OrderedDict, defaultdict
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import split_every
from psycopg2 import OperationalError

from odoo import api, fields, models, registry, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_is_zero, float_round

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'


    move_type = fields.Selection(selection_add=[
        ('delivered_by_sc','SC will deliver the product'),
        ('pick_up','Product pick up')])

class Picking(models.Model):
    _inherit = "stock.picking"


    move_type = fields.Selection(selection_add=[
        ('delivered_by_sc','SC will deliver the product'),
        ('pick_up','Product pick up')])
