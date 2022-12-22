from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create_transfer_from_pos(self, values):
        pick_values = {}
        pos_session = values.get('pos_session')
        lead_time = 0

        picking_type_id = values['transfer_picking_type_id']
        pick_values['picking_type_id'] = picking_type_id
        picking_type = self.env['stock.picking.type'].browse(picking_type_id)
        pick_values['location_id'] = picking_type.default_location_src_id.id
        pick_values['location_dest_id'] = picking_type.default_location_dest_id.id
        pick_values['note'] = values.get('transfer_note')

        if pos_session:
            session_id = self.env['pos.session'].browse(pos_session)
            lead_time = session_id.config_id.transfer_lead_time
            pick_values['scheduled_date'] = datetime.now() + relativedelta(days=lead_time)

        lines = [line[2] for line in values['lines']]
        product_ids = [x[2]['product_id'] for x in values['lines']]
        products = self.env['product.product'].browse(product_ids)
        source_locations = products.mapped('categ_id.source_location_id')

        for line in lines:
            product = self.env['product.product'].browse(line['product_id'])
            line['categ_id'] = product.categ_id.id
            line['source_location_id'] = product.categ_id.source_location_id.id

        lines_with_source_location = [l for l in lines if l['source_location_id']]
        lines_without_source_location = [l for l in lines if not l['source_location_id']]

        created_pickings = []
        created_pickings_names = ''
        for sl in source_locations:
            move_lines = []
            sline_to_create = [l for l in lines_with_source_location if l['source_location_id'] == sl.id]
            for sl_create in sline_to_create:
                product = self.env['product.product'].browse(sl_create['product_id'])
                move_lines.append((0, 0, {
                    'product_id': sl_create['product_id'],
                    'product_uom_qty': sl_create['qty'],
                    'name': product.name,
                    'product_uom': product.uom_id.id,
                    'procure_method': 'make_to_stock',
                    'location_id': sl_create['source_location_id'],
                    'location_dest_id': picking_type.default_location_dest_id.id,
                }))
            pick_values['location_id'] = sl.id
            pick_values['move_lines'] = move_lines
            new_pick = self.env['stock.picking'].create(pick_values)
            del pick_values['name']
            created_pickings.append(new_pick.name)
            created_pickings_names = created_pickings_names + ' \n ' + new_pick.name

        if lines_without_source_location:
            for nsl_create in lines_without_source_location:
                move_lines = []
                product = self.env['product.product'].browse(nsl_create['product_id'])
                move_lines.append((0, 0, {
                    'product_id': nsl_create['product_id'],
                    'product_uom_qty': nsl_create['qty'],
                    'name': product.name,
                    'product_uom': product.uom_id.id,
                    'procure_method': 'make_to_stock',
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                }))
            pick_values['location_id'] = picking_type.default_location_src_id.id
            pick_values['move_lines'] = move_lines
            new_pick = self.env['stock.picking'].create(pick_values)
            del pick_values['name']
            created_pickings.append(new_pick.name)
            created_pickings_names = created_pickings_names + ' \n ' + new_pick.name

        return {'result': created_pickings_names, 'id': picking_type.id}

    @api.model
    def create_return_from_pos(self, values):
        move_lines = []
        pick_values = {}
        pos_session = values.get('pos_session')
        lead_time = 0

        picking_type_id = values['return_picking_type_id']
        pick_values['picking_type_id'] = picking_type_id
        picking_type = self.env['stock.picking.type'].browse(picking_type_id)
        pick_values['location_id'] = picking_type.default_location_src_id.id
        pick_values['note'] = values.get('return_note')
        pick_values['location_dest_id'] = picking_type.default_location_dest_id.id

        if pos_session:
            session_id = self.env['pos.session'].browse(pos_session)
            lead_time = session_id.config_id.transfer_lead_time
            pick_values['scheduled_date'] = datetime.now() + relativedelta(days=lead_time)

        lines = [line[2] for line in values['lines']]
        product_ids = [x[2]['product_id'] for x in values['lines']]
        products = self.env['product.product'].browse(product_ids)
        destination_locations = products.mapped('categ_id.destination_location_id')

        for line in lines:
            product = self.env['product.product'].browse(line['product_id'])
            line['categ_id'] = product.categ_id.id
            line['destination_location_id'] = product.categ_id.destination_location_id.id

        lines_with_destination_location = [l for l in lines if l['destination_location_id']]
        lines_without_destination_location = [l for l in lines if not l['destination_location_id']]

        created_pickings = []
        created_pickings_names = ''
        for dl in destination_locations:
            move_lines = []
            dline_to_create = [l for l in lines_with_destination_location if l['destination_location_id'] == dl.id]
            for dl_create in dline_to_create:
                product = self.env['product.product'].browse(dl_create['product_id'])
                move_lines.append((0, 0, {
                    'product_id': dl_create['product_id'],
                    'product_uom_qty': dl_create['qty'],
                    'name': product.name,
                    'product_uom': product.uom_id.id,
                    'procure_method': 'make_to_stock',
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': dl_create['destination_location_id'],
                }))
            pick_values['location_dest_id'] = dl.id
            pick_values['move_lines'] = move_lines
            new_pick = self.env['stock.picking'].create(pick_values)
            del pick_values['name']
            created_pickings.append(new_pick.name)
            created_pickings_names = created_pickings_names + ' \n ' + new_pick.name

        if lines_without_destination_location:
            for ndl_create in lines_without_destination_location:
                move_lines = []
                product = self.env['product.product'].browse(ndl_create['product_id'])
                move_lines.append((0, 0, {
                    'product_id': ndl_create['product_id'],
                    'product_uom_qty': ndl_create['qty'],
                    'name': product.name,
                    'product_uom': product.uom_id.id,
                    'procure_method': 'make_to_stock',
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                }))
            pick_values['location_dest_id'] = picking_type.default_location_dest_id.id
            pick_values['move_lines'] = move_lines
            new_pick = self.env['stock.picking'].create(pick_values)
            del pick_values['name']
            created_pickings.append(new_pick.name)
            created_pickings_names = created_pickings_names + ' \n ' + new_pick.name

        return {'result': created_pickings_names, 'id': picking_type.id}


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_return = fields.Boolean(string="Is Return")
