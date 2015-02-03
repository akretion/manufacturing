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

WORKCENTER_ACTION = {
    'res_model': 'mrp.workcenter',
    'type': 'ir.actions.act_window',
    'target': 'current',
}

STATIC_STATES = ['cancel', 'done']


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'
    _parent_name = "parent_id"
    _parent_store = True
    _order = 'parent_left'

    def _compute_availability(self, cr, uid, ids, field_n, arg, context=None):
        res = {}
        for elm in self.browse(cr, uid, ids):
            res[elm.id] = elm.day_capacity - elm.global_load
        return res

    def _order_by_production_lines(self, cr, uid, context=None):
        return [('date_planned_ ASC', 'Planned Date ASC'), ]

    def __order_by_production_lines(self, cr, uid, context=None):
        return self._order_by_production_lines(cr, uid, context=context)

    def _get_hierarchical_name(self, cr, uid, ids, field_n, arg, context=None):
        res = {}
        for elm in self.browse(cr, uid, ids):
            distance = elm.level
            distance = ''.join(['--'] * distance)
            res[elm.id] = '%s%s' % (distance, elm.name)
        return res

    _columns = {
        'parent_id': fields.many2one(
            'mrp.workcenter',
            'Parent',
            ondelete='cascade',
            help="Parent Work Center: a workcenter can be any kind of "
                 "ressource: human, machine, workshop, plant\n"
                 "This field help to compute global load"),
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
            'Level'),
        'used': fields.boolean(
            'Used',
            help="Used workcenters are taken account "
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
        'day_capacity': fields.float(
            'Capacity',
            help="Number of hours a day available to produce"),
        'availability': fields.function(
            _compute_availability,
            string='Available',
            type='float'),
        'production_line_order_by': fields.selection(
            __order_by_production_lines, 'Proposed Order',
            help="Allow to define work orders ..."),
        'production_line_ids': fields.one2many(
            'mrp.production.workcenter.line',
            'workcenter_id',
            string='Production Lines',
            readonly=True,
            # this domain is displayed in the view as filter
            # think about it when update domain:
            # search <!-- schedule_state_filter --> in the view
            domain=[('state', 'not in', STATIC_STATES),
                    ('schedule_state', 'in', ['scheduled', 'pending'])],
            help=""),
    }

    def button_order_workorders_in_workcenter(
            self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            ProdLineM = self.pool['mrp.production.workcenter.line']
            order_by = elm.production_line_order_by
            prod_line_ids = ProdLineM.search(cr, uid, [
                ('state', 'not in', STATIC_STATES),
                ('workcenter_id.parent_id', 'child_of', elm.id), ],
                order=order_by, context=context)
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
                'name': "'%s' In Progress Operations" % elm.name,
                'res_model': 'mrp.production.workcenter.line',
                'type': 'ir.actions.act_window',
                'domain': [('workcenter_id', 'in', workcenter_child_ids),
                           ('state', 'not in', STATIC_STATES)],
                'target': 'current',
            }

    def toogle_used(self, cr, uid, ids, context=None):
        " Called by button in tree view "
        for elm in self.browse(cr, uid, ids, context=context):
            used = True
            used_ids = ids
            if elm.used:
                used_ids = self.search(
                    cr, uid, [
                        ('parent_id', 'child_of', [elm.id])],
                    context=context)
                used = False
            vals = {'used': used}
            self.write(cr, uid, used_ids, vals, context=context)
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
                # unused workcenters shouldn't taken account
                if child.used:
                    capacity += child.day_capacity
            vals = {'day_capacity': capacity}
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
