# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # Inherit from account
    # Force to edit and save movent linked to posted payment
    def _validate_move_modification(self):
        pass