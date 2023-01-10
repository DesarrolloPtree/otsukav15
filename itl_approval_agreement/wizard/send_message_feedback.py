from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SendMessageFeedback(models.TransientModel):
    _name = 'send.message.feedback.agreement'
    _description = "Send Message Feedback Agreement"
    
    name = fields.Char(string="Reason")
    
    def send_message(self):
        if not self.name:
            raise UserError("Debe agregar un mensaje.")
        context = dict(self._context or {})
        
        approval_request_id = self.env['approval.request'].browse(context['active_id'])
        approval_request_id.action_refuse_confirm()
        
        if 'agreement_id' in context:
            agreement_id = self.env['agreement'].sudo().browse(context['agreement_id'])
            if agreement_id:
                agreement_id.message_post(body=self.name, subject="Approval request refused")
                agreement_id.state = 'rejected'
                approval_request_id.message_post(body=self.name, subject="Approval request refused")
