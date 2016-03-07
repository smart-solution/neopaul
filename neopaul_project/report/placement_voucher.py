import time
from report import report_sxw

class placement_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(placement_voucher, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.neopaul.placement.voucher', 'neopaul.placement.voucher', 'addons/neopaul_project/report/placement_voucher.rml', parser=placement_voucher)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

