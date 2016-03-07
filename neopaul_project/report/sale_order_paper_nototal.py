# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from report import report_sxw

class order_email(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order_email, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lastname': self._get_lastname,
        })


    def _get_lastname(self, name, context=None):
        x = name.split(" ")
        y = x[:-1]
        res = ""
        for i in y:
            res += i + " " 
        return res[:-1]


report_sxw.report_sxw('report.neopaul.project.so.paper.nototal', 'sale.order', 'addons/neopaul_project/report/sale_order_paper_nototal.rml', parser=order_email, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

