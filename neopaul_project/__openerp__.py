#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    "name" : "neopaul_project",
    "version" : "1.0",
    "author" : "SmartSolution",
    "category" : "Generic Modules/Base",
    "description": """
    Neopaul custom module for project management
""",
    "depends" : ["project","sale_tender","account", "purchase", "crm", "document", "project_sale_order","stock"],
    "init_xml" : [
        ],
    "update_xml" : [
        'neopaul_project_view.xml',
        'neopaul_project_data.xml',
        'neopaul_project_report.xml',
#        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
