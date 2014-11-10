# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def default_get(self, cr, uid, fields, context=None):
        res = super(MrpProduction, self).default_get(
            cr, uid, fields, context=context)
        # We only needs to change location field values which are in res keys
        location_fields = set(res.keys()).intersection(
            ['location_src_id', 'location_dest_id'])
        for field in location_fields:
            res[field] = self._change_location(
                cr, uid, field, res[field], context=None)
        return res

    def create(self, cr, uid, vals, context=None):
        location_fields = set(vals.keys()).intersection(
            ['location_src_id', 'location_dest_id'])
        for field in location_fields:
            vals[field] = self._change_location(
                cr, uid, field, vals[field], context=None)
        return super(MrpProduction, self).create(cr, uid, vals, context=context)

    def _change_location(self, cr, uid, loc_field, location, context=None):
        """ You may inherit this method to change
            from/to location according to loc_field
            super(...)
            if loc_field == 'location_src_id':
                return X
            else:
                return Y
        """
        return location
