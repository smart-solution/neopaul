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


class mail_notification_internal(osv.Model):
    """ Update partner to add a field about notification preferences """
    _name = "mail.notification"
    _inherit = ['mail.notification']

    def _notify(self, cr, uid, msg_id, partners_to_notify=None, context=None):
        """ Filter partners to notify only employee users if mail_post_internal
            key is provided in the context. """
        if context and context.get('mail_post_internal'):
            partner_ids = self.pool['res.partner'].filter_internal_user(cr, uid, partners_to_notify, context=context)
        else:
            partner_ids = partners_to_notify
        return super(mail_notification_internal, self)._notify(cr, uid, msg_id, partners_to_notify=partner_ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
