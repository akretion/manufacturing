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
        states.append(('25', 'Pending'))
        states = list(set(states))
        states.sort(key=lambda t: t[0])
        return states


class HierarchicalWorkcenterLoad(orm.TransientModel):
    _inherit = 'hierarchical.workcenter.load'

    #def _add_custom_sql_clause(self, cr, uid, context=None):
    #    res = super(HierarchicalWorkcenterLoad, self)._add_custom_sql_clause(
    #        cr, uid, context=context)
    #    res.append("")
    #    return res
