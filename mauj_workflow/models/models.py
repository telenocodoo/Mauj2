# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),('shifting', 'Shifting to Daraz'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")

    @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id')
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        '''
        if not self.move_lines:
            self.state = 'draft'
        elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
            self.state = 'draft'
        elif all(move.state == 'cancel' for move in self.move_lines):
            self.state = 'cancel'
        elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
            self.state = 'done'
        else:
            relevant_move_state = self.move_lines._get_relevant_state_among_moves()
            if relevant_move_state == 'partially_available':
                self.state = 'assigned'
            else:
                self.state = relevant_move_state


    def shifting_to_daraz(self):
        return self.write({'state': 'shifting'})


class SaleOrder(models.Model):
    _inherit = "sale.order"
    client_order_ref=fields.Char("Order Customer Name")
    studio_phone_no=fields.Char("Phone No")
    studio_order_city=fields.Char("Order City Name")
    studio_store_name=fields.Many2one("res.store","Store Name")

    def action_view_invoice(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_view_invoice()
        rr_id = self.env['account.move'].sudo().search([('invoice_origin', '=', self.name)],limit=1)
        rr_id.write({'client_order_ref': self.client_order_ref,'studio_phone_no': self.studio_phone_no,'studio_order_city': self.studio_order_city,'studio_store_name': self.studio_store_name.id})
        return res



class AccountInvoice(models.Model):
    _inherit = "account.move"

    client_order_ref=fields.Char("Order Customer Name")
    studio_phone_no=fields.Char("Phone No")
    studio_order_city=fields.Char("Order City Name")
    studio_store_name=fields.Many2one("res.store","Store Name")