# Copyright 2012-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = "account.account"

    
    def _revaluation_query(self, revaluation_date):

        tables, where_clause, where_clause_params = self.env[
            "account.move.line"
        ]._query_get()
        query = (
            "with amount as ( SELECT aml.account_id, aml.partner_id, "
            "aml.currency_id, aml.debit, aml.credit, aml.amount_currency "
            "FROM account_move_line aml LEFT JOIN "
            "account_partial_reconcile aprc ON (aml.balance < 0 "
            "AND aml.id = aprc.credit_move_id) LEFT JOIN "
            "account_move_line amlcf ON (aml.balance < 0 "
            "AND aprc.debit_move_id = amlcf.id "
            "AND amlcf.date < %s ) LEFT JOIN "
            "account_partial_reconcile aprd ON (aml.balance > 0 "
            "AND aml.id = aprd.debit_move_id) LEFT JOIN "
            "account_move_line amldf ON (aml.balance > 0 "
            "AND aprd.credit_move_id = amldf.id "
            "AND amldf.date < %s ) "
            "WHERE aml.account_id IN %s AND aml.parent_state = 'posted'"
            "AND aml.date <= %s "
            "AND aml.currency_id IS NOT NULL "
            "GROUP BY aml.id "
            "HAVING aml.full_reconcile_id IS NULL "
            "OR (MAX(amldf.id) IS NULL AND MAX(amlcf.id) IS NULL)"
            ") SELECT account_id as id, partner_id, currency_id, "
            + ", ".join(self._sql_mapping.values())
            + " FROM amount "
            + (("WHERE " + where_clause) if where_clause else " ")
            + " GROUP BY account_id, currency_id, partner_id"
        )

        params = []
        params.append(revaluation_date)
        params.append(revaluation_date)
        params.append(tuple(self.ids))
        params.append(revaluation_date)
        params += where_clause_params
        return query, params
