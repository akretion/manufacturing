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


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def _set_schedule_states(self, cr, uid, context=None):
        return [
            ('unable', 'Unable'),
            ('todo', 'Todo'),
            ('scheduled', 'Scheduled'),
        ]

    def __set_schedule_states(self, cr, uid, context=None):
        return self._set_schedule_states(cr, uid, context=context)

    _columns = {
        'schedule_state': fields.selection(
            __set_schedule_states,
            'Schedule State',
            readonly=True,
            oldname="planification",
            help="Planification State"),
    }

    _defaults = {
        'schedule_state': 'unable',
    }
