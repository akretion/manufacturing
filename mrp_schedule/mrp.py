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


class MrpProduction(orm.Model):
    _inherit = ['mrp.production', 'abstract.selection.rotate']
    _name = 'mrp.production'

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
            help="Planification State"),
    }

    _defaults = {
        'schedule_state': 'unable',
    }

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        res = super(MrpProduction, self)._get_values_from_selection(
            cr, uid, ids, field, context=context)
        if field == 'schedule_state':
            # also check model name ?
            # get states and drop 'unable' state
            res = self._set_schedule_states(cr, uid, context=context)[1:]
        return res


class MrpProductionWorkcenterLine(orm.Model):
    _inherit = ['mrp.production.workcenter.line', 'abstract.selection.rotate']
    _name = 'mrp.production.workcenter.line'

    _columns = {
        'schedule_state': fields.related(
            'production_id', 'schedule_state',
            type='char',
            string='MO Schedule',
            help=""),
    }

    def _iter_selection(self, cr, uid, ids, direction, context=None):
        """ Allows to update the field selection to its next value
            here, we pass through the related field
            to go towards 'schedule_state' in mrp.production
        """
        for elm in self.browse(cr, uid, ids, context=context):
            self.pool['mrp.production']._iter_selection(
                cr, uid, [elm.production_id.id], direction, context=context)
        return True
