# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2013-Today OpenERP S.A. (<http://openerp.com>).
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

from openerp.osv import osv


class res_partner_internal(osv.Model):
    _name = "res.partner"
    _inherit = ['res.partner', 'mail.thread']

    def filter_internal_user(self, cr, uid, ids, context=None):
        """ Filter partners to have only partners that are users and members
            of base.group_user group (employees). """
        partner_ids = []
        model, group_employee_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'base', 'group_user')
        for partner in self.browse(cr, uid, ids, context=context):
            if not partner.user_ids:
                continue
            if not group_employee_id in [g.id for g in partner.user_ids[0].groups_id]:
                continue
            partner_ids.append(partner.id)
        return partner_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
