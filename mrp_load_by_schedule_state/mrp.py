# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
from openerp.addons.mrp_workcenter_load.workcenter import STATIC_STATES


PRODUCTION_PROPOSED_ORD_DEF = 'date_planned_ ASC'


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    def _order_by_production_line(self, cr, uid, context=None):
        return [(PRODUCTION_PROPOSED_ORD_DEF, 'Planned Date ASC')]

    def __order_by_production_line(self, cr, uid, context=None):
        return self._order_by_production_line(cr, uid, context=context)

    _columns = {
        'unable_load': fields.float('Unable'),
        'todo_load': fields.float('Todo'),
        'scheduled_load': fields.float('Scheduled'),
        'proposed_order': fields.selection(
            __order_by_production_line, 'Proposed Order',
            help="Define order of the work orders"),
        'production_line_ids': fields.one2many(
            'mrp.production.workcenter.line',
            'workcenter_id',
            string='Work Orders',
            readonly=True,
            # this domain is displayed in the view as filter
            # think about it when update domain:
            # search <!-- schedule_state_filter --> in the view
            domain=[('state', 'not in', STATIC_STATES),
                    ('schedule_state', 'in', ['scheduled', 'pending'])],
            help=""),
    }

    _defaults = {
        'proposed_order': PRODUCTION_PROPOSED_ORD_DEF,
    }


class HierarchicalWorkcenterLoad(orm.TransientModel):
    _inherit = 'hierarchical.workcenter.load'

    def _get_sql_query(self, cr, uid, context=None):
        query = super(HierarchicalWorkcenterLoad, self)._get_sql_query(
            cr, uid, context=context)
        query = query.replace("FROM", ", mp.schedule_state\nFROM")
        query = query.replace("BY wl.workcenter_id",
                              "BY wl.workcenter_id, mp.schedule_state")
        return query

    def _prepare_load_vals(self, cr, uid, result, context=None):
        super(HierarchicalWorkcenterLoad, self)._prepare_load_vals(
            cr, uid, result, context=context)
        vals = {}
        for elm in result:
            sched = elm['schedule_state']
            workcenter = elm['workcenter']
            if workcenter not in vals:
                vals[workcenter] = {
                    'load': elm['hour'],
                    '%s_load' % sched: elm['hour'],
                }
            else:
                vals[workcenter]['load'] += elm['hour']
                if '%s_load' % sched in vals[workcenter]:
                    vals[workcenter]['%s_load' % sched] += elm['hour']
                else:
                    vals[workcenter]['%s_load' % sched] = elm['hour']
        return vals
