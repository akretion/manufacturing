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

    def _pending_scheduled_state(self, cr, uid, ids, field_n, arg, context=None):
        res = {}
        for elm in self.browse(cr, uid, ids):
            res[elm.id] = elm.pending_load + elm.scheduled_load
        return res

    _columns = {
        'pending_load': fields.float(
            'Pending',
            help="Pending Load (hour)"),
        'pending_scheduled_load': fields.function(
            _pending_scheduled_state,
            string='Pend./Sched.',
            type='float')
    }


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def _set_schedule_states(self, cr, uid, context=None):
        states = super(MrpProduction, self)._set_schedule_states(
            cr, uid, context=context)
        position = states.index(('scheduled', 'Scheduled'))
        states.insert(position, ('pending', 'Pending'))
        return states
