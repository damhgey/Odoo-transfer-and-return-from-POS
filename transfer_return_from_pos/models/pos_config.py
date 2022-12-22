from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    transfer_lead_time = fields.Integer('Transfer Lead Time')
    operation_type_ids = fields.Many2many(comodel_name="stock.picking.type", string="Operation Types")

