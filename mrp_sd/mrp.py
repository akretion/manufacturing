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


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def _set_schedule_states(self, cr, uid, context=None):
        states = super(MrpProduction, self)._set_schedule_states(
            cr, uid, context=context)
        position = states.index(('scheduled', 'Scheduled'))
        states.insert(position, ('pending', 'Pending'))
        return states
