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


class HierarchicalWorkcenterLoad(orm.TransientModel):
    _name = 'hierarchical.workcenter.load'

    def _add_sql_clauses(self, cr, uid, workcenter_ids, context=None):
        states = ['ready', 'confirmed', 'in_production']
        states_clause = "'%s'" % "', '".join(states)
        workcenters_clause = ", ".join([str(x) for x in workcenter_ids])
        return (states_clause, workcenters_clause)

    def _sql_query(self, cr, uid, context=None):
        query = """
            SELECT wl.workcenter_id AS id, sum(wl.hour) AS hour_load
            FROM mrp_production_workcenter_line wl
                LEFT JOIN mrp_production mp ON wl.production_id = mp.id
            WHERE mp.state IN (%s) and wl.workcenter_id IN (%s)
            GROUP BY wl.workcenter_id
        """ % (self._add_sql_clauses(cr, uid, self._workcter_ids,
                                     context=context))
        return query

    def compute_load(self, cr, uid, ids, context=None):
        self._workcter_ids = self.pool['mrp.workcenter'].search(
            cr, uid, [], context=context)
        # Erase cached data
        vals = {'load': 0, 'global_load': 0}
        self.pool['mrp.workcenter'].write(cr, uid, self._workcter_ids, vals,
                                          context=context)
        # Compute time for workcenters in mrp_production_workcenter_line
        cr.execute(self._sql_query(cr, uid, context=context))
        res = cr.dictfetchall()
        workcenter_hours = {}
        for elm in res:
            workcenter_hours[elm['id']] = elm['hour_load']
            vals = {'load': elm['hour_load'],
                    'global_load': elm['hour_load'],
                    'last_compute': time.strftime('%Y-%m-%d %H:%M:%S')}
            self.pool['mrp.workcenter'].write(
                cr, uid, [elm['id']], vals, context=context)
        # Compute upper level data
        self._aggregate_values(
            cr, uid, workcenter_hours, context=context)
        return True

    def _aggregate_values(self, cr, uid, work_hours, context=None):
        res = self._build_hierarchical_list(cr, uid, context=context)
        print res
        for elm in res:
            parent, children = elm.items()[0]
            children_time = sum([work_hours.get(child, 0)
                                 for child in children])
            work_hours[parent] = children_time + work_hours.get(parent, 0)
            vals = {'global_load': work_hours[parent],
                    'last_compute': time.strftime('%Y-%m-%d %H:%M:%S')}
            self.pool['mrp.workcenter'].write(
                cr, uid, parent, vals, context=context)

    def _build_hierarchical_list(self, cr, uid, context=None):
        """ return a workcenter relations list from LOW level to HIGH level
    [{parent_id1: [child_id1]}, {parent_id2: [child_id5, child_id7]}, ...]
        """
        hierarch, filtered_hierarchy = [], []
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
            hierarch.append({elm['id']: []})
            pos_in_list[elm['id']] = position
            position += 1
        for elm in res:
            # None values (without parent_id) are not used
            if elm['parent']:
                value = hierarch[pos_in_list[elm['parent']]][elm['parent']]
                value.append(elm['id'])
                hierarch[pos_in_list[elm['parent']]][elm['parent']] = value
        for elm in hierarch:
            parent, children = elm.items()[0]
            if children:
                # only nodes with children are useful
                filtered_hierarchy.append(elm)
        return filtered_hierarchy
