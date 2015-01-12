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
    _workcter_ids = None

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

    def _erase_cached_data(self, cr, uid, context=None):
        " Update to 0 '*load' columns "
        MrpWorkC = self.pool['mrp.workcenter']
        vals = {}
        for col in MrpWorkC._columns:
            if len(col) > 3 and col[-4:] == 'load':
                vals.update({col: 0})
        MrpWorkC.write(cr, uid, self._workcter_ids, vals, context=context)
        return True

    def compute_load(self, cr, uid, ids, context=None):
        workcenter_hours = {}
        self._workcter_ids = self.pool['mrp.workcenter'].search(
            cr, uid, [], context=context)
        self._erase_cached_data(cr, uid, context=context)
        # Compute time for workcenters in mrp_production_workcenter_line
        cr.execute(self._get_sql_query(cr, uid, context=context))
        result = cr.dictfetchall()
        vals = self._prepare_load_vals(cr, uid, result, context=context)
        for workcenter, values in vals.items():
            workcenter_hours[workcenter] = values
            workcenter_hours[workcenter]['global_load'] = values['load']
            to_update = dict(values)
            #to_update['global_load'] = values['load']
            to_update['last_compute'] = time.strftime(ERP_DATETIME)
            self.pool['mrp.workcenter'].write(
                cr, uid, workcenter, to_update, context=context)
        # Compute upper level data
        self._aggregate_values(
            cr, uid, workcenter_hours, context=context)
        return {
            'name': 'Workcenters Load',
            'view_type': 'tree',
            'view_mode': 'tree',
            'view_id': self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'mrp', 'mrp_workcenter_tree_view')[1],
            'res_model': 'mrp.workcenter',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def _aggregate_child_value(self, cr, uid, child, key, val, parent_hr,
                               work_hours, context=None):
        #print '    ', child, self.pool['mrp.workcenter'].browse(cr, uid, child).name, ' child', key, val
        if key not in ('load', 'global_load'):
            if key in parent_hr:
                parent_hr[key] += val
            else:
                parent_hr[key] = val

    def _aggregate_values(self, cr, uid, work_hours, context=None):
        MrpWorkC = self.pool['mrp.workcenter']
        res = MrpWorkC._build_hierarchical_list(cr, uid, context=context)
        for elm in res:
            parent_hr = {}
            parent, children = elm.items()[0]
            #print work_hours
            #print 'PARENT', parent
            #print elm, MrpWorkC.browse(cr, uid, parent).name, [x.name for x in MrpWorkC.browse(cr, uid, children)]
            if parent in work_hours:
                parent_hr = work_hours[parent]
                #print parent, self.pool['mrp.workcenter'].browse(cr, uid, parent).name, 'parent    work_hours', work_hours[parent]
            for child in children:
                if child in work_hours:
                    for key, val in work_hours[child].items():
                        self._aggregate_child_value(
                            cr, uid, child, key, val, parent_hr, work_hours,
                            context=context)
                        #print key, 'parent_hr', parent_hr
                    if 'global_load' not in parent_hr:
                        parent_hr['global_load'] = 0
                    if 'global_load' in work_hours[child]:
                        parent_hr['global_load'] += work_hours[child]['global_load']
            if parent_hr and parent in work_hours:
                if 'load' in parent_hr and 'load' in work_hours[parent]:
                    parent_hr['global_load'] += parent_hr['load']
                    #print 'parent_hr', parent_hr
                #print 'NORMALLY NOT', parent_hr
                work_hours[parent] = parent_hr
                MrpWorkC.write(cr, uid, parent, parent_hr, context=context)
        #print '\n', work_hours
