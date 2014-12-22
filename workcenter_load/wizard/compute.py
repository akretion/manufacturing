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


class HierarchicalWorkcenterLoad(orm.TransientModel):
    _name = 'hierarchical.workcenter.load'

    def _get_default_workcenter(self, cr, uid, context=None):
        ids = self.pool['mrp.workcenter'].search(
            cr, uid, [('parent_id', '=', False)], context=context)
        if ids:
            return ids[0]
        return False

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            'Parent Workcenter',
            required=True),

    }

    _defaults = {
        'workcenter_id': _get_default_workcenter,
    }

    def _add_sql_clauses(self, cr, uid, workcenter_ids, context=None):
        states = ['ready', 'confirmed', 'in_production']
        specific_clauses = ''
        clauses = self._add_custom_sql_clause(cr, uid, context=context)
        if clauses:
            specific_clauses = 'AND ' + '\n\t AND '.join(clauses)
        states_clause = "'%s'" % "', '".join(states)
        workcenters_clause = ", ".join([str(x) for x in workcenter_ids])
        return (states_clause, workcenters_clause, specific_clauses)

    def _add_custom_sql_clause(self, cr, uid, context=None):
        " inherit to complete with your own clause "
        return []

    def compute_load(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        workcter_ids = self.pool['mrp.workcenter'].search(cr, uid, [
            ('id', 'child_of', wizard.workcenter_id.id),
        ], context=context)
        # Erase cached data
        vals = {'load': 0, 'global_load': 0}
        self.pool['mrp.workcenter'].write(cr, uid, workcter_ids, vals,
                                          context=context)
        # Compute time for workcenters in mrp_production_workcenter_line
        query = """
SELECT wl.workcenter_id AS id, sum(wl.hour) AS hour_load
FROM mrp_production_workcenter_line wl
    LEFT JOIN mrp_production mp ON wl.production_id = mp.id
WHERE mp.state IN (%s) and wl.workcenter_id IN (%s) %s
GROUP BY wl.workcenter_id
        """ % (self._add_sql_clauses(cr, uid, workcter_ids, context=context))
        cr.execute(query)
        res = cr.dictfetchall()
        workcenter_hours = {}
        for elm in res:
            workcenter_hours[elm['id']] = elm['hour_load']
            vals = {'load': elm['hour_load'],
                    'global_load': elm['hour_load'],
                    'last_compute': time.strftime('%Y-%m-%d %H:%M:%S')}
            self.pool['mrp.workcenter'].write(
                cr, uid, [elm['id']], vals, context=context)
        # Compute the aggregate data
        self._compute_summarize_values(
            cr, uid, workcenter_hours, context=context)
        return True

    def _compute_summarize_values(self, cr, uid, wk_hours, context=None):
        res = self._build_hierarchical_list(cr, uid, context=context)
        for item in res:
            parent, children = item.items()[0]
            working_time = sum([wk_hours[child]
                                for child in children
                                if child in wk_hours])
            parent_wh = 0
            if parent in wk_hours:
                parent_wh = wk_hours[parent]
            wk_hours[parent] = working_time + parent_wh
            vals = {'global_load': working_time + parent_wh,
                    'last_compute': time.strftime('%Y-%m-%d %H:%M:%S')}
            self.pool['mrp.workcenter'].write(
                cr, uid, parent, vals, context=context)

    def _build_hierarchical_list(self, cr, uid, context=None):
        """ return a workcenter relations list from LOW level to HIGH level
    [{parent_id1: [child_id1]}, {parent_id2: [child_id5, child_id7]}, ...]
        """
        query = """
SELECT id, parent_id AS parent
FROM mrp_workcenter
ORDER BY (parent_right - parent_left) ASC, parent_id
        """
        cr.execute(query)
        res = cr.dictfetchall()
        hierarch, seen_keys = [], []
        position = 0
        pos_in_list = {}
        for elm in res:
            # None values (without parent_id) are not used
            if elm['parent']:
                if elm['parent'] in seen_keys:
                    value = hierarch[pos_in_list[elm['parent']]][elm['parent']]
                    value.append(elm['id'])
                    hierarch[pos_in_list[elm['parent']]][elm['parent']] = value
                else:
                    seen_keys.append(elm['parent'])
                    hierarch.append({elm['parent']: [elm['id']]})
                    pos_in_list[elm['parent']] = position
                    position += 1
        return hierarch
