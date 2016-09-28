#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    "name" : "sale_tender",
    "version" : "1.0",
    "author" : "SmartSolution",
    "category" : "Generic Modules/Base",
    "description": """
    Manage tenders for sale orders. When one of the sale order of a tender is validated the other ones are cancelled.
""",
    "depends" : ["sale",],
    "init_xml" : [
        ],
    "update_xml" : [
        'sale_tender_view.xml',
        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
