import time
from report import report_sxw

class neopaul_repair(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(neopaul_repair, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.neopaul.repair.order', 'project.issue', 'addons/neopaul_repair/report/repair.rml', parser=neopaul_repair)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

