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

{
    'name': 'Internal Messaging Restrictions',
    'version': '1.0',
    'category': 'Social Network',
    'sequence': 2,
    'summary': 'Discussions, Mailing Lists, News',
    'description': """
DESCRIBE ME
    """,
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['mail'],
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'images': [
    ],
    'js': [
        'static/src/js/mail.js',
        'static/src/js/mail_followers.js',
    ],
    'qweb': [
        'static/src/xml/mail.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
