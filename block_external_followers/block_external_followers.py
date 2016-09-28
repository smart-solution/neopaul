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

from openerp.osv import fields, osv

class mail_followers(osv.osv):
    _inherit = 'mail.followers'

    def create(self, cr, uid, vals, context=None):
        if 'partner_id' in vals and vals['partner_id']:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
            if not partner.employee:
                return False

            return super(mail_followers, self).create(cr, uid, vals, context=context)

        _columns = {
        }

mail_followers()

class mail_mail(osv.osv):
    _inherit = 'mail.mail'

    def create(self, cr, uid, vals, context=None):
        if 'subject' in vals and vals['subject']:
            if vals['subject'][0:9] == 'Invitation':
            	return False
        if 'mail_message_id' in vals and vals['mail_message_id']:
            mailmessage = self.pool.get('mail.message').browse(cr, uid, vals['mail_message_id'])
            if mailmessage.subject and mailmessage.subject[0:9] == 'Invitation':
                return False

            return super(mail_mail, self).create(cr, uid, vals, context=context)

    def send(self, cr, uid, ids, auto_commit=False, recipient_ids=None, context=None):
        if str(ids) == "[None]":
            return False

        return super(mail_mail, self).send(cr, uid, ids, auto_commit=auto_commit, recipient_ids=recipient_ids, context=context)

    _columns = {
    }

mail_mail()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
