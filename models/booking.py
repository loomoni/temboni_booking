from stdnum.at import uid

from odoo import api, fields, models, _
import datetime

from odoo.api import cr


class Book(models.Model):
    _name = "book"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "booking Table"
    _rec_name = "name_seq"
    _order = "id desc"

    # The code to control the onchange according to the section of the venue
    @api.onchange('name')
    def _onchange_name_id(self):
        sections = []
        for section in self.name.venue_section_name_tab:
            sections.append(section.id)
        return {'domain': {'section_name': [('id', 'in', sections)]}}

    #  this code controls the clicked smart button
    # @api.multi
    def open_booked_venue(self):
        return {
            'name': _('Booking'),
            'domain': [('name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'book',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    #     compute the number where the venue is booked by count in each booking time
    def get_booked_count(self):
        count = self.env['book'].search_count([('name', '=', self.id)])
        self.booked_times = count

    name = fields.Many2one(comodel_name="create.venue", string="Venue Name", required=True,
                           track_visibility='onchange', )
    customer_name_add = fields.Many2one(comodel_name="res.partner", string="Customer Name", required=True, )
    customer_name = fields.Many2one(comodel_name="customer.add", string="Customer Name", required=False, )
    section_name = fields.Many2one(comodel_name="venue.section", string="Section", required=False, )
    date_from = fields.Date(string="Date", required=True, track_visibility='onchange', )

    date_to = fields.Date(string="Date to", required=False, )
    # date_to = fields.Datetime(string="End Date", required=False, track_visibility='onchange', )
    event_type = fields.Selection(string="Event Type",
                                  selection=[('wedding', 'Wedding'),
                                             ('sendoff', 'Send off'),
                                             ('kitchenparty', 'Kitchen Party'),
                                             ('kipaimara', 'Kipa Imara'),
                                             ('birthday', 'Birthday'),
                                             ('graduation', 'Graduation Ceremony'),
                                             ('meeting', 'Meeting'),
                                             ('conference', 'Conference'), ],

                                  required=False, )
    no_participant = fields.Integer(string="Number of Participant", required=True, )
    rate = fields.Float(string="Rate", required=False, compute="_compute_according_to_day", store=True)
    total = fields.Integer(string="Total", required=False, compute="_compute_total", store=True)
    # venue_id = fields.Many2one(comodel_name="basic.information.venue", string="Venue", required=True, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('refuse', 'Refused'),
        ('approve', 'Approved'), ],
        string="Status", default='draft',
        track_visibility='onchange', )

    name_seq = fields.Char(string='Booking Reference', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    booked_times = fields.Integer(string="Booked Time", required=False, compute="get_booked_count")

    active = fields.Boolean("Active", default=True)
    date = fields.Date(string="Date", required=False, )

    event_day = fields.Selection(string="Event Day", selection=[('monday', 'Monday'), ('tuesday', 'Tuesday'),
                                                                ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
                                                                ('friday', 'Friday'), ('saturday', 'Saturday'),
                                                                ('sunday', 'Sunday'), ], default='saturday',
                                 required=True,
                                 track_visibility='onchange', store=True)
    charge_method = fields.Selection(string="Charge Method",
                                     selection=[('section', 'Per Section'),
                                                ('participant', 'Per Participant'), ],
                                     default="participant", required=True, )
    participant_tab = fields.One2many(comodel_name="participant.tab.book", inverse_name="per_participant_id",
                                      string="Participant Method", required=False, )
    payment_term_tab = fields.One2many(comodel_name="payment.terms.tab", inverse_name="payment_term_id", string="",
                                       required=False, )
    per_venue_tab = fields.One2many(comodel_name="per.venue.tab", inverse_name="per_venue_tab_id",
                                    string="Per Venue ID", required=False, )
    per_section_venue_term_tab = fields.One2many(comodel_name="payment.per.section.terms.tab",
                                                 inverse_name="payment_per_section_term_id", string="Per Section Terms",
                                                 required=False, )

    amount_total = fields.Float(string="Total", required=False, compute="_total_booking_cost", store=True)
    booking_payment_id = fields.Many2one(comodel_name="venue.payment", string="Booking Payment", required=False, )
    check_discount = fields.Boolean(string="Discount", )
    discount_amount = fields.Float(string="Discount Amount",
                                   help="Activate the discount button if "
                                        "a customer have discount otherwise leave it as false",
                                   required=False, )
    food_select_id = fields.One2many(comodel_name="food.select.tab", inverse_name="per_food_tab_id",
                                     string="Food Selection", required=False, )
    system_select_id = fields.One2many(comodel_name="system.select.tab", inverse_name="per_system_tab_id",
                                       string="System Selection", required=False, )
    decoration_select_id = fields.One2many(comodel_name="decoration.select.tab", inverse_name="per_decoration_tab_id",
                                           string="Decoration Selection", required=False, )
    others_select_id = fields.One2many(comodel_name="others.select.tab", inverse_name="per_others_tab_id",
                                       string="Others Selection", required=False, )

    section_rate_id = fields.Many2one(comodel_name="section.tab", string="Section Rate", required=False, )
    hall_fee = fields.Float(string="Hall Fee", compute='_total_booking_cost', required=False, store=False)
    hall_fee_sub_cost = fields.Float(string="hall fee cost", required=False, )

    @api.depends('name', 'section_name', 'event_day')
    def _compute_according_to_day(self):
        for rec in self:
            for hall in rec.name:
                if hall.id == rec.name.id:
                    for section in rec.name.venue_section_name_tab:
                        if section.id == rec.section_name.id:
                            for eventday in rec.name.participant_tab:
                                if rec.event_day == eventday.day:
                                    rec.rate = eventday.rate

    @api.depends('name', 'section_name', 'event_day')
    def _compute_hall_fee(self):
        for rec in self:
            for section in rec.name.venue_section_name_tab:
                for section_day in rec.name.section_tab_line:
                    if [rec.section_name.id == section.id and rec.event_day == section_day.day]:
                        rec.hall_fee = section_day.rate

    @api.depends("no_participant", "rate")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.no_participant * rec.rate

    # The code to calculate the sum of the cost per participants in booking part
    @api.depends('participant_tab.total', 'discount_amount',
                 'per_venue_tab.total_cost', 'charge_method',
                 'food_select_id.total_cost', 'system_select_id.total_cost',
                 'decoration_select_id.total_cost', 'others_select_id.total_cost',
                 'name', 'section_name', 'event_day', 'section_rate_id', 'hall_fee', 'total')
    def _total_booking_cost(self):
        # self.hall_fee = 0
        if self.charge_method == "participant":
            self.amount_total = self.total
            self.amount_total = self.amount_total - self.discount_amount
        else:
            for section in self.name.venue_section_name_tab:
                for section_day in self.name.section_tab_line:
                    if ['&', ('section_name', '=', 'section.venue_section_name'), ('event_day', '=', 'section_day.day')]:
                        self.hall_fee_sub_cost = section_day.rate
            self.sub_amount_total = self.hall_fee_sub_cost + sum(line.total_cost for line in self.per_venue_tab)
            self.add_food_price = self.sub_amount_total + sum(line.total_cost for line in self.food_select_id)
            self.add_system_price = self.add_food_price + sum(line.total_cost for line in self.system_select_id)
            self.add_decoration_price = self.add_system_price + sum(
                line.total_cost for line in self.decoration_select_id)
            self.add_others_price = self.add_decoration_price + sum(line.total_cost for line in self.others_select_id)
            self.amount_total = self.add_others_price - self.discount_amount

    # Status bar control code part
    def confirm_allocation(self):
        self.ensure_one()
        self.state = 'confirm'

    def approve_request(self):
        self.ensure_one()
        self.state = 'approve'

    def refuse_request(self):
        self.ensure_one()
        self.state = 'refuse'

    # Generating a rondom different number
    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('venue.booking.sequence') or _('New')
        result = super(Book, self).create(vals)
        return result


class ParticipantTab(models.Model):
    _name = "participant.tab.book"
    _description = "participant method payment table"
    _rec_name = "no_participant"

    no_participant = fields.Integer(string="Number of Participant", required=False, )
    rate = fields.Float(string="Rate", required=False, compute="_compute_according_to_day", store=True)
    total = fields.Integer(string="Total", required=False, compute="_compute_total", store=True)
    per_participant_id = fields.Many2one(comodel_name="book", string="Participant ID", required=False, )
    participant_per_day = fields.One2many(comodel_name="participant.tab", inverse_name="participant_day_id",
                                          string="Participant Per Day", required=False, )

    @api.depends("no_participant", "rate")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.no_participant * rec.rate


class PaymentTermsTab(models.Model):
    _name = "payment.terms.tab"
    _description = "payment term method"
    _rec_name = "payment_terms_per_participant"

    payment_terms_per_participant = fields.Text(string="Payment Terms", required=False, )
    payment_term_id = fields.Many2one(comodel_name="book", string="Payment ID", required=False, )


class PerVenueTab(models.Model):
    _name = "per.venue.tab"
    _description = "payment per venue"
    _rec_name = "section_fields"

    section_fields = fields.Many2one(comodel_name="product.product", string="Drink", )
    quantity = fields.Integer(string="Quantity", required=False, )
    unit_cost = fields.Float(string="Unit Cost", related="section_fields.lst_price", required=False, )
    total_cost = fields.Integer(string="Total", required=False, compute="_compute_facility_cost")
    per_venue_tab_id = fields.Many2one(comodel_name="book", string="Per Venue ID", required=False, )

    @api.depends("quantity", "unit_cost")
    def _compute_facility_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost


class FoodSelectTab(models.Model):
    _name = "food.select.tab"
    _description = "Food select category"
    _rec_name = "food_fields"

    food_fields = fields.Many2one(comodel_name="food.tab", string="Food", )
    quantity = fields.Integer(string="Quantity", required=False, )
    unit_cost = fields.Float(string="Unit Cost", related="food_fields.selling_price", required=False, )
    total_cost = fields.Integer(string="Total", required=False, compute="_compute_facility_cost")
    per_food_tab_id = fields.Many2one(comodel_name="book", string="Per Venue ID", required=False, )

    @api.depends("quantity", "unit_cost")
    def _compute_facility_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost


class SystemSelectTab(models.Model):
    _name = "system.select.tab"
    _description = "System select category"
    _rec_name = "system_fields"

    system_fields = fields.Many2one(comodel_name="system.tab", string="System", )
    quantity = fields.Integer(string="Quantity", required=False, )
    unit_cost = fields.Float(string="Unit Cost", related="system_fields.selling_price", required=False, )
    total_cost = fields.Integer(string="Total", required=False, compute="_compute_facility_cost")
    per_system_tab_id = fields.Many2one(comodel_name="book", string="Per Venue ID", required=False, )

    @api.depends("quantity", "unit_cost")
    def _compute_facility_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost


class DecorationSelectTab(models.Model):
    _name = "decoration.select.tab"
    _description = "decoration select category"
    _rec_name = "decoration_fields"

    decoration_fields = fields.Many2one(comodel_name="decoration.tab", string="System", )
    quantity = fields.Integer(string="Quantity", required=False, )
    unit_cost = fields.Float(string="Unit Cost", related="decoration_fields.selling_price",
                             required=False, )
    total_cost = fields.Integer(string="Total", required=False, compute="_compute_facility_cost")
    per_decoration_tab_id = fields.Many2one(comodel_name="book", string="Per Venue ID", required=False, )

    @api.depends("quantity", "unit_cost")
    def _compute_facility_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost


class OthersSelectTab(models.Model):
    _name = "others.select.tab"
    _description = "Others select category"
    _rec_name = "others_fields"

    others_fields = fields.Many2one(comodel_name="others.tab", string="System", )
    quantity = fields.Integer(string="Quantity", required=False, )
    unit_cost = fields.Float(string="Unit Cost", related="others_fields.selling_price",
                             required=False, )
    total_cost = fields.Integer(string="Total", required=False, compute="_compute_facility_cost")
    per_others_tab_id = fields.Many2one(comodel_name="book", string="Per Venue ID", required=False, )

    @api.depends("quantity", "unit_cost")
    def _compute_facility_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost


class PaymentPerSectionTermsTab(models.Model):
    _name = "payment.per.section.terms.tab"
    _description = "payment term per section"
    _rec_name = "payment_terms_per_participant"

    payment_terms_per_participant = fields.Text(string="Payment Terms", required=False, )
    payment_per_section_term_id = fields.Many2one(comodel_name="book", string="Payment ID", required=False, )
