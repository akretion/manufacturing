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
    'name': 'Mrp Schedule',
    'version': '0.1',
    'author': 'Akretion',
    'maintener': 'Akretion',
    'category': 'Manufacturing',
    'depends': [
        'mrp_operations',
    ],
    'description': """

* Add a schedule state field in Manufacturing Order
* Allow to change this field in tree view

This module offers services to these modules:

- mrp_whole_procurable_sale
- mrp_workcenter_load
- mrp_load_by_schedule_state


Contributors
------------
* David BEAL <david.beal@akretion.com>
* Sébastien BEAL <sebastien.beau@akretion.com>

""",
    'website': 'http://www.akretion.com/',
    'data': [
        'mrp_view.xml',
    ],
    'demo': [
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
