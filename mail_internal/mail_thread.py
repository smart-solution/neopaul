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


class mail_thread_internal(osv.AbstractModel):
    """ Update partner to add a field about notification preferences """
    _name = "mail.thread"
    _inherit = ['mail.thread']

    def message_subscribe(self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):
        """ Filter partners to subscribe only employee users, unless mail_subscribe_manual
            key is provided in the context. """
        if context is None:
            context = {}
        if not context.get('mail_subscribe_manual'):
            partner_ids = self.pool['res.partner'].filter_internal_user(cr, uid, partner_ids, context=context)
        return super(mail_thread_internal, self).message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
