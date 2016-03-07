# -*- coding: utf-8 -*-
##############################################################################
#
#    Smart Solution bvba
#    Copyright (C) 2010-Today Smart Solution BVBA (<http://www.smartsolution.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################## 

from osv import osv, fields
from tools.translate import _

class project_sale_order_create(osv.osv_memory):

    _name = "project.sale.order.create"

    _columns = {
        'project_id': fields.many2one('project.project', 'Project', invisible=False),
        'order_id': fields.many2one('sale.order', 'Template Offer/Order'),
    }

    def so_create(self, cr, uid , ids, context=None):
       # Generate an sale order from a project
        for obj in self.browse(cr, uid, ids):
            vals = {}
            if obj.project_id.partner_id:
                
                if not obj.project_id.partner_id: 
                    raise osv.except_osv(_('Creation Error'), _('Please set a customer in the project')) 
                partner = self.pool.get('res.partner').browse(cr, uid, obj.project_id.partner_id.id)
                pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                fiscal_position = partner.property_account_position and partner.property_account_position.id or False
                salesman = partner.user_id and partner.user_id.id or uid
                salesteam = partner.section_id and partner.section_id.id or False

                vals['partner_id'] = partner.id
                vals['pricelist_id'] = pricelist
                vals['partner_invoice_id'] = partner.id
                vals['partner_order_id'] = partner.id
                vals['partner_contact_id'] = obj.project_id.contact_id.id or False
                vals['partner_shipping_id'] = obj.project_id.delivery_address_id and obj.project_id.delivery_address_id.id or partner.id
                vals['origin'] = obj.project_id.name
                vals['payment_term'] = payment_term
                vals['fiscal_position'] = fiscal_position
                vals['user_id'] = salesman
                vals['section_id'] = salesteam
                vals['project_id'] = obj.project_id.analytic_account_id.id

                if obj.order_id:
                    offer_id = self.pool.get('sale.order').copy(cr, uid, obj.order_id.id, vals, context)
                else:
                    offer_id = self.pool.get('sale.order').create(cr, uid, vals, context)

                if offer_id:

                    self.pool.get('project.project').write(cr, uid, [context['active_id']], {'neopaul_stage':'draft_offer'})

                    #Force store of sale_order_id function field 

                    #self.pool.get('project.project')._store_set_values(cr, uid, [obj.project_id.id], ['sale_order_id'], context)

                    view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','sale.order'),('name','=','sale.order.form')])
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Offer',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_id': offer_id,
                        'view_id': view_id[0],
                        'res_model': 'sale.order',
                        'context': context,
                        }
                else:
                    raise osv.except_osv(_('Creation Error'), _('Unable to create new offer')) 

            else:
                raise osv.except_osv(_('Offer Error'), _('Please add a customer to this project')) 

        return offer_id

project_sale_order_create()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
