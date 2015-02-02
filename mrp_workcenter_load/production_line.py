# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm
from .workcenter import WORKCENTER_ACTION


class MrpProductionWorkcenterLine(orm.Model):
    _inherit = 'mrp.production.workcenter.line'

    def button_workcenter(self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            view_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'mrp', 'mrp_workcenter_view')[1]
            action = {
                'view_id': view_id,
                'res_id': elm.workcenter_id.id,
                'name': "'%s' Workcenter" % elm.name,
                'name': 'Workcenter',
            }
            action.update(WORKCENTER_ACTION)
            action['view_mode'] = 'form'
            action['view_type'] = 'form'
            return action
