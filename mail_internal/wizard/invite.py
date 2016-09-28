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


class invite_wizard_internal(osv.AbstractModel):
    _name = 'mail.wizard.invite'
    _inherit = ['mail.wizard.invite']
    _description = 'Invite wizard'

    def add_followers(self, cr, uid, ids, context=None):
        """ Override to add 'manual' key meaning this is a manual follower subscription """
        context = dict(context, mail_subscribe_manual=True)
        print context
        return super(invite_wizard_internal, self).add_followers(cr, uid, ids, context=context)
