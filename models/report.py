from odoo import api, fields, models


class ReportPrint(models.Model):
    _name = "report.print"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Addition of the customer table"

    name = fields.Char(string="Name", required=False, )