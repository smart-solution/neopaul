#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################

from osv import osv, fields
import netsvc

class sale_tender(osv.osv):
	
	_name = 'sale.tender'
	_description = 'sale tender'
	_columns = {
		'name': fields.char('name', size=64, required=True),
        'order_ids': fields.one2many('sale.order','tender_id',
            'Sale Orders'),
	}
sale_tender()

class sale_order(osv.osv):

    _name = "sale.order"
    _inherit = "sale.order"

    _columns = {
        'tender_id': fields.many2one('sale.tender', 'Sale Tender'),
    }

    def action_wait(self, cr, uid, ids, context=None):
        """ Cancel other sale orders in the tender when the order is confirmed """
        for so in self.browse(cr, uid, ids):
            if so.tender_id:
                for s in so.tender_id.order_ids:
                    if s.id != so.id: 
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'sale.order', s.id, 'cancel', cr)
        return super(sale_order, self).action_wait(cr, uid, ids, context=context)

sale_order()






# SAMPLES

#class sale_tender(osv.osv):
#	
#	_name = 'sale_tender'
#	_description = 'sale_tender'
#	_columns = {
#		'char': fields.char('char', size=64, required=True),
#		'integer': fields.integer('Integer'),
#		'float': fields.float('Float', digits=(16,2)),
#       'function': fields.function(_some_function, 
#       'related': fields.related(...
#	}
#sale_tender()

#    _defaults = {
#            'state': 'draft',
#    {

#    def create(self, cr, uid, vals, context=None):
#        ...
#        return super(sale_tender, self).create(cr, uid, vals, context=context)

#    def write(self, cr, uid, ids, vals, context=None):
#        ...
#        return super(sale_tender, self).write(cr, uid, ids, vals, context=context)

#    def copy(self, cr, uid, id, default={}, context=None):
#        ...
#        return super(account_invoice, self).copy(cr, uid, id, default=default, context=context)


#       raise osv.except_osv(_('No product found !'), _('Could not find any product for the code %s'%(val)))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
