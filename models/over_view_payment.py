from odoo import api, fields, models


class OverViewPayment(models.Model):
    _name = "over.view.payment"
    _description = "Over View Table to show current venue Status"

    name = fields.Char(string="Venue Name", required=False, )
    section_name = fields.Char(string="Section Name", required=False, )
    status = fields.Char(string="Status", required=False, )
    payment_reference = fields.Char(string="Payment Reference", required=False, )
    customer = fields.Char(string="Customer Name", required=False, )

