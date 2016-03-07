#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import time
import collections

def iterable(obj):
    return isinstance(obj, collections.Iterable)

class res_partner(osv.osv):

    _inherit = 'res.partner'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Customer name must be unique'),
    ]

    def default_get(self, cr, uid, fields, context=None):
        """Set Dutch as default"""
        if context is None:
            context = {}
        result = super(res_partner,self).default_get(cr, uid, fields, context=context)

        country_id = self.pool.get('res.country').search(cr, uid, [('code','=','BE')])[0]
        result['country_id'] = country_id
        result['lang'] = 'nl_NL'
        return result

    def create(self, cr, uid, vals, context=None):
        """Set the reference as id + 100000"""
        res =  super(res_partner, self).create(cr, uid, vals, context=context)
        ref = res + 100000
        self.write(cr, uid, [res], {'ref':str(ref)})
        return res

res_partner()

class res_users(osv.osv):

    _inherit = 'res.users'

    _columns = {
        'initials': fields.char('Initials', size=8, required=True),
    }

res_users()

class res_user_team(osv.osv):

    _name = 'res.user.team'

    _columns = {
        'name': fields.char('Team', size=64, required=True),
    }

res_user_team()

class project_project(osv.osv):

    _name = 'project.project'
    _inherit = 'project.project'

    
    def _order_get(self, cr, uid, ids, name, args, context=None):
        # Get the validated order
        if not ids:
            return {}
        res = {}.fromkeys(ids, False)
        for project in self.browse(cr, uid, ids, context=context):
            so_ids = self.pool.get('sale.order').search(cr, uid, [('project_id','=',project.analytic_account_id.id)])
            for so in self.pool.get('sale.order').browse(cr, uid, so_ids):
                if so.state not in ['draft','sent','cancel']:
                    res[project.id] = so.id
                    break
        return res

    def _offers_get(self, cr, uid, ids, name, args, context=None):
        # Get the offers
        if not ids:
            return {}
        res = {}.fromkeys(ids, False)
        offer_ids = []
        for project in self.browse(cr, uid, ids, context=context):
            so_ids = self.pool.get('sale.order').search(cr, uid, [('project_id','=',project.analytic_account_id.id)])
            for so in self.pool.get('sale.order').browse(cr, uid, so_ids):
                if so.state in ['draft','sent','cancel']:
                    offer_ids.append(so.id)
                    break
        res[project.id] = offer_ids
        return res


    def create(self, cr, uid, vals, context=None):
        """ Create a sale tender at project creation """
        vals['sale_tender_id'] = self.pool.get('sale.tender').create(cr, uid, {'name':vals['name']})

        res =  super(project_project, self).create(cr, uid, vals, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        if type(ids) != type([]):
                ids = [ids] 
        for project in self.browse(cr, uid, ids):
            if 'partner_id' in vals and 'no_date_update' not in context and project.task_id:
                partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
                self.pool.get('project.task').write(cr, uid, [project.task_id.id], {'name':partner.name})
            if 'date' in vals and 'no_date_update' not in context and project.task_id:
                self.pool.get('project.task').write(cr, uid, [project.task_id.id], {'date_start':vals['date'], 'date_end':vals['date']})
            if 'user_id' in vals and 'no_date_update' not in context and project.task_id:
                self.pool.get('project.task').write(cr, uid, [project.task_id.id], {'user_id':vals['user_id']})
            if 'team_id' in vals and 'no_date_update' not in context and project.task_id:
                self.pool.get('project.task').write(cr, uid, [project.task_id.id], {'team_id':vals['team_id']})
	    if 'short_description' in vals and 'no_date_update' not in context and project.task_id:
                self.pool.get('project.task').write(cr, uid, [project.task_id.id], {'short_description':vals['short_description']})
        return super(project_project, self).write(cr, uid, ids, vals=vals, context=context)
    
#    def unlink(self, cr, uid, ids, context=context):
#        """Delete all task from this project"""
#        return super(project_project, self).unlink(cr, uid, ids, context=context)

    _columns = {
        'code': fields.char('Code', size=32, readonly=True),
        'design_voucher_ids' : fields.one2many('neopaul.project.design.voucher',
            'project_id', 'Design Vouchers'),
        'calculation_voucher_ids' : fields.one2many('neopaul.project.calculation.voucher',
            'project_id', 'Calculation Vouchers'),
        'production_order_ids' : fields.one2many('neopaul.production.order',
            'project_id', 'Production Orders'),
        'placement_voucher_ids' : fields.one2many('neopaul.placement.voucher',
            'project_id', 'Placement Vouchers'),
        'offer_ids' : fields.one2many('sale.order',
            'project_project_id', 'Offers'),
#        'offer_ids': fields.function(_offers_get, relation='project.project', type='one2many', method=True,string='Offers'), 
        'neopaul_stage': fields.selection([('draft_offer','Concept offerte'),('project_created','Project aangemaakt'),
            ('in_design','In ontwerp'),('waiting_computation','Wachten op calculatie'),('offer_sent','Offerte verstuurd'),('offer_cancel','Offerte Geannuleerd'),
            ('waiting_offer','Wachten op offerte'),('waiting_order','Wachten op productie'),
            ('in_production','In Productie'),
            ('done','Gedaan')],'Stage', translate=False),
        'manager_id': fields.many2one('res.users', 'Account Manager'),
        'contact_id': fields.many2one('res.partner', 'Contact 1'),
        'contact2_id': fields.many2one('res.partner', 'Contact 2'),
        'delivery_address_id': fields.many2one('res.partner', 'Delivery Address'),
        'invoice_address_id': fields.related('sale_order_id', 'partner_invoice_id', type="many2one", relation="res.partner", string='Invoicing Address', readonly=True),
        'date_preferred': fields.date('Preferred Date'),
        'shop_opening_dates': fields.char('Shop Openning Dates', size=64),
        'planning_permission': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Planning Permission', translate=True),
        'planning_permission_text': fields.char('Planning Permission', size=64),
        'particular_size': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Need of Measurement', translate=True),
        'particular_size_text': fields.char('Need of Measurement', size=64),
        'cabling_requirements_1': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'To set in advance ?', translate=True),
        'cabling_requirements_1_text': fields.char('To set in advance ?', size=64),
        'cabling_requirements_2': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Cable making invisible ?', translate=True),
        'cabling_requirements_2_text': fields.char('Cable making invisible ?', size=64),
        'cabling_requirements_3': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Place available for Transformator ?', translate=True),
        'cabling_requirements_3_text': fields.char('Place available for Transformator ?', size=64),
        'cabling_requirements_4': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'220v existing ?', translate=True),
        'cabling_requirements_4_text': fields.char('220v existing ?', size=64),
        'parking_1': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Need allowance ?', translate=True),
        'parking_1_text': fields.char('Need allowance ?', size=64),
        'parking_2': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Site accessible ?', translate=True),
        'parking_2_text': fields.char('Site accessible ?', size=64),
        'platform': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Platform needed ?', translate=True),
        'platform_text': fields.char('Platform needed ?', size=64),
        'platform_height': fields.integer('Platform Height'),
        'surface_1': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Unstable ground ?', translate=True),
        'surface_1_text': fields.char('Unstable ground ?', size=64),
        'surface_2': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Concrete anchor needed ?', translate=True),
        'surface_2_text': fields.char('Concrete anchor needed ?', size=64),
        'surface_3': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Surface', translate=True),
        'surface_3_text': fields.char('Surface', size=64),
        'surface_4': fields.char('Kind of surface ?', size=64),
        'surface_4': fields.char('Kind of surface ?', size=64),
        'surface_5': fields.char('Surface color ?', size=64),
        'existing_commercials_1': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Existing Sign ?', translate=True),
        'existing_commercials_1_text': fields.char('Existing Sign ?', size=64),
        'existing_commercials_2': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Sign to take away ?', translate=True),
        'existing_commercials_2_text': fields.char('Sign to take away ?', size=64),
        'existing_commercials_3': fields.selection([('ja','J'),('nee','N'),('nvt','NVT')],'Sign to stock ?', translate=True),
        'existing_commercials_3_text': fields.char('Sign to stock ?', size=64),
        'color_1': fields.char('Constuctions Color', size=64),
        'color_2': fields.char('Films Color', size=64),
        'lighting_type': fields.char('Lighting Type', size=64),
        'date_deadline_type': fields.selection([('Vast','Fixed'),('Variable','Variabel'),
            ('In deze week', 'In deze week'),('In overleg met de werfleider','In overleg met de werfleider')], 'Deadline Type', translate=True),
        'amount_quoted': fields.related('sale_order_id', 'amount_untaxed', string='Order Amount', type='float', readonly=True),
        'amount_advance': fields.float('Voorshot'),
        'amount_tam': fields.char('In regie', size=64),
        'amount_unit': fields.char('Volgens eenheidsprijzen', size=64),
        'sale_order_id': fields.function(_order_get, string="Sale Order", type="many2one", relation="sale.order", store=True),
        'sale_tender_id': fields.many2one('sale.tender', 'Sale Tender'),
        'so_line_ids': fields.related('sale_order_id','order_line', type='one2many', relation='sale.order.line', string='Sale order Lines', readonly=True),
        'description': fields.text('Description'),
        'team_id': fields.many2one('res.user.team', 'Team'),
        'task_id': fields.many2one('project.task', 'Related Task'),
        'create_date': fields.datetime("Aanmaakdatum", readonly=True),
        'production_checked': fields.boolean('Production Checked'),
        'production_start_date': fields.date('Startproductiedatum'),
	'short_description': fields.char('Short Description', size=128),
    }

    _defaults = {
        'neopaul_stage': 'project_created',
    }

    def production_start(self, cr, uid, ids, context=None):
        """ Check if production can be started """

        for project in self.browse(cr, uid, ids):
            so_exists = False
            if not project.date:
                raise osv.except_osv(_('Start Production'), _('Cannot Start Production\nNo end date has been given for this project')) 
            if not project.planning_permission or not \
                project.particular_size or not \
                project.cabling_requirements_1 or not \
                project.cabling_requirements_2 or not \
                project.cabling_requirements_3 or not \
                project.cabling_requirements_4 or not \
                project.parking_1 or not \
                project.parking_2 or not \
                project.platform or not \
                project.surface_1 or not \
                project.surface_2 or not \
                project.surface_4 or not \
                project.surface_5 or not \
                project.existing_commercials_1 or not \
                project.existing_commercials_2 or not \
                project.existing_commercials_3 or not \
                project.color_1 or not \
                project.color_2 or not \
                project.lighting_type:
                raise osv.except_osv(_('Start Production'), _('Cannot Start Production\nAll site information fields must be filled to start production')) 

            so_ids = self.pool.get('sale.order').search(cr, uid, [('project_id','=',project.analytic_account_id.id)])
            for so in self.pool.get('sale.order').browse(cr, uid, so_ids):
                if so.state not in ['draft','cancel']:
                    so_exists = True
                    break

            if not so_exists:
                raise osv.except_osv(_('Start Production'), _('Cannot Start Production\nNo sale order have been confirmed for this project')) 



            # Create and fill the Production Order
            prod_data = {
                'name': project.name,
                'project_id': project.id,
            }
            po_id = self.pool.get('neopaul.production.order').create(cr, uid, prod_data)

            for order_line in so.order_line:
                item_data = {
                    'name': order_line.product_id.name,
                    'description': order_line.name,
                    'production_order_id': po_id,
                }
                item_id = self.pool.get('neopaul.production.order.item').create(cr, uid, item_data)

            seq = self.pool.get('ir.sequence').get(cr, uid, 'neopaul.project.code')
            self.write(cr, uid, ids, {'code':seq, 'neopaul_stage':'in_production'}) 


        # Create a task to display in the planning tool    
        if project.partner_id:
            partner_name = project.partner_id.name
        else:
            partner_name = ' '

        task_id = self.pool.get('project.task').create(cr, uid, {
            'project_id': project.id,
            'name': partner_name,
            'date_start' : project.date or False,
            'date_end' : project.date or False,
            'user_id': project.user_id and project.user_id.id or False,
            'team_id': project.team_id and project.team_id.id or False,
	    'short_description': project.short_description,
        })
        self.write(cr, uid, [project.id], {'task_id':task_id,'production_start_date':time.strftime('%Y-%m-%d')})        

        
        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','neopaul.production.order'),('name','=','view.neopaul_production.order.form')])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Production Order',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': po_id,
            'view_id': view_id[0],
            'res_model': 'neopaul.production.order',
            'context': context,
            }

    def production_check(self, cr, uid, ids, context=None):
        """ Check if production can be started """

        for project in self.browse(cr, uid, ids):
            so_exists = False
            if not project.date:
                raise osv.except_osv(_('Start Production'), _('Cannot Start Production\nNo end date has been given for this project')) 
            if not project.planning_permission or not \
                project.particular_size or not \
                project.cabling_requirements_1 or not \
                project.cabling_requirements_2 or not \
                project.cabling_requirements_3 or not \
                project.cabling_requirements_4 or not \
                project.parking_1 or not \
                project.parking_2 or not \
                project.platform or not \
                project.surface_1 or not \
                project.surface_2 or not \
                project.surface_4 or not \
                project.surface_5 or not \
                project.existing_commercials_1 or not \
                project.existing_commercials_2 or not \
                project.existing_commercials_3 or not \
                project.color_1 or not \
                project.color_2 or not \
                project.lighting_type:
                raise osv.except_osv(_('Start Production'), _('Cannot Start Production\nAll site information fields must be filled to start production')) 

            so_ids = self.pool.get('sale.order').search(cr, uid, [('project_id','=',project.analytic_account_id.id)])
            for so in self.pool.get('sale.order').browse(cr, uid, so_ids):
                if so.state not in ['draft','cancel']:
                    so_exists = True
                    break

            if not so_exists:
                raise osv.except_osv(_('Start Production'), _('Cannot Start Production\nNo sale order have been confirmed for this project')) 

            self.write(cr, uid, ids, {'production_checked':True})

            return True

    def calc_voucher_generate(self, cr, uid, ids, context=None):
        """Generate the Calculation Voucher"""
        project = self.browse(cr, uid ,ids)[0]

        calc_voucher_vals = {}
        calc_voucher_vals['name'] = project.name
        calc_voucher_vals['description'] = project.description
        calc_voucher_vals['project_id'] = project.id
        calc_voucher_vals['customer_id'] = project.partner_id.id
        calc_voucher_vals['contact_address_id'] = project.contact_id.id
        calc_voucher_vals['manager_id'] = project.user_id.id
        calc_voucher_vals['date_deadline'] = project.date_preferred
        calc_voucher_vals['delivery_address_id'] = project.delivery_address_id.id
        calc_voucher_vals['foreseen_placement_date_type'] = project.date_deadline_type
        calc_voucher_vals['foreseen_placement_date'] = project.date
        calc_voucher_id =  self.pool.get('neopaul.project.calculation.voucher').create(cr, uid, calc_voucher_vals, context=context)

        # change the project stage
        if 'project_id' in calc_voucher_vals and calc_voucher_vals['project_id']:
            self.pool.get('project.project').write(cr, uid, calc_voucher_vals['project_id'], {'neopaul_stage':'waiting_computation'})

        self.log(cr, uid, ids[0], 'Calculation Voucher %s created'%(project.name))

        if calc_voucher_id:
            view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','neopaul.project.calculation.voucher'),('name','=','view.neopaul_project.calculation.voucher.form')])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Calculation Voucher',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': calc_voucher_id,
                'view_id': view_id[0],
                'res_model': 'neopaul.project.calculation.voucher',
                'context': context,
                }
        else:
            raise osv.except_osv(_('Creation Error'), _('Unable to create new calculation voucher')) 

        return calc_voucher_id


    def copy(self, cr, uid, id, default={}, context=None):
        obj = self.browse(cr, uid, id)
        default.update({'sale_order_id':False})
        default.update({'sale_tender_id':False})
        default.update({'so_line_ids':False})
        default.update({'design_voucher_ids':False})
        default.update({'calculation_voucher_ids':False})
        default.update({'production_order_ids':False})
        default.update({'placement_voucher_ids':False})
        default.update({'offer_ids':False})
        return super(project_project, self).copy(cr, uid, id, default=default, context=context)

