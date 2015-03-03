# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2015 Akretion
#    @author David BEAL <david.beal@akretion.com>
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
###############################################################################


{
    'name': 'Mrp Workcenter Load',
    'version': '0.1',
    'author': 'Akretion',
    'maintener': 'Akretion',
    'category': 'Manufacturing',
    'summary': "Helper to compute workcenters load",
    'depends': [
        'mrp_operations',
        'stock_delivery_times_working_days',
    ],
    'description': """

Mrp Workcenter Load
=====================


* Define workcenter load in a hierarchical view, examples:
    - machine
    - machines group
    - workshop
    - plant
    - plants group

* Routing operations can be attributed to a machine or
  any upper level in the structure like workshop.

* Workcenters can be set offline:

    - no more used in capacity calculation
    - load of offline workcenters is switch to the workcenter
      with next upper level

* Allows massive replacement of Workcenter in Work Orders
  in selected operations (Work orders)

* Provides shortcuts to switch between Workcenters and Workorders views

* Limitation: the load is defined globally (not by period)
  => only useful for companies with short time frame


Quick start
=============

* install module
* click on Manufacturing > Load > Compute

Contributors
------------
* David BEAL <david.beal@akretion.com>
* Sébastien BEAL <sebastien.beau@akretion.com>

""",
    'website': 'http://www.akretion.com/',
    'data': [
        'workcenter_view.xml',
        'wizard/load_view.xml',
        'wizard/mrp_view.xml',
    ],
    'demo': [
        'demo/mrp.workcenter.csv',
        'demo/mrp_1.xml',
        'demo/mrp.routing.workcenter.csv',
        'demo/mrp_2.xml',
    ],
    'external_dependencies': {
        'python': [],
    },
    'license': 'AGPL-3',
    'tests': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
