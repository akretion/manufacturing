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
    }

    _parent_name = "parent_id"
    _parent_store = True
    _order = 'parent_left'