project_project()


class project_task(osv.osv):

    _inherit = 'project.task'

    _columns = {
        'team_id': fields.many2one('res.user.team', 'Project'),
	'short_description': fields.char('Short Description', size=128),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        for task in self.browse(cr, uid, ids):
            if 'date_start' in vals:
                vals['date_end'] = vals['date_start']
                context['no_date_update'] = True
                self.pool.get('project.project').write(cr, uid, [task.project_id.id], {'date':vals['date_start']}, context=context)
        return super(project_task, self).write(cr, uid, ids, vals=vals, context=context)

project_task()

class account_analytic_account(osv.osv):

    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique'),
    ]

account_analytic_account()


class neopaul_project_design_voucher(osv.osv):
    
    _name = 'neopaul.project.design.voucher'
    _description = 'Project Design Voucher (Ontwerpbon)'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'design_ids': fields.one2many('neopaul.project.design', 'design_voucher_id', 'Designs'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'manager_id': fields.many2one('res.users', 'Account Manager'),
        'designer_id': fields.many2one('res.users', 'Designer'),
        'contact_address_id': fields.many2one('res.partner', 'Contact 1'),
        'contact2_address_id': fields.many2one('res.partner', 'Contact 2'),
        'delivery_address_id': fields.many2one('res.partner', 'Delivery Address'),
        'date_deadline': fields.date('Deadline'),
        'date_preferred': fields.date('Preferred Date'),
        'facade_color': fields.char('Facade Color', size=64),
        'facade_type': fields.char('Facade Type', size=64),
        'viewing_situation': fields.char('Viewing Situation', size=64),
        'budget': fields.char('Budget', size=64),
        'atmosphere': fields.char('Atmosphere',size=128),
        'description': fields.text('description'),
        'website': fields.char('Website', size=64),
        'calc_voucher_id': fields.many2one('neopaul.project.calculation.voucher',
            'Calculation Voucher'),
        'state': fields.selection([('pending','In Progress'),('done','Done')],'State'),
        'create_date': fields.datetime("Aanmaakdatum", readonly=True),
    }

    _defaults = {
        'state': 'pending',
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(neopaul_project_design_voucher, self).default_get(cr, uid, fields, context=context)
        if 'default_project_id' in context and context['default_project_id']:
            project = self.pool.get('project.project').browse(cr, uid, context['default_project_id'])
            if 'customer_id' in fields:
                res.update({'customer_id':project.partner_id.id})
                # Compute the name
                name_res = self.search(cr, uid, [('name','like', project.name + '%')])
                name = project.name + '-' + str(len(name_res)+1).zfill(2)
                res.update({'name':name})
            if 'manager_id' in fields:
                res.update({'manager_id':project.user_id.id})
            if 'contact_address_id' in fields:
                res.update({'contact_address_id':project.contact_id.id})
            if 'contact2_address_id' in fields:
                res.update({'contact2_address_id':project.contact2_id.id})
            if 'delivery_address_id' in fields:
                res.update({'delivery_address_id':project.delivery_address_id.id})
            if 'date_preferred' in fields:
                res.update({'date_preferred':project.date_preferred})
            if 'date_deadline' in fields:
                res.update({'date_deadline':project.date})
        return res 

    def onchange_project(self, cr, uid, ids, project_id, context=None):
        res = {}
        project = self.pool.get('project.project').browse(cr, uid, project_id)
        if project:
            if project.partner_id:
                res.update({'customer_id':project.partner_id.id})
                # Compute the name
                name_res = self.search(cr, uid, [('name','like', project.name + '%')])
                name = project.name + '-' + str(len(name_res)+1).zfill(2)
                res.update({'name':name})
            if project.user_id:
                res.update({'manager_id':project.user_id.id})
            if project.contact_id:
                res.update({'contact_address_id':project.contact_id.id})
            if project.contact2_id:
                res.update({'contact2_address_id':project.contact2_id.id})
            if project.delivery_address_id:
                res.update({'delivery_address_id':project.delivery_address_id.id})

        return {'value': res}

    def dv_print(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        #self.write(cr, uid, ids, {}, context=context)
        datas = {
             'ids': ids,
             'model': 'neopaul.project.design.voucher',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'neopaul.project.design.voucher',
            'datas': datas,
            'nodestroy' : True
        }
  


    def create(self, cr, uid, vals, context=None):
        """ change the project stage """
        if 'project_id' in vals and vals['project_id']:
            self.pool.get('project.project').write(cr, uid, vals['project_id'], {'neopaul_stage':'in_design'})
        return super(neopaul_project_design_voucher, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default={}, context=None):
        """ Compute the name at duplication and remove the relation to the Calculation Voucher"""
        obj = self.browse(cr, uid, id)
        if obj.project_id:
            name_res = self.search(cr, uid, [('name','like', obj.project_id.name + '%')])
            name = obj.project_id.name + '-' + str(len(name_res)+1).zfill(2)
            default.update({'name':name})
            default.update({'calc_voucher_id':False})
        return super(neopaul_project_design_voucher, self).copy(cr, uid, id, default=default, context=context)

    def calc_voucher_generate(self, cr, uid, ids, context=None):
        """Generate the Calculation Voucher"""
        design_voucher = self.browse(cr, uid ,ids)[0]

        if design_voucher.calc_voucher_id:
            raise osv.except_osv(_('Creation Error'), _('A calculation voucher already exists for this design voucher')) 

        calc_voucher_vals = {}
        calc_voucher_vals['name'] = design_voucher.name
        calc_voucher_vals['description'] = design_voucher.description
        calc_voucher_vals['project_id'] = design_voucher.project_id.id
        calc_voucher_vals['design_voucher_id'] = design_voucher.id
        calc_voucher_vals['customer_id'] = design_voucher.customer_id.id
        calc_voucher_vals['contact_address_id'] = design_voucher.contact_address_id.id
        calc_voucher_vals['manager_id'] = design_voucher.manager_id.id
        calc_voucher_vals['date_deadline'] = design_voucher.date_deadline
        calc_voucher_vals['delivery_address_id'] = design_voucher.delivery_address_id.id
        calc_voucher_vals['foreseen_placement_date_type'] = design_voucher.project_id.date_deadline_type
        calc_voucher_vals['foreseen_placement_date'] = design_voucher.project_id.date
        calc_voucher_vals['project_id'] = design_voucher.project_id.id
        calc_voucher_id =  self.pool.get('neopaul.project.calculation.voucher').create(cr, uid, calc_voucher_vals, context=context)
        self.write(cr, uid , ids, {'calc_voucher_id':calc_voucher_id})

        # change the project stage
        if 'project_id' in calc_voucher_vals and calc_voucher_vals['project_id']:
            self.pool.get('project.project').write(cr, uid, calc_voucher_vals['project_id'], {'neopaul_stage':'waiting_computation'})

        # Create computation lines
        for design in design_voucher.design_ids:
            calc_line_id =  self.pool.get('neopaul.project.calculation.voucher.line').create(cr, uid, 
                {'name':design.description,
                'product_id':design.name.id,
                'amount':design.amount, 
                'calc_voucher_id':calc_voucher_id},
                context=context)

        self.log(cr, uid, ids[0], 'Calculation Voucher %s created'%(design_voucher.name))

        if calc_voucher_id:
            view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','neopaul.project.calculation.voucher'),('name','=','view.neopaul_project.calculation.voucher.form')])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Calculation Voucher',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': calc_voucher_id,
                'view_id': view_id[0],
                'res_model': 'neopaul.project.calculation.voucher',
                'context': context,
                }
        else:
            raise osv.except_osv(_('Creation Error'), _('Unable to create new calculation voucher')) 

        return calc_voucher_id

neopaul_project_design_voucher()

class neopaul_project_design(osv.osv):
    
    _name = 'neopaul.project.design'
    _description = 'Project Design'
    _columns = {
        #'name': fields.char('Name', size=64, required=True),
        'name': fields.many2one('product.product','Name', required=True),
        'code': fields.char('Code', size=64, required=True),
        'design_voucher_id': fields.many2one('neopaul.project.design.voucher', 'Design Voucher'),
        'project_id': fields.related('design_voucher_id', 'project_id', string='Project', type='many2one', relation='project.project', readonly=True),
        'amount': fields.float('Amount'),
        'image': fields.binary('Image'),
        'description': fields.text('description', required=True),
        'state': fields.selection([('draft','Draft'),('inprogress','In Progress'),('done','Done'),('refused','Refused'),('accepted','Accepted')],'State'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(neopaul_project_design, self).default_get(cr, uid, fields, context=context)
        if 'default_design_voucher_id' in context and context['default_design_voucher_id']:
            voucher = self.pool.get('neopaul.project.design.voucher').browse(cr, uid, context['default_design_voucher_id'])
            if voucher.manager_id and voucher.designer_id:
                # Compute the code
                code_res = self.search(cr, uid, [('code','like',
                    voucher.manager_id.initials + '-' + voucher.designer_id.initials + '-' + '%'),('project_id','=',voucher.project_id.id)])
                code = voucher.manager_id.initials + '-' + voucher.designer_id.initials + '-' + str(len(code_res)+1).zfill(2)
                res.update({'code':code})
        return res 

    def onchange_design_voucher(self, cr, uid, ids, voucher_id, context=None):
        res = {}
        voucher = self.pool.get('neopaul.project.design.voucher').browse(cr, uid, voucher_id)
        if voucher:
            if voucher.manager_id and voucher.designer_id:
                # Compute the code
                code_res = self.search(cr, uid, [('code','like',
                    voucher.manager_id.initials + '-' + voucher.designer_id.initials + '-' + '%'),('project_id','=',voucher.project_id.id)])
                code = voucher.manager_id.initials + '-' + voucher.designer_id.initials + '-' + str(len(code_res)+1).zfill(2)
                res.update({'code':code})

        return {'value': res}

    _defaults = {
        'state': 'draft',
    }
neopaul_project_design()

class neopaul_project_create(osv.osv_memory):

    _name = 'neopaul.project.create'
    _columns = {
        'name': fields.char('Project Name', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', invisible=True),
        'delivery_address_id': fields.many2one('res.partner', 'Delivery Place', required=True,
            domain="['|',('parent_id','=',partner_id),('id','=',partner_id)]"),
        'directory_name': fields.char('Directory Name', size=128),
    }

    _defaults = {
        'delivery_address_id' : lambda self,cr,uid,context={}: context.get('default_partner_id', False),
    }

    def default_get(self, cr, uid, fields, context=None):
        value = super(neopaul_project_create, self).default_get(cr, uid, fields, context)
        if 'partner_id' in context and context['partner_id']:
            partner = self.pool.get('res.partner').browse(cr, uid, context['partner_id'])
            if partner:
                value['name'] = partner.name
        return value

    def onchange_address(self, cr, uid, ids, address_id, name, context=None):
        res = {}
        address = self.pool.get('res.partner').browse(cr, uid, address_id)
        if address:
            if address.city:
                res['name'] = address.name + ' (' + address.city + ')'
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
        return True

neopaul_project_create()

class neopaul_project_calculation_voucher(osv.osv):

    _name = 'neopaul.project.calculation.voucher'
    _description = 'Project calculation Voucher'

    def _total_amount(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        for calc_voucher in self.browse(cr, uid, ids, context=context):
            res[calc_voucher.id] = 0.0
            for calc_line in calc_voucher.calc_voucher_line_ids:
                res[calc_voucher.id] += calc_line.amount
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'design_voucher_id': fields.many2one('neopaul.project.design.voucher', 'Design Voucher'),
        'amount': fields.float('Total Amount'),
        'description': fields.text('description'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'manager_id': fields.many2one('res.users', 'Account Manager'),
        'contact_address_id': fields.many2one('res.partner', 'Contact 1'),
        'contact2_address_id': fields.many2one('res.partner', 'Contact 2'),
        'delivery_address_id': fields.many2one('res.partner', 'Delivery Address'),
        'date_deadline': fields.date('Deadline'),
        'calc_voucher_line_ids': fields.one2many('neopaul.project.calculation.voucher.line',
            'calc_voucher_id', 'Lines'),
        'total_amount': fields.function(_total_amount, string="Total Amount", type="float", store=False),
        'sale_order_id': fields.many2one('sale.order', 'Offer'),
        'has_commision': fields.selection([('ja','Ja'),('nee','Nee')],'Commission', translate=True),
        'commision_rate': fields.float('Commission Rate (%)'),
        'foreseen_placement_date_type': fields.selection([('Vast','Fixed'),('Variable','Variabel'),
            ('In deze week', 'This week'),('In overleg met de werfleider','In overleg met de werfleider')], 'Foreseen Placement date', translate=True),
        'foreseen_placement_date': fields.date('Foreseen Placement date'),
        'state': fields.selection([('pending','Pending'),('done','Done')], 'State', readonly=False),
        'project_id': fields.many2one('project.project', 'Project'),
        'create_date': fields.datetime("Aanmaakdatum", readonly=True),
        }

    _defaults = {
        'state': 'pending',
    }


    def default_get(self, cr, uid, fields, context=None):
        value = super(neopaul_project_calculation_voucher, self).default_get(cr, uid, fields, context)
        if 'default_design_voucher_id' in context and context['default_design_voucher_id']:
            raise osv.except_osv(_('Creation Error'), _('Please use the "Generate Calculation Voucher" button')) 
        return value
    def default_get(self, cr, uid, fields, context=None):
        value = super(neopaul_project_calculation_voucher, self).default_get(cr, uid, fields, context)
        if 'default_design_voucher_id' in context and context['default_design_voucher_id']:
            raise osv.except_osv(_('Creation Error'), _('Please use the "Generate Calculation Voucher" button')) 
        return value

    def offer_generate(self, cr, uid, ids, context=None):
        """ Generate the Offer """
        # Need a desing product for the taxes computation
#        design_prod_id = self.pool.get('product.product').search(cr, uid, [('name','=','design')])
#        if not design_prod_id:
#            raise osv.except_osv(_('Design Product Error'), _('Please create a service product called design')) 
#        design_prod = self.pool.get('product.product').browse(cr, uid, design_prod_id[0])

        print "CALC CONTEXT:",context
            
        calc_vouchers = self.browse(cr, uid, ids)
 
        for calc_voucher in calc_vouchers: 
            if not calc_voucher.customer_id:
                raise osv.except_osv(_('Customer Error'), _('Please add a customer to this calculation voucher')) 
            addr = self.pool.get('res.partner').address_get(cr, uid, [calc_voucher.customer_id.id], ['delivery', 'invoice', 'contact'])
            part = self.pool.get('res.partner').browse(cr, uid, calc_voucher.customer_id.id)
#            if not part.vat:
#                raise osv.except_osv(_('Customer VAT Error'), _('Please add a vat number to the customer %s'%(part.name))) 

            pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
            payment_term = part.property_payment_term and part.property_payment_term.id or False
            fiscal_position = part.property_account_position and part.property_account_position.id or False
            dedicated_salesman = part.user_id and part.user_id.id or uid
            offer_val = {
                'partner_id': calc_voucher.customer_id.id,
                'partner_invoice_id': addr['invoice'],
                'partner_order_id': addr['contact'],
                'partner_shipping_id': calc_voucher.delivery_address_id and \
                    calc_voucher.delivery_address_id.id or addr['delivery'],
                'partner_contact_id': calc_voucher.contact_address_id and calc_voucher.contact_address_id.id or addr['contact'],
                'payment_term': payment_term,
                'fiscal_position': fiscal_position,
                'user_id': dedicated_salesman,
                'calc_voucher_id': calc_voucher.id,
                'tender_id': calc_voucher.project_id.sale_tender_id.id,
                'project_id': calc_voucher.project_id.analytic_account_id.id,
            }

            if pricelist:
                offer_val['pricelist_id'] = pricelist
            else:
                list = self.pool.get('product.pricelist').search(cr, uid, [('type','=','sale')])
                if plist:
                    offer_val['pricelist_id'] = plist[0]
                else:
                    raise osv.except_osv(_('Pricelist Error'), _('No Pricelist could be found')) 

            offer_id = self.pool.get('sale.order').create(cr, uid, offer_val, context=context)
            self.write(cr, uid, ids, {'sale_order_id':offer_id})

            if offer_id: 
                for line in calc_voucher.calc_voucher_line_ids:
                    if line.selected:
                        prod_val = self.pool.get('sale.order.line').product_id_change(cr, uid, None,
                            offer_val['pricelist_id'], line.product_id.id, partner_id=part.id,
                            fiscal_position=fiscal_position, update_tax=True)
                        product = line.product_id and line.product_id.id or False
                        offer_line_val = {             
                            'name': line.name,
                            'product_id': line.product_id.id,
                            'order_id': offer_id,
                            'discount': line.discount,
                            'price_unit': line.amount,
                            #'notes': line.description,
                            'tax_id': [(6,0,prod_val['value']['tax_id'])],
                        }
                        offer_line_id = self.pool.get('sale.order.line').create(cr, uid, offer_line_val, context=context)

            if calc_voucher.design_voucher_id and calc_voucher.design_voucher_id.project_id:
                self.pool.get('project.project').write(cr, uid, [calc_voucher.design_voucher_id.project_id.id], {'neopaul_stage':'waiting_order'})

            if offer_id:
                self.write(cr, uid, ids, {'state':'done'})
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','sale.order'),('name','=','sale.order.form')])
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Offer',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': offer_id,
                    'view_id': view_id[0],
                    'res_model': 'sale.order',
                    'context': context,
                    }
            else:
                raise osv.except_osv(_('Creation Error'), _('Unable to create new offer')) 

        return True


neopaul_project_calculation_voucher()

class neopaul_project_calculation_voucher_line(osv.osv):

    _name = 'neopaul.project.calculation.voucher.line'
    _description = 'Project Calculation Voucher Line'
    _columns = {
        'name': fields.text('Name', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'calc_voucher_id': fields.many2one('neopaul.project.calculation.voucher', 'Calculation Voucher'),
        'discount': fields.float('Discount (%)'),
        'amount': fields.float('Amount'),
        'description': fields.text('description'),
        'selected': fields.boolean('Selected'),
    }

    _defaults = {
        'selected': True,
    }

    def onchange_product(self, cr, uid, ids, product_id, context=None):
        res = {}
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        if product:
            res.update({'name':product.name})
            res.update({'amount':product.list_price})
        return {'value': res}

neopaul_project_calculation_voucher_line()

class sale_order(osv.osv):

    _name = 'sale.order'
    _inherit = 'sale.order'

    def _order_get(self, cr, uid, ids, name, args, context=None):
        # Get the validated order
        if not ids:
            return {}
        res = {}.fromkeys(ids, False)
        for project in self.browse(cr, uid, ids, context=context):
            so_ids = self.pool.get('sale.order').search(cr, uid, [('project_id','=',project.analytic_account_id.id)])
            for so in self.pool.get('sale.order').browse(cr, uid, so_ids):
                if so.state not in ['draft','cancel']:
                    res[project.id] = so.id
                    break
        return res

    def _project_get(self, cr, uid, ids, name, args, context=None):
        # Get the project from the analytic account
        if not ids:
            return {}
        res = {}.fromkeys(ids, False)
        for order in self.browse(cr, uid, ids, context=context):
            project_id = self.pool.get('project.project').search(cr, uid, [('analytic_account_id','=',order.project_id.id)])
            if project_id:
                res[order.id] = project_id[0]
        return res

    _columns = {
            'calc_voucher_id': fields.many2one('neopaul.project.calculation.voucher','Calculation Voucher'),
            'partner_contact_id': fields.many2one('res.partner', 'Contact Address', required=False),
            'project_project_id': fields.function(_project_get, string="Project", type="many2one", relation="project.project", store=True),
    } 


    def action_button_confirm(self, cr, uid, ids, context=None):
        for so in self.browse(cr, uid, ids):
            part = so.partner_invoice_id
            if not part.vat and part.vat_subjected:
                raise osv.except_osv(_('Customer VAT Error'), _('Please add a vat number to the customer %s'%(part.name))) 
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        

    def action_wait(self, cr, uid, ids, context=None):
        """ Force store=True in project for sale_order_id field """
        res = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        if type(ids) != type([]):
            ids = [ids]
        for so in self.browse(cr, uid, ids):
            if so.project_id:
                project_ids = self.pool.get('project.project').search(cr, uid, [('analytic_account_id','=',so.project_id.id)])  
                if project_ids:
                    self.pool.get('project.project')._store_set_values(cr, uid, project_ids, ['sale_order_id'], context)
        return res 

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order,self).write(cr, uid, ids, vals, context=context)

	if type(ids) != type([]):
	    ids = [ids]

	orders = self.browse(cr, uid, ids)

        for so in orders:
            if so.state == 'sent' and so.project_project_id:
                self.pool.get('project.project').write(cr, uid, [so.project_project_id.id], {'neopaul_stage':'offer_sent'})
            if so.state == 'cancel' and so.project_project_id:
                self.pool.get('project.project').write(cr, uid, [so.project_project_id.id], {'neopaul_stage':'offer_cancel'})

        return res


    def _prepare_invoice(self, cr, uid, order, lines, context=None):

        res = super(sale_order, self)._prepare_invoice(
            cr, uid, order, lines, context=context
        )
        res.update({
            'contact_id': order.partner_invoice_id.id, })

        return res        

sale_order()


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

    _defaults = {
        'delay': 42,
        'type': 'make_to_order',
    }

sale_order_line()


class account_payment_term(osv.osv):

    _name="account.payment.term"
    _inherit="account.payment.term"

    _columns = {
        'sales_conditions': fields.text('Sales Conditiones', translate=True),
    }
account_payment_term()


class purchase_order(osv.osv):

    _name = "purchase.order"
    _inherit = "purchase.order"

    _columns = {
        'production_order_id': fields.many2one('neopaul.production.order', 'Production Order'),
        'quality_checked': fields.selection([('ja','Ja'),('nee','Nee')],'Quality Check', translate=True),
        'project_id': fields.many2one('project.project', 'Project'),
        'parent_partner_id': fields.related('partner_id', 'parent_id', type='many2one', relation='res.partner', string='Parent Partner'),
    }

    _defaults = {
        'quality_checked': 'no',
    }

purchase_order()


class purchase_order_line(osv.osv):

    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    # TODO : Get the analytic acccount from the production order project
    def default_get(self, cr, uid, fields, context=None):
        res = super(purchase_order_line, self).default_get(cr, uid, fields, context=context)
        if 'production_order_id' in context and context['production_order_id']:
            prod_order = self.pool.get('neopaul.production.order').browse(cr, uid, context['production_order_id'])
            project = prod_order.project_id
            #project = self.pool.get('project.project').browse(cr, uid, context['project_id'])
            if 'customer_id' in fields:
                res.update({'customer_id':project.partner_id.id})
                # Compute the name
                name_res = self.search(cr, uid, [('name','like', project.name + '%')])
                name = project.name + '-' + str(len(name_res)+1).zfill(2)
                res.update({'name':name})
            if 'contact_address_id' in fields:
                res.update({'contact_address_id':project.contact_id.id})
            if 'contact2_address_id' in fields:
                res.update({'contact2_address_id':project.contact2_id.id})
            if 'delivery_address_id' in fields:
                res.update({'delivery_address_id':project.delivery_address_id.id})
            if 'date_preferred' in fields:
                res.update({'date_preferred':project.date_preferred})
        return res 

purchase_order_line()


class neopaul_production_order(osv.osv):

    _name = "neopaul.production.order"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'customer_id': fields.related('project_id', 'partner_id', string='Customer', type='many2one', relation='res.partner', readonly=True, store=False),
        'account_manager_id': fields.related('project_id', 'user_id', string='Account Manager', type='many2one', relation='res.users', readonly=False, store=True),
        'item_ids': fields.one2many('neopaul.production.order.item', 'production_order_id', 'Items'),
        'purchase_order_ids': fields.one2many('purchase.order', 'production_order_id', 'Purchase Orders'),
        'packing_ids': fields.one2many('neopaul.production.order.packing', 'production_order_id', 'Packing Lists'),
        'state': fields.selection([('pending','Pending'),('validated','Validated'),('done','Done')],'State', readonly=True),
        'printing_date': fields.datetime('Printing Date'),
    }

    _defaults = {
        'state': 'pending',
    }

    def prod_order_validate(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'validated'})

    def prod_order_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'})

    def prod_order_reset(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'pending'})

    def placement_voucher_generate(self, cr, uid, ids, context=None):
        # Generate the placement voucher
        prod_order = self.browse(cr, uid, ids)[0]
        placement_voucher_id = self.pool.get('neopaul.placement.voucher').create(cr, uid, {'name':prod_order.name,
            'production_order_id':prod_order.id})

        if placement_voucher_id:
            view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','neopaul.placement.voucher'),('name','=','view.neopaul_placement.voucher.form')])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Placement Voucher',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': placement_voucher_id,
                'view_id': view_id[0],
                'res_model': 'neopaul.placement.voucher',
                'context': context,
                }
        else:
            raise osv.except_osv(_('Creation Error'), _('Unable to create placement voucher')) 
        return  False 

