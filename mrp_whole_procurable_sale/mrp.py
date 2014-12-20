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
    _inherit = ['mrp.production', 'abstract.selection.rotate']
    _name = 'mrp.production'

    def _set_schedule_states(self, cr, uid, context=None):
        states = super(MrpProduction, self)._set_schedule_states(
            cr, uid, context=context)
        states.append(('25', 'Pending'))
        states = list(set(states))
        states.sort(key=lambda t: t[0])
        return states

    def set_planable_mo(self, cr, uid, ids, context=None):
        """ Set the MO as to able to be manufactured (20, To Do)
            if all the MO of the sale can be manufactured
        """
        for mo in self.browse(cr, uid, ids, context=context):
            if mo.sale_order_id:
                mrp_ids = self.search(cr, uid, [
                    ('sale_order_id', '=', mo.sale_order_id.id)],
                    context=context)
                sale = mo.sale_order_id
                manuf_product_ids = [
                    l.product_id.id
                    for l in sale.order_line
                    if l.product_id.supply_method == 'produce']
                if len(manuf_product_ids) > len(mrp_ids):
                    return True
                procurable_sale = True
                mo_ids = []
                for production in self.browse(
                        cr, uid, mrp_ids, context=context):
                    print production.name
                    if production.state not in ['ready']:
                        procurable_sale = procurable_sale and False
                    else:
                        mo_ids.append(production.id)
                if procurable_sale:
                    vals = {'schedule_state': '20'}
                    self.write(cr, uid, mo_ids, vals, context=context)
        return True

    def action_ready(self, cr, uid, ids, context=None):
        " Standard method "
        super(MrpProduction, self).action_ready(cr, uid, ids, context=context)
        self.set_planable_mo(cr, uid, ids, context=context)

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        res = super(MrpProduction, self)._get_values_from_selection(
            cr, uid, ids, field, context=context)
        if field == 'schedule_state':
            # also check model name ?
            res = self._set_schedule_states(cr, uid, context=context)
            del res[0]
        return res
