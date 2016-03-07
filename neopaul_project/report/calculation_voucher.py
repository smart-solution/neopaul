import time
from report import report_sxw

class calculation_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(calculation_voucher, self).__init__(cr, uid, name, context=context)
        print "init parser"
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.neopaul.project.calculation.voucher', 'neopaul.project.calculation.voucher', 'addons/neopaul_project/report/calculation_voucher.rml', parser=calculation_voucher)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

