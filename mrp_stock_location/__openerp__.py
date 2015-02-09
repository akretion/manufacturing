# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2014 Akretion
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
    'name': 'MRP Stock Location',
    'version': '0.1',
    'author': 'Akretion',
    'maintener': 'Akretion',
    'category': 'Manufaturing',
    'summary': "Allow to use alternative locations",
    'depends': [
        'mrp',
    ],
    'description': """
MRP Stock Location
======================

This module does nothing used alone.

It provides method to change the default manufacturing location:
source and destination

Example: Here is how to do


```python

    # You may inherit this method to change
    # from/to location according to loc_field
    def _change_location(self, cr, uid, loc_field, location, context=None):
        super(my_class, self)._change_location(...)
        _, location_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'my_module', 'my_specific_loaction')
        _, alt_loc_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'my_module', 'my_specific_loaction')
        if loc_field == 'location_src_id':
            return location_id
        else:
            return alt_loc_id

```

Contributors
------------
* David BEAL <david.beal@akretion.com>

""",
    'website': 'http://www.akretion.com/',
    'data': [
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
