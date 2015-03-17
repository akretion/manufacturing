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
COMPLEX_WORK_ORDER_FIELDS = ['message_follower_ids',
                             'message_is_follower',
                             'message_unread',
                             'criterious_output',
                             ]


class MrpWorkcenterOrdering(orm.Model):
    _name = 'mrp.workcenter.ordering'
    _description = "Workcenter Ordering"
    _order = 'sequence'

    _columns = {
        'sequence': fields.integer(
            'Sequence'),
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            'Workcenter'),
        'field_id': fields.many2one(
            'ir.model.fields',
            string='Work Order Field',
            domain=[('model', '=', 'mrp.production.workcenter.line'),
                    ('name', 'not in', COMPLEX_WORK_ORDER_FIELDS)],
            help="",),
        'ttype': fields.related(
            'field_id', 'ttype',
            type='char',
            string='Type'),
        'order': fields.selection(
            [('asc', 'Asc'), ('desc', 'Desc')],
            string='Order'),
    }

    _defaults = {
        'order': 'asc',
    }


class MrpProdLine(orm.Model):
    _inherit = 'mrp.production.workcenter.line'

    def _get_criterious_html(self, cr, uid, ids, field_n, arg, context=None):
        """ Convert String criterious values to table format """
        table_format = """
        <table cellspacing="0" cellpadding="5" border="1"
               width="70%%" style="border-color:#cacaca;border-style:solid;"
               class="oe_list_content">
            <thead>
                <tr align='center'>
                    <th>Field</td>
                    <th>Value</td>
                </tr>
            </thead>
            <tbody style="cursor:default">"""
        res = {}
        for elm in self.browse(cr, uid, ids):
            for field in elm.workcenter_id.accessible_field_ids:
                value = elm[field.name]
                if field.ttype not in ('one2many', 'many2many'):
                    if field.ttype == 'many2one':
                        value = value.name or ''
                    table_format += """<tr align='center'>
                                        <td>%s</td>
                                        <td>%s</td>
                                    </tr>""" % (
                        field.field_description, value)
            table_format += """</tbody></table> """
            res[elm.id] = table_format
        return res

    _columns = {
        'criterious_output': fields.function(
            _get_criterious_html,
            string='Criterious',
            type='html',
            store=False,
            help="Display criterious tab"),
    }


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        workcenter_ids = self.search(cr, uid, [], context=context)
        self.pool['hierarchical.workcenter.load'].compute_load(
            cr, uid, workcenter_ids, context=context)
        return super(MrpWorkcenter, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

    def _add_sql_clauses(self, cr, uid, workcenter_ids, context=None):
        states = ['ready', 'confirmed', 'in_production']
        states_clause = "'%s'" % "', '".join(states)
        workcenters_clause = ", ".join([str(x) for x in workcenter_ids])
        return (states_clause, workcenters_clause)

    def compute_load(self, cr, uid, ids, field_n, arg, context=None):
        FIELDS_TO_COMPUTE = ('unable_load', 'todo_load', 'scheduled_load')
        res = {}
        result = {}
        workcenter_ids = self.search(cr, uid, [], context=context)
        query = """
            SELECT wl.workcenter_id AS workcenter, sum(wl.hour) AS hour,
                mp.schedule_state
            FROM mrp_production_workcenter_line wl
                LEFT JOIN mrp_production mp ON wl.production_id = mp.id
            WHERE mp.state IN (%s) and wl.workcenter_id IN (%s)
            GROUP BY wl.workcenter_id, mp.schedule_state
        """ % (self._add_sql_clauses(cr, uid, workcenter_ids, context=context))
        cr.execute(query)
        # [{'hour': 0.25, 'workcenter': 30, 'schedule_state': u'unable'}, ...]
        result = cr.dictfetchall()
        print '\nresult', result
        aaa = {}
        for elm in result:
            aaa[elm['workcenter']] = {elm['schedule_state']: elm['hour']}
        # print '\naaa', aaa
        for elm in self.browse(cr, uid, workcenter_ids, context=context):
            if elm.id not in res:
                res[elm.id] = {x: 0 for x in FIELDS_TO_COMPUTE}
            else:
                res[elm.id] = {aaa[elm.id]['schedule_state']: elm['hour']}
        print 'res', res
        return res

    def _compute_load(self, cr, uid, ids, field_n, arg, context=None):
        return self.compute_load(
            cr, uid, ids, field_n, arg, context=context)

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
        'ordering_field_ids': fields.one2many(
            'mrp.workcenter.ordering',
            'workcenter_id',
            string='Ordering fields',
            help=" "),
        'accessible_field_ids': fields.many2many(
            'ir.model.fields',
            string='Accessible fields',
            domain=[('model', '=', 'mrp.production.workcenter.line'),
                    ('name', 'not in', COMPLEX_WORK_ORDER_FIELDS)],
            help="These fields will be accessible by production"),
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
