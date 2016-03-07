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
from openerp.tools.translate import _

class neopaul_issue_project_create(osv.osv_memory):

    _name = 'neopaul.issue.project.create'
    _columns = {
        'name': fields.char('Project Name', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', invisible=True),
        'delivery_address_id': fields.many2one('res.partner', 'Delivery Place', required=True,
            domain="['|',('parent_id','=',partner_id),('id','=',partner_id)]"),
        'directory_name': fields.char('Directory Name', size=128),
    }    

    _defaults = {
#        'delivery_address_id' : lambda self,cr,uid,context={}: context.get('default_partner_id', False),
    }    

    def default_get(self, cr, uid, fields, context=None):
        value = super(neopaul_issue_project_create, self).default_get(cr, uid, fields, context)
        if 'active_id' in context and context['active_id']:
            issue = self.pool.get('project.issue').browse(cr, uid, context['active_id'])
            value['name'] = issue.name + " - herstelling"
            if issue.partner_id:
                value['partner_id'] = issue.partner_id.id
                value['delivery_address_id'] = issue.partner_id.id
        return value

    def onchange_address(self, cr, uid, ids, address_id, name, context=None):
        res = {} 
        address = self.pool.get('res.partner').browse(cr, uid, address_id)
        if address:
            if address.city:
                res['name'] = address.name + ' - herstelling'
        return {'value': res} 
      
    
    def project_generate(self, cr, uid, ids, context=None):
        # Create project from customer
        objs = self.browse(cr, uid, ids) 
        for obj in objs:
            project_id = self.pool.get('project.project').create(cr, uid, 
                    {'name':obj.name,
                        'partner_id':obj.partner_id.id,
                        'contact_id':obj.partner_id.id,
                        'delivery_address_id':obj.delivery_address_id.id})
            if project_id:
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','project.project'),('name','=','view.neopaul_project.form')])
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Project',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': project_id,
                    'view_id': view_id[0],
                    'res_model': 'project.project',
                    'context': context,
                    }
            else:
                raise osv.except_osv(_('Creation Error'), _('Unable to create new project')) 







# SAMPLES

#class neopaul_repair(osv.osv):
#	
#	_name = 'neopaul_repair'
#	_description = 'neopaul_repair'
#	_columns = {
#		'char': fields.char('char', size=64, required=True),
#		'integer': fields.integer('Integer'),
#		'float': fields.float('Float', digits=(16,2)),
#       'function': fields.function(_some_function, 
#       'related': fields.related(...
#	}
#neopaul_repair()

#    _defaults = {
#            'state': 'draft',
#    {

#    def create(self, cr, uid, vals, context=None):
#        ...
#        return super(neopaul_repair, self).create(cr, uid, vals, context=context)

#    def write(self, cr, uid, ids, vals, context=None):
#        ...
#        return super(neopaul_repair, self).write(cr, uid, ids, vals, context=context)

#    def copy(self, cr, uid, id, default={}, context=None):
#        ...
#        return super(account_invoice, self).copy(cr, uid, id, default=default, context=context)


#       raise osv.except_osv(_('No product found !'), _('Could not find any product for the code %s'%(val)))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
