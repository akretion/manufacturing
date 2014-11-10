# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'auto_manufacturing_order': fields.boolean(
            'Auto Manuf. Order',
            help="Check if Manufacturing Order of this product "
                 "can be confirmed automatically "
                 "by a planned task (cron)")
    }

    _defaults = {
        'auto_manufacturing_order': False,
    }


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def mo_auto_confirm_cron(self, cr, uid, context=None):
        mo_ids = self.search(
            cr, uid, [('state', 'in', ['draft'])], context=context)
        for production in self.browse(cr, uid, mo_ids, context=context):
            if production.product_id.auto_manufacturing_order:
                self.action_confirm(cr, uid, [production.id], context=context)
        return True

