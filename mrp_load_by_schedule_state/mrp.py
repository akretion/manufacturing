# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
import time
from openerp.tools.misc import (DEFAULT_SERVER_DATETIME_FORMAT as ERP_DATETIME)


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _columns = {
        'unable_load': fields.float('Todo'),
        'todo_load': fields.float('Todo'),
        'scheduled_load': fields.float('Scheduled'),
    }


class HierarchicalWorkcenterLoad(orm.TransientModel):
    _inherit = 'hierarchical.workcenter.load'

    def _get_sql_query(self, cr, uid, context=None):
        query = super(HierarchicalWorkcenterLoad, self)._get_sql_query(
            cr, uid, context=context)
        query = query.replace("FROM", ", mp.schedule_state\nFROM")
        query = query.replace("GROUP BY", "GROUP BY mp.schedule_state,")
        return query

    def _write_load(self, cr, uid, result, context=None):
        print result
        # {'hour': 0.8, 'workcenter': 14, 'schedule_state': u'pending'}
        #import pdb;pdb.set_trace()
        workcenter_hours = {}
        values = {}
        for elm in result:
            # TODO compute with new field
            if elm['workcenter'] not in workcenter_hours:
                workcenter_hours[elm['workcenter']] = elm['hour']
            else:
                workcenter_hours[elm['workcenter']] += elm['hour']
            if elm['schedule_state'] not in values:
                values[elm['schedule_state']] = {elm['workcenter']: elm['hour']}
            else:
                if elm['workcenter'] not in values[elm['schedule_state']]:
                    values[elm['schedule_state']][elm['workcenter']] = elm['hour']
                else:
                    values[elm['schedule_state']][elm['workcenter']] += elm['hour']
            #vals = {'load': elm['hour'],
            #        'global_load': elm['hour'],
            #        'last_compute': time.strftime(ERP_DATETIME)}
        for state, workc_val in values.items():
            for workc, value in workc_val.items():
                vals = {
                    '%s_load' % state: value
                }
                self.pool['mrp.workcenter'].write(
                    cr, uid, workc, vals, context=context)

        return workcenter_hours
