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


def get_neighbor_element(my_itr, initial=None):
    try:
        val = my_itr.next()
        if initial:
            while val != initial:
                val = my_itr.next()
            val = my_itr.next()
        return val
    except StopIteration:
        return None


class AbstractSelectionRotate(orm.Model):
    _name = 'abstract.selection.rotate'

    def _iter_selection(self, cr, uid, ids, direction, context=None):
        " Allows to update the field selection value "
        if not 'selection_field' in context:
            return True
        field = context['selection_field']
        # extract first value in each tuple as content of the selection field
        values = [elm[0]
                  for elm in self._get_values_from_selection(
                      cr, uid, ids, field, context=context)]
        if direction == 'prev':
            values = reversed(values)
        my_itr = iter(values)
        for item in self.browse(cr, uid, ids, context=context):
            initial = item[field]
            value = get_neighbor_element(my_itr, initial)
            if value is None:
                my_itr = iter(values)
                value = get_neighbor_element(my_itr)
            self.write(cr, uid, item.id, {field: value},
                       context=context)
        return True

    def iter_selection_next(self, cr, uid, ids, context=None):
        """ You can trigger this method by this xml declaration
            in your own view to iterate field selection

            <button name="iter_selection_next"
                    context="{'selection_field': 'my_selection_field'}"
                    icon="gtk-go-forward"
                    type="object"/>
        """
        self._iter_selection(cr, uid, ids, 'next', context=context)

    def iter_selection_prev(self, cr, uid, ids, context=None):
        " see previous method "
        self._iter_selection(cr, uid, ids, 'prev', context=context)

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        """ Override this method
            to return your own list of tuples
            which match with field selection values or a sub part

            [('val1', 'My Val1'),
             ('val2', 'My Val2')]
        """
        return [(), ]
