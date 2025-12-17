# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _generate_pos_order_invoice(self):
        """Override to provide better validation for Dominican fiscal invoices
        and ensure NCF is generated before PDF.
        """
        moves = self.env['account.move']

        for order in self:
            _logger.warning("POS Order Invoice Debug: order=%s, partner_id=%s, partner.name=%s, to_invoice=%s",
                           order.name, order.partner_id.id, order.partner_id.name if order.partner_id else None, order.to_invoice)
            
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))
            
            # Check if this is a Dominican company with fiscal documents
            is_do_fiscal = (order.company_id.country_code == 'DO' and 
                           order.session_id.config_id.invoice_journal_id.l10n_latam_use_documents)
            
            if is_do_fiscal:
                # Validate partner has tax payer type configured
                partner = order.partner_id
                if not partner.l10n_do_dgii_tax_payer_type:
                    raise UserError(_(\
                        "El cliente '%s' no tiene configurado el Tipo de Contribuyente DGII.\\n\\n"\
                        "Por favor vaya a:\\n"\
                        "Contactos → %s → Pestaña 'Ventas y Compras' → Tipo de Contribuyente DGII"\
                    ) % (partner.name, partner.name))
                
                # Validate VAT for taxpayers
                if partner.l10n_do_dgii_tax_payer_type == 'taxpayer' and not partner.vat:
                    raise UserError(_(\
                        "El cliente '%s' está marcado como 'Contribuyente' pero no tiene RNC.\\n\\n"\
                        "Por favor vaya a:\\n"\
                        "Contactos → %s → Campo 'NIF/RNC' y agregue el RNC"\
                    ) % (partner.name, partner.name))

            move_vals = order._prepare_invoice_vals()
            new_move = order._create_invoice(move_vals)

            order.state = 'invoiced'
            new_move.sudo().with_company(order.company_id).with_context(**order._get_invoice_post_context())._post()

            moves += new_move
            payment_moves = order._apply_invoice_payments(order.session_id.state == 'closed')

            # CRITICAL: Invalidate cache and reload the move to get fresh data including NCF
            new_move.invalidate_recordset(['l10n_do_fiscal_number', 'name'])
            new_move = self.env['account.move'].browse(new_move.id)
            _logger.warning("POS NCF check before PDF: invoice=%s, ncf=%s", new_move.name, new_move.l10n_do_fiscal_number)

            # Update order name to include NCF for sync to POS client
            # This makes NCF available via JavaScript's this.name (like Colombia module does)
            if is_do_fiscal and new_move.l10n_do_fiscal_number:
                ncf = new_move.l10n_do_fiscal_number
                order.write({'name': f"{order.name} - NCF: {ncf}"})
                _logger.warning("POS Order name updated with NCF: %s", order.name)

            # Send and Print
            if self.env.context.get('generate_pdf', True):
                new_move.with_context(skip_invoice_sync=True)._generate_and_send()

            if order.session_id.state == 'closed':
                order._create_misc_reversal_move(payment_moves)

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves[0].id if len(moves) == 1 else False,
            'context': "{'move_type':'out_invoice'}",
        }
    
    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        _logger.warning("POS _prepare_invoice_vals Debug: partner_id=%s, journal_id=%s", 
                       vals.get('partner_id'), vals.get('journal_id'))
        return vals
    
    def _create_invoice(self, move_vals):
        _logger.warning("POS _create_invoice Debug: move_vals partner_id=%s, type=%s", 
                       move_vals.get('partner_id'), type(move_vals.get('partner_id')))
        invoice = super()._create_invoice(move_vals)
        _logger.warning("POS _create_invoice POST: invoice.id=%s, partner_id=%s, partner.id=%s", 
                       invoice.id, invoice.partner_id, invoice.partner_id.id if invoice.partner_id else None)
        return invoice

    def read_pos_data(self, data, config_id):
        """Override to include NCF data in sync response for Dominican orders."""
        result = super().read_pos_data(data, config_id)
        
        # Add NCF data for Dominican fiscal orders
        for order_data in result.get('pos.order', []):
            order = self.browse(order_data.get('id'))
            _logger.warning("read_pos_data: order=%s, account_move=%s, country=%s", 
                          order.name, order.account_move.id if order.account_move else None,
                          order.company_id.country_code)
            if order.account_move and order.company_id.country_code == 'DO':
                ncf = order.account_move.l10n_do_fiscal_number
                order_data['l10n_do_fiscal_number'] = ncf or False
                order_data['l10n_do_ncf_expiration_date'] = str(order.account_move.l10n_do_ncf_expiration_date) if order.account_move.l10n_do_ncf_expiration_date else False
                order_data['l10n_do_document_type'] = order.account_move.l10n_latam_document_type_id.name if order.account_move.l10n_latam_document_type_id else False
                _logger.warning("read_pos_data: Added NCF=%s to order %s", ncf, order.name)
        
        return result

