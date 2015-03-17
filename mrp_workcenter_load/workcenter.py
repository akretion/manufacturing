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
from datetime import datetime


WORKCENTER_ACTION = {
    'res_model': 'mrp.workcenter',
    'type': 'ir.actions.act_window',
    'target': 'current',
}

WORKING_HOUR_DAY_DEFAULT = 8
STATIC_STATES = ['cancel', 'done']


class WorkcenterGroup(orm.Model):
    _name = 'workcenter.group'
    _description = 'Workcenter Group'

    _columns = {
        'name': fields.char('Name'),
    }

class MrpWorkcenter(orm.Model):
    """
Useful debug query
SELECT m.parent_id, m.id AS _id, r.name, m.parent_left, m.parent_right
FROM mrp_workcenter m
    LEFT JOIN resource_resource r ON r.id = m.resource_id
    """
    _inherit = 'mrp.workcenter'
    _parent_name = "parent_id"
    _parent_store = True
    _order = 'parent_left'

    def _compute_availability(self, cr, uid, ids, field_n, arg, context=None):
        res = {}
        for elm in self.browse(cr, uid, ids):
            res[elm.id] = elm.h24_capacity - elm.global_load
        return res

    def get_capacity_next24h(self, cr, uid, ids, field_n, arg, context=None):
        """ Compute the hours number to use the workcenter in next 24h
            excluding unworking days
            @return float: hour
            example:
                 We are Friday 15h, the next working 24h ends Monday at 14h59
            """
        now = datetime.today()
        mResCal = self.pool['resource.calendar']
        horizon = 1  # day
        res = {}
        for workc in self.browse(cr, uid, ids, context=context):
            working_hours_in_next24 = WORKING_HOUR_DAY_DEFAULT
            if workc.calendar_id:
                # _get_date exclude not working days
                working_date_in_next24 = mResCal._get_date(
                    cr, uid, workc.calendar_id.id, now,
                    horizon, resource=workc.id, context=context)
                # interval_hours_get 18.0    intervalle entre 2 dates
                working_hours_in_next24 = mResCal.interval_hours_get(
                    cr, uid, workc.calendar_id.id, now,
                    working_date_in_next24, resource=workc.id)
            res[workc.id] = working_hours_in_next24
        return res

    def _get_hierarchical_name(self, cr, uid, ids, field_n, arg, context=None):
        res = {}
        for elm in self.browse(cr, uid, ids):
            distance = elm.level
            distance = '-' * distance
            res[elm.id] = '%s %s' % (distance, elm.name)
        return res

    _columns = {
        'parent_id': fields.many2one(
            'mrp.workcenter',
            'Parent',
            ondelete='cascade',
            help="Parent Work Center: a workcenter can be any kind of "
                 "ressource: human, machine, workshop, plant\n"
                 "This field help to compute global load"),
        'workcenter_group_id': fields.many2one(
            'workcenter.group',
            string='Workcenter Group'),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'child_id': fields.one2many(
            'mrp.workcenter',
            'parent_id',
            string='Child Workcenter'),
        'hierachical_name': fields.function(
            _get_hierarchical_name,
            store=False,
            string='Name',
            type='char'),
        'level': fields.integer(
            'Level',
            help="Level computed according to workcenter hierarchy position"),
        'online': fields.boolean(
            'Online',
            help="Online workcenters are taken account "
                 "in capacity computing"),
        'global_load': fields.float(
            'Global Load (h)',
            help="Load for all the Manufacturing Orders in these states:\n"
                 "'ready' / 'confirmed' / 'in_production'"),
        'load': fields.float(
            'Load (h)',
            help="Load for this particular workcenter"),
        'last_compute': fields.datetime(
            'Calculation',
            oldname="last_compute",
            help="Last calculation"),
        'h24_capacity': fields.function(
            get_capacity_next24h,
            string='Capacity',
            type='float',
            help="Number of hours a day available to produce"),
        'availability': fields.function(
            _compute_availability,
            string='Available',
            type='float'),
    }

    _defaults = {
        'online': True,
    }

    def button_order_workorders_in_workcenter(
            self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            ProdLineM = self.pool['mrp.production.workcenter.line']
            order_by = elm.proposed_order
            order_by = ['%s %s' % (row.field_id.name, row.order)
                        for row in elm.ordering_field_ids]
            prod_line_ids = ProdLineM.search(cr, uid, [
                ('state', 'not in', STATIC_STATES),
                ('workcenter_id.parent_id', 'child_of', elm.id), ],
                order=', '.join(order_by), context=context)
            count = 1
            for prod_line_id in prod_line_ids:
                vals = {'sequence': count}
                count += 1
                ProdLineM.write(cr, uid, prod_line_id, vals, context=context)
        return True

    def button_workcenter_line(self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            workcenter_child_ids = self.search(
                cr, uid, [('parent_id', 'child_of', elm.id)], context=context)
            return {
                'view_mode': 'tree,form',
                'name': "'%s' or children in Progress Operations" % elm.name,
                'res_model': 'mrp.production.workcenter.line',
                'type': 'ir.actions.act_window',
                'domain': [('workcenter_id', 'in', workcenter_child_ids),
                           ('state', 'not in', STATIC_STATES)],
                'target': 'current',
            }

    def toogle_online(self, cr, uid, ids, context=None):
        " Called by button in tree view "
        for elm in self.browse(cr, uid, ids, context=context):
            online = True
            online_ids = ids
            if elm.online:
                online_ids = self.search(
                    cr, uid, [
                        ('parent_id', 'child_of', [elm.id])],
                    context=context)
                online = False
            vals = {'online': online}
            self.write(cr, uid, online_ids, vals, context=context)
        self._compute_capacity(cr, uid, context=context)
        action = {
            'view_mode': 'tree,form',
        }
        action.update(WORKCENTER_ACTION)
        return action

    def _compute_capacity(self, cr, uid, context=None):
        """ Compute capacity of the workcenters which have children """
        res = self._build_hierarchical_list(cr, uid, context=context)
        for elm in res:
            parent, children_ids = elm.items()[0]
            capacity = 0
            for child in self.browse(cr, uid, children_ids, context=context):
                # offline workcenters shouldn't taken account
                if child.online:
                    capacity += child.h24_capacity
            vals = {'h24_capacity': capacity}
            self.write(cr, uid, parent, vals, context=context)
        return True

    def _build_hierarchical_list(self, cr, uid, context=None):
        """ return a workcenter relations list from LOW level to HIGH level
        [{parent_id1: [child_id1]}, {parent_id2: [child_id5, child_id7]}, ...]
        """
        hierarchy, filtered_hierarchy = [], []
        pos_in_list = {}
        parents = {}
        position = 0
        query = """
            SELECT id, parent_id AS parent
            FROM mrp_workcenter
            ORDER BY (parent_right - parent_left) ASC, parent_id DESC
        """
        cr.execute(query)
        res = cr.dictfetchall()
        # we assign nodes in the right order to make aggregation reliable
        for elm in res:
            hierarchy.append({elm['id']: []})
            pos_in_list[elm['id']] = position
            position += 1
            parents[elm['id']] = elm['parent']
        for elm in res:
            parent = elm['parent']
            if parent:
                value = hierarchy[pos_in_list[parent]][parent]
                value.append(elm['id'])
                hierarchy[pos_in_list[parent]][parent] = value
        for elm in hierarchy:
            parent, children = elm.items()[0]
            if children:
                # only nodes with children are useful
                filtered_hierarchy.append(elm)
        self._set_workc_level(cr, uid, hierarchy, parents, context=context)
        return filtered_hierarchy

    def _set_workc_level(self, cr, uid, hierarchy, parents, context=None):
        """ Write level field for each workcenter according to hierarchy
            Example with this hierarchy
            [{5: []}, {8: []}, {2: []}, {3: []}, {7: [8]},
             {1: [2, 3]}, {4: [7, 1]}]
            will result:
            level 0: [4, 5]    # here 5 has no parent neither child
            level 1: [7, 1]
            level 2: [2, 3, 8]
        """
        children_level = {}
        already_fallen_in_lower_level = {}
        level = 0
        for elm in reversed(hierarchy):
            parent, children = elm.items()[0]
            already_fallen_in_lower_level[level] = False
            if level in children_level and parent in children_level[level]:
                if already_fallen_in_lower_level[level] is False:
                    already_fallen_in_lower_level[level] = True
                    level += 1
            if level in children_level:
                children_level[level].extend(children)
            else:
                children_level[level] = children
            if parents[parent] is None:
                level = 0
            self.write(cr, uid, parent, {'level': level}, context=context)
        return True
