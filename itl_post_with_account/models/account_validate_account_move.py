from odoo import models, api, _, fields
from odoo.exceptions import UserError


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"
    
    itl_account_id = fields.Many2one('account.account', string="Account to post")

    def validate_move(self):
        if self._context.get('active_model') == 'account.move':
            domain = [('id', 'in', self._context.get('active_ids', [])), ('state', '=', 'draft')]
        elif self._context.get('active_model') == 'account.journal':
            domain = [('journal_id', '=', self._context.get('active_id')), ('state', '=', 'draft')]
        else:
            raise UserError(_("Missing 'active_model' in context."))

        moves = self.env['account.move'].search(domain).filtered('line_ids')
        if not moves:
            raise UserError(_('There are no journal items in the draft state to post.'))
        
        if self.itl_account_id:
            for move in moves:
                for line in move.invoice_line_ids:
                    line.account_id = self.itl_account_id
        
        result = super(ValidateAccountMove, self).validate_move()
        
        return result
