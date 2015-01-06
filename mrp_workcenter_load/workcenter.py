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


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

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
            help="(h/day)")
    }

    _parent_name = "parent_id"
    _parent_store = True
    _order = 'parent_left'

    def toogle_active(self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            active = True
            active_ids = ids
            if elm.active:
                active_ids = self.search(
                    cr, uid, [
                        ('parent_id', 'child_of', [elm.id])],
                    context=context)
                active = False
            self.write(cr, uid, active_ids, {'active': active}, context=context)
        self._compute_capacity(cr, uid, context=context)
        return True

    def _compute_capacity(self, cr, uid, context=None):
        res = self._build_hierarchical_list(cr, uid, context=context)
        for elm in res:
            parent, children_ids = elm.items()[0]
            capacity = 0
            for child in self.browse(cr, uid, children_ids, context=context):
                # unactive workcenters should not taken account
                if child.active:
                    capacity += child.day_capacity
            vals = {'day_capacity': capacity}
            self.write(cr, uid, parent, vals, context=context)

    def _build_hierarchical_list(self, cr, uid, context=None):
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
            parent = elm['parent']
            if parent:
                value = hierarchy[pos_in_list[parent]][parent]
                value.append(elm['id'])
                hierarchy[pos_in_list[parent]][parent] = value
        for elm in hierarchy:
            _, children = elm.items()[0]
            if children:
                # only nodes with children are useful
                filtered_hierarchy.append(elm)
        return filtered_hierarchy
