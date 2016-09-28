#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    "name" : "caldav_client",
    "version" : "1.0",
    "author" : "SmartSolution",
    "category" : "Generic Modules/Base",
    "description": """
    CalDav Client for meetings synchronisation

    Require : sudo easy_install caldav
""",
    "depends" : ["base","crm"],
    "init_xml" : [
        'caldav_client_data.xml',
        ],
    "update_xml" : [
        'caldav_client_view.xml',
#        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
