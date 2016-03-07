import time
from report import report_sxw

class design_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(design_voucher, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.neopaul.project.design.voucher', 'neopaul.project.design.voucher', 'addons/neopaul_project/report/design_voucher.rml', parser=design_voucher)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

