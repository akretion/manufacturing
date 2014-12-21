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

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            'Parent Workcenter',
            required=True)
    }

    def _add_sql_clause(self, cr, uid, context=None):
        " inherit to complete with your own clause "
        return []

    def compute_load(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        workcenter_ids = self.pool['mrp.workcenter'].search(cr, uid, [
            ('id', 'child_of', wizard.workcenter_id.id),
        ], context=context)
        states = ['ready', 'confirmed', 'in_production']
        specific_clauses = ''
        clauses = self._add_sql_clause(cr, uid, context=context)
        if clauses:
            specific_clauses = 'AND ' + '\n\t AND '.join(clauses)
        states_clause = "'%s'" % "', '".join(states)
        workcenters_clause = ", ".join([str(x) for x in workcenter_ids])
        print workcenters_clause, states_clause, workcenter_ids
        query = """
SELECT wl.workcenter_id AS id, sum(wl.hour) AS hour_load
FROM mrp_production_workcenter_line wl
    LEFT JOIN mrp_production mp ON wl.production_id = mp.id
WHERE mp.state IN (%s) and wl.workcenter_id IN (%s) %s
GROUP BY wl.workcenter_id
        """ % (states_clause, workcenters_clause, specific_clauses)
        cr.execute(query)
        res = cr.dictfetchall()
        for elm in res:
            vals = {'load': elm['hour_load'],
                    'last_compute': time.strftime('%Y-%m-%d %H:%M:%S')}
            self.pool['mrp.workcenter'].write(
                cr, uid, [elm['id']], vals, context=context)
        return True
