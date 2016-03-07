import time
from report import report_sxw

class production_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(production_order, self).__init__(cr, uid, name, context=context)
        self.pool.get('neopaul.production.order').write(cr, uid, context['active_ids'], {'printing_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.neopaul.production.order', 'neopaul.production.order', 'addons/neopaul_project/report/production_order.rml', parser=production_order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

