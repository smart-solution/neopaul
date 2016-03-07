from openerp.osv import fields, osv

class project_task (osv.osv):
    _inherit = "project.task"
    
    def view_task(self,cr,uid,context=None):
        mod_obj= self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'action_view_task')[1]
        return mod_obj