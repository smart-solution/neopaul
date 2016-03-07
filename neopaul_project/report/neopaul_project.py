import time
from report import report_sxw

class neopaul_project(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(neopaul_project, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.neopaul.project.project', 'project.project', 'addons/neopaul_project/report/neopaul_project.rml', parser=neopaul_project)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

