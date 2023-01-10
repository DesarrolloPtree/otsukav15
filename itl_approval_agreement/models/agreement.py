from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class Agreement(models.Model):
    _inherit = 'agreement'
    
    
    approval_request_id = fields.Many2one('approval.request', string="Approval request", readonly=True, store=True, copy=False)
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], related="approval_request_id.request_status")
    
    
    def send_to_approve(self):
        if self.is_template and not self.env.company.itl_agreement_tmp_approval_category_id:
            raise ValidationError("Approval category for agreement template is not configured.")
        if not self.is_template and not self.env.company.itl_agreement_approval_category_id:
            raise ValidationError("Approval category for agreement is not configured.")
            
        if self.is_template:
            category_id = self.env.company.itl_agreement_tmp_approval_category_id
        else:
            category_id = self.env.company.itl_agreement_approval_category_id

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Agreement - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': category_id.id,
            'agreement_id': self.id,
        }

        
        if not self.approval_request_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.approval_request_id
            for p in rec.product_line_ids:
                p.unlink()
            rec.write(vals)
            rec.action_draft()
            rec.action_confirm()
        
        self.sudo().approval_request_id = rec.id
        
        #self.sudo().state = 'to_approve'
        
        #self.message_post_with_view('itl_approval_agreement.message_approval_agreement_created_link',
        #            values={'self': rec, 'origin': self},
        #            subtype_id=self.env.ref('mail.mt_note').id)
        
        #rec.message_post_with_view('mail.message_origin_link',
        #            values={'self': rec, 'origin': self},
        #            subtype_id=self.env.ref('mail.mt_note').id)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if not self.approval_request_id:
            raise ValidationError("Falta la solicitud de aprobación.")
        else:
            if self.approval_status != 'approved':
                raise ValidationError("La solicitud de aprobación no está aprobada.")