# -*- coding: utf-8 -*-
##############################################################################
#
#    Smart Solution bvba
#    Copyright (C) 2010-Today Smart Solution BVBA (<http://www.smartsolution.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################## 

{
	"name" : "Block External Followers",
	"version" : "1.0",
	"author" : "Smart Solution",
	"description" : """This module prevents that followers, external to the company (partners), are automaticaly added as follower to an OpenERP object""",
	"website" : "http://",
	"category" : "Generic Modules/Project",
	"depends" : ["base","mail"],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["block_external_followers_view.xml"],
	"installable": True
}
