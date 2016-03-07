# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _function_name_disp(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids):
            if partner.id:
                res[partner.id] = ''
                if partner.first_name:
                    res[partner.id] = partner.first_name
                if partner.first_name and partner.middle_name:
                    res[partner.id] = res[partner.id] + ' '
                if partner.middle_name:
                    res[partner.id] = res[partner.id] + partner.middle_name
                if partner.first_name and partner.last_name:
                    res[partner.id] = res[partner.id] + ' '
                if partner.last_name:
                    res[partner.id] = res[partner.id] + partner.last_name
        return res

    _columns = {
        'last_name': fields.char('Achternaam', len=64),
        'first_name': fields.char('Voornaam', len=64),
        'middle_name': fields.char('Tussenvoegsel', len=64),
        'initials': fields.char('Initialen', len=32),
        'name_disp': fields.function(_function_name_disp, string='Name', type='char'),
    }
    
    def onchange_name(self, cr, uid, ids, first_name, middle_name, last_name, context=None):
        res = {}
        name = ''
        if first_name:
            name = first_name
        if first_name and middle_name:
            name = name + ' '
        if middle_name:
            name = name + middle_name
        if (first_name or middle_name) and last_name:
            name = name + ' '
        if last_name:
            name = name + last_name
        res['name'] = name
        res['name_disp'] = name
        return {'value':res}

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
