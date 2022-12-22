from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    source_location_id = fields.Many2one('stock.location', "Source Location", compute='_get_location_ids', inverse='_inverse_location_ids', store=True)
    destination_location_id = fields.Many2one('stock.location', "Destination Location", compute='_get_location_ids', inverse='_inverse_location_ids', store=True)

    @api.depends('parent_id.source_location_id', 'parent_id.destination_location_id')
    def _get_location_ids(self):
        for rec in self:
            source_location_id = False
            destination_location_id = False
            if rec.parent_id.source_location_id:
                source_location_id = rec.parent_id.source_location_id
            if rec.parent_id.destination_location_id:
                destination_location_id = rec.parent_id.destination_location_id
            rec.source_location_id = source_location_id
            rec.destination_location_id = destination_location_id

    def _inverse_location_ids(self):
        pass