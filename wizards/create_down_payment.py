from odoo import api, fields, models, _


class CreateDownPayment(models.TransientModel):
    _name = "create.down.payment"
    _description = "Wizard to caption small payment that are made in time"

    # ref_number = fields.Many2one(comodel_name="venue.payment", string="", required=False, )
    down_payment = fields.Float(string="Payment Amount", required=True, )
    date = fields.Date(string="Payment Date", required=True, )

    def action_register_save(self):
        print("This is the call")
