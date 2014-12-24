# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm
import time
from openerp.tools.misc import (DEFAULT_SERVER_DATETIME_FORMAT as ERP_DATETIME)


class HierarchicalWorkcenterLoad(orm.TransientModel):
    _inherit = 'hierarchical.workcenter.load'

    def _get_sql_query(self, cr, uid, context=None):
        query = super(HierarchicalWorkcenterLoad, self)._get_sql_query(
            cr, uid, context=context)
        query = query.replace("FROM", ", mp.schedule_state\nFROM")
        query = query.replace("GROUP BY", "GROUP BY mp.schedule_state,")
        return query

    def _write_load(self, cr, uid, result, context=None):
        workcenter_hours = {}
        for elm in result:
            # TODO compute with new field
            workcenter_hours[elm['id']] = elm['hour']
            vals = {'load': elm['hour'],
                    'global_load': elm['hour'],
                    'last_compute': time.strftime(ERP_DATETIME)}
            self.pool['mrp.workcenter'].write(
                cr, uid, [elm['id']], vals, context=context)
        return workcenter_hours
