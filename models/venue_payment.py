from odoo import api, fields, models, _
import datetime


class AccountInvoiceGenerator(models.Model):
    _inherit = "account.invoice"
    _order = "id desc"

    ref_number = fields.Many2one(comodel_name="book", string="Ref Number", required=True, )
    amount_untaxed = fields.Float(string="Total Cost", required=False, related="ref_number.amount_total")
    booking_payment = fields.One2many(comodel_name="book",
                                      inverse_name="booking_payment_id", string="Booking Payment",
                                      required=False, store=True)
    name = fields.Char(string="Venue Name",
                       related="ref_number.name.name",
                       required=False, )

    @api.one
    @api.depends('booking_payment.amount_total')
    def _compute_amount(self):
        self.amount_total = self.booking_payment.amount_total + self.amount_untaxed + self.amount_tax
        # self.amount_total_company_signed = self.amount_total
        # self.amount_untaxed_signed = self.amount_untaxed
        amount_total_company_signed = self.amount_total


class VenuePayment(models.Model):
    _name = "venue.payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Venue Payment Table"
    _rec_name = "ref_number"

    ref_number = fields.Many2one(comodel_name="book", string="Ref Number", required=True, )
    customer_name_add = fields.Many2one(comodel_name="res.partner", string="Customer Name", )
    name = fields.Char(string="Venue Name", related="ref_number.name.name", required=False, )
    email = fields.Char(string="Email", related="ref_number.customer_name.email", copy=False)
    # payment_reference = fields.Float(string="Payment Reference", required=False, compute="_according_to_venue")
    payment_reference = fields.Char(string='Payment Reference', required=True, copy=False, readonly=True, index=True,
                                    default=lambda self: _('New'))
    payment_amount = fields.Float(string="Payed Amount", required=False, )
    due_date = fields.Datetime(string="Date", required=False, default=fields.Datetime.now(), )
    total_venue_book_cost = fields.Integer(string="Sub Total", required=False, compute="_total_cost_compute",
                                           store=True)
    products_lines = fields.One2many(comodel_name="product.lines", inverse_name="product_field_id", string="Products",
                                     required=False, )
    booking_payment = fields.One2many(comodel_name="book", inverse_name="booking_payment_id", string="",
                                      required=False, )
    total_cost = fields.Float(string="Total Cost", required=False, related="ref_number.amount_total")
    things_paid = fields.Html(string="Paid For", required=False, store=True)
    payment_widget = fields.Text(string="Customer Payment", required=False, )
    partner_field_id = fields.Many2one(comodel_name="res.users", string="PRO", required=False, )
    # wizard_down_payment_field = fields.Many2one(comodel_name="create.down.payment", string="down payment", required=False, )

    # payed_items = fields.Char(string="Paid For", required=False, )
    # compute = "_compute_venue_total_cost"
    # Try code from hotel management for the calculation of payment
    amount_paid = fields.Float(
        compute="_compute_amount_paid", method=True, string="Amount Paid", store=True
    )
    # tax = fields.Float("Tax (%) ")

    amount_unpaid = fields.Float(
        compute="_compute_amount_remain", method=True, string="Unpaid Amount", store=True
    )
    state = fields.Selection(string="",
                             selection=[('', ''),
                                        ('', ''), ],
                             required=False, )

    # Generating a rondom different number
    @api.model
    def create(self, vals):
        if vals.get('payment_reference', _('New')) == _('New'):
            vals['payment_reference'] = self.env['ir.sequence'].next_by_code('venue.payment.sequence') or _('New')
        result = super(VenuePayment, self).create(vals)
        return result

    @api.depends('booking_payment.amount_total', 'name.name.name', 'booking_payment.name')
    def _compute_venue_total_cost(self):
        for rec in self:
            rec.total_cost = rec.booking_payment.amount_total

    # Computation for the the total money paid
    @api.depends("payment_amount")
    def _compute_amount_paid(self):
        for rec in self:
            rec.amount_paid = rec.payment_amount
        return rec.amount_paid

    #     compute amount remain after the initial payment
    @api.depends('payment_amount', 'total_cost')
    def _compute_amount_remain(self):
        for rec in self:
            rec.amount_unpaid = rec.total_cost - rec.payment_amount
            # rec.total_cost = rec.amount_paid

    # This is action to send email when is need after making payment
    def action_send_registered_payment(self):
        template_id = self.env.ref('om_venue_booking.register_payment_email_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)


class ProductLines(models.Model):
    _name = "product.lines"
    _description = "This is are the lines to show producuts"

    product_field = fields.Many2one(comodel_name="product.product", string="Products",
                                    column1="standard_price",
                                    column2="", required=True, )
    product_qty = fields.Integer(string="Quantity", required=False, )
    sub_price = fields.Float(string="Sub Price", required=False, )
    total_price = fields.Integer(string="Total Price", required=False, compute="_total_product_price", )
    product_field_id = fields.Many2one(comodel_name="venue.payment", string="Product ID", required=False, )

    # Produce the quantity total price unit per item
    @api.depends('sub_price', 'product_qty')
    def _total_product_price(self):
        for rec in self:
            rec.total_price = rec.sub_price * rec.product_qty
        return rec.total_price
