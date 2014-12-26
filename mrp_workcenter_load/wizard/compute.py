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
    _name = 'hierarchical.workcenter.load'

    def _add_sql_clauses(self, cr, uid, workcenter_ids, context=None):
        states = ['ready', 'confirmed', 'in_production']
        states_clause = "'%s'" % "', '".join(states)
        workcenters_clause = ", ".join([str(x) for x in workcenter_ids])
        return (states_clause, workcenters_clause)

    def _get_sql_query(self, cr, uid, context=None):
        query = """
            SELECT wl.workcenter_id AS workcenter, sum(wl.hour) AS hour
            FROM mrp_production_workcenter_line wl
                LEFT JOIN mrp_production mp ON wl.production_id = mp.id
            WHERE mp.state IN (%s) and wl.workcenter_id IN (%s)
            GROUP BY wl.workcenter_id
        """ % (self._add_sql_clauses(cr, uid, self._workcter_ids,
                                     context=context))
        return query

    def _prepare_load_vals(self, cr, uid, result, context=None):
        vals = {}
        for elm in result:
            vals[elm['workcenter']] = {'load': elm['hour']}
        return vals

    def compute_load(self, cr, uid, ids, context=None):
        workcenter_hours = {}
        self._workcter_ids = self.pool['mrp.workcenter'].search(
            cr, uid, [], context=context)
        # Erase cached data
        vals = {'load': 0, 'global_load': 0}
        self.pool['mrp.workcenter'].write(cr, uid, self._workcter_ids, vals,
                                          context=context)
        # Compute time for workcenters in mrp_production_workcenter_line
        cr.execute(self._get_sql_query(cr, uid, context=context))
        result = cr.dictfetchall()
        vals = self._prepare_load_vals(cr, uid, result, context=context)
        for workcenter, values in vals.items():
            workcenter_hours[workcenter] = values['load']
            values['global_load'] = values['load']
            values['last_compute'] = time.strftime(ERP_DATETIME)
            self.pool['mrp.workcenter'].write(
                cr, uid, workcenter, values, context=context)
        # Compute upper level data
        self._aggregate_values(
            cr, uid, workcenter_hours, context=context)
        return {
            'name': 'Workcenters Load',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'mrp.workcenter',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def _aggregate_values(self, cr, uid, work_hours, context=None):
        res = self._build_hierarchyical_list(cr, uid, context=context)
        for elm in res:
            parent, children = elm.items()[0]
            children_time = sum([work_hours.get(child, 0)
                                 for child in children])
            work_hours[parent] = children_time + work_hours.get(parent, 0)
            vals = {'global_load': work_hours[parent],
                    'last_compute': time.strftime(ERP_DATETIME)}
            self.pool['mrp.workcenter'].write(
                cr, uid, parent, vals, context=context)

    def _build_hierarchyical_list(self, cr, uid, context=None):
        """ return a workcenter relations list from LOW level to HIGH level
        [{parent_id1: [child_id1]}, {parent_id2: [child_id5, child_id7]}, ...]
        """
        hierarchy, filtered_hierarchy = [], []
        pos_in_list = {}
        position = 0
        query = """
            SELECT id, parent_id AS parent
            FROM mrp_workcenter
            ORDER BY (parent_right - parent_left) ASC, parent_id
        """
        cr.execute(query)
        res = cr.dictfetchall()
        # we assign nodes in the right order to make aggregation reliable
        for elm in res:
            hierarchy.append({elm['id']: []})
            pos_in_list[elm['id']] = position
            position += 1
        for elm in res:
            if elm['parent']:
                value = hierarchy[pos_in_list[elm['parent']]][elm['parent']]
                value.append(elm['id'])
                hierarchy[pos_in_list[elm['parent']]][elm['parent']] = value
        for elm in hierarchy:
            parent, children = elm.items()[0]
            if children:
                # only nodes with children are useful
                filtered_hierarchy.append(elm)
        return filtered_hierarchy