neopaul_production_order()


class neopaul_production_order_item(osv.osv):

    _name = "neopaul.production.order.item"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'production_order_id': fields.many2one('neopaul.production.order', 'Production Order', ondelete="cascade", required=True),
    }
neopaul_production_order_item()

class neopaul_production_order_packing(osv.osv):

    _name = "neopaul.production.order.packing"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'production_order_id': fields.many2one('neopaul.production.order', 'Production Order', ondelete="cascade", required=True),
        'quality_checked': fields.selection([('ja','Ja'),('nee','Nee')],'Quality Check', translate=True),
    }

    _defaults = {
        'quality_checked': 'no',
    }

neopaul_production_order_packing()

class neopaul_placement_voucher(osv.osv):

    _name = 'neopaul.placement.voucher'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'production_order_id': fields.many2one('neopaul.production.order', 'Production Order', ondelete="cascade", required=True),
        'project_id': fields.related('production_order_id', 'project_id', type='many2one', relation='project.project', string='Project', readonly=True, store=True),
        'customer_id': fields.related('production_order_id', 'project_id', 'partner_id', string='Customer', type='many2one', relation='res.partner', readonly=True),
        'account_manager_id': fields.related('production_order_id', 'project_id', 'user_id', string='Account Manager', type='many2one', relation='res.users', readonly=True),
        'contact_id': fields.related('production_order_id', 'project_id', 'contact_id', string='Contact', type='many2one', relation='res.partner', readonly=True),
        'delivery_id': fields.related('production_order_id', 'project_id', 'delivery_address_id', string='Delivery Address', type='many2one', relation='res.partner', readonly=True),
        'designdrawing': fields.selection([('ja','J'),('nee','N')],'Onwerptekening ?', translate=True),
        'simulationdrawing': fields.selection([('ja','J'),('nee','N')],'Simulatietekening', translate=True),
        'customerplan': fields.selection([('ja','J'),('nee','N')],'Plannen van klant', translate=True),
        'note': fields.text('Belangrijke Informatie'),
        'state': fields.selection([('pending','Pending'),('done','Done')],'State', readonly=True),
    }

    _defaults = {
        'state': 'pending',
    }

    def prod_order_close(self, cr, uid, ids, context=None):
        """Set project as done"""        
        pvs = self.browse(cr, uid, ids)
        for pv in pvs:
            self.pool.get('project.project').write(cr, uid, [pv.project_id.id], {'neopaul_stage':'done'}) 
        return self.write(cr, uid, ids, {'state':'done'})

    def prod_order_reset(self, cr, uid, ids, context=None):
        pvs = self.browse(cr, uid, ids)
        for pv in pvs:
            self.pool.get('project.project').write(cr, uid, [pv.project_id.id], {'neopaul_stage':'in_production'}) 
        return self.write(cr, uid, ids, {'state':'pending'})

