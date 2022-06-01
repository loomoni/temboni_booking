from odoo import api, fields, models


class CustomerAdd(models.Model):
    _name = "customer.add"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Addition of the customer table"

    name = fields.Char(string="Name", required=False, )
    image = fields.Binary(string="image", max_width=50, max_height=50)
    phone = fields.Integer(string="Phone", required=False, )
    email = fields.Char(string="Email", required=False, )
    alt_phone = fields.Integer(string="Phone alternative", required=False, )
    no_payment = fields.Integer(string="Number of payment", required=False)
    no_participants = fields.Integer(string="Number of Participants", required=False, )
