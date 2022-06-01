from odoo import api, fields, models


class BookVenueConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    # note = fields.HTML(string="Note")
    # note = fields.Char(string="Note", required=False, )