neopaul_placement_voucher()

class res_company(osv.osv):

    _name = 'res.company'
    _inherit = 'res.company'
    _columns = {
        'so_legal_notice1': fields.text('Neopaul Legal Notice 1'),
    }

res_company()

class calc_sale_order_create(osv.osv_memory):

    _name = "calc.sale.order.create"

    _columns = {
        'project_id': fields.many2one('project.project', 'Project', invisible=False),
        'order_id': fields.many2one('sale.order', 'Template Offer/Order'),
    }

    def calc_create(self, cr, uid , ids, context=None):
        # Generate an calculation voucher from a project
        return self.pool.get('project.project').calc_voucher_generate(cr, uid, context['active_ids'], context=context)

calc_sale_order_create()

class stock_picking_in(osv.osv):

    _inherit = 'stock.picking.in'

    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',
            ondelete='set null', select=True),
        'project_id': fields.related('purchase_id','project_id', type='many2one', relation='project.project', string='Project', store=False, readonly=True),
    }

class account_invoice_vat_note(osv.osv):

    _name = 'account.invoice.vat.note'

    _columns = {
	'name': fields.char('Name', size=256, required=True, translate=True),
    } 

class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    def _project_get(self, cr, uid, ids, name, args, context=None):
        # Get the project from the analytic account
        if not ids: 
            return {}
        res = {}.fromkeys(ids, False)
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.invoice_line:
                project_id = self.pool.get('project.project').search(cr, uid, [('analytic_account_id','=',invoice.invoice_line[0].account_analytic_id.id)])
                if project_id:
                    res[invoice.id] = project_id[0]
        return res

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        result['value']['contact_id'] = partner_id
        return result

    _columns = {
        'contact_id': fields.many2one('res.partner', 'Contact'),
        'project_project_id': fields.function(_project_get, string="Project", type="many2one", relation="project.project", store=True),
        'comment': fields.text('Additional Information', translate=True),
        'description': fields.char('Description', size=128),
	'vat_note_id': fields.many2one('account.invoice.vat.note','BTW Nota'),
    }    

    def create(self, cr, uid, vals, context=None):
        """Set the contact from the partner"""
        vals['contact_id'] = vals['partner_id']
        res = super(account_invoice, self).create(cr, uid, vals, context=context)
        # Set the description per default
        project_id = self._project_get(cr, uid, [res], "", False)
        if project_id and project_id[res]:
            project = self.pool.get('project.project').browse(cr, uid, project_id[res])
            self.write(cr, uid, [res], {'description': project.name})
        return res

class account_tax(osv.osv):

    _inherit = 'account.tax'

    _columns = {
        'description': fields.char('Tax Code', size=64, translate=True),
    }    



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
