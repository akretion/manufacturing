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


class SwitchWorkcenter(orm.TransientModel):
    _name = 'switch.workcenter'

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            'Workcenter',
            required=True)
    }

    def switch_workcenter(self, cr, uid, ids, context=None):
        # TODO add a check (child of)
        MrpProdWorkcLine = self.pool['mrp.production.workcenter.line']
        active_ids = context.get('active_ids', [])
        switch_workc = self.browse(cr, uid, ids, context=context)[0]
        vals = {'workcenter_id': switch_workc.workcenter_id.id}
        MrpProdWorkcLine.write(cr, uid, active_ids, vals, context=context)
        return True
