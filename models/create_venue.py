# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime


class CreateVenue(models.Model):
    _name = "create.venue"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Create venue data table"

    # @api.onchange('name')
    # def _onchange_name_id(self):
    #     sections = []
    #     for section in self.venue_section_name_tab:
    #         sections.append(section.id)
    #     return {'domain': {'venue_section_name_tab': [('id', 'in', sections)]}}

    name = fields.Char(string="Venue Name", copy=False, required=True)
    location = fields.Char(string="Location", copy=False, required=False)
    supervisor = fields.Many2one(comodel_name="res.partner", string="Supervisor", required=False, )
    image = fields.Binary(string="Image", required=False)
    charge_cost = fields.Selection(string="Charge Method",
                                   selection=[('section', 'Per Section'),
                                              ('participant', 'Per Participant'), ],
                                   default="participant", required=True, )
    total_cost = fields.Integer(string="Total Cost: ", required=False, compute="_total_cost_compute", store=True)
    # Reverse line that takes in the line products and sections
    section_tab_line = fields.One2many(comodel_name="section.tab", inverse_name="section_id", string="Section Venue",
                                       required=False, )
    participant_tab = fields.One2many(comodel_name="participant.tab", inverse_name="participant_id",
                                      string="Section Venue",
                                      required=False, )
    # drink_tab = fields.One2many(comodel_name="drinks.tab", inverse_name="drink_tabs_id", string="Drinks",
    #                             required=False, )
    food_tab = fields.One2many(comodel_name="food.tab", inverse_name="food_id", string="Food",
                               required=False, )
    system_tab = fields.One2many(comodel_name="system.tab", inverse_name="system_id", string="System",
                                 required=False, )
    decoration_tab = fields.One2many(comodel_name="decoration.tab", inverse_name="decoration_id", string="System",
                                     required=False, )
    others_tab = fields.One2many(comodel_name="others.tab", inverse_name="others_id", string="Others",
                                 required=False, )
    venue_section_name_tab = fields.One2many(comodel_name="venue.section", inverse_name="venue_section_id", string="",
                                             required=False, )


class SectionTab(models.Model):
    _name = "section.tab"
    _description = "Section add Lines"
    _rec_name = "name"

    name = fields.Many2one(comodel_name="venue.section", string="Section Name", required=False, )
    day = fields.Selection(string="Day",
                           selection=[('monday', 'Monday'), ('tuesday', 'Tuesday'),
                                      ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
                                      ('friday', 'Friday'), ('saturday', 'Saturday'),
                                      ('sunday', 'Sunday'), ], required=False, )
    rate = fields.Float(string="Rate", required=False, )
    section_id = fields.Many2one(comodel_name="create.venue", string="Section ID", )
    section_move_rate_id = fields.One2many(comodel_name="book", inverse_name="section_rate_id", string="Section rate id", required=False, )


class FoodTab(models.Model):
    _name = "food.tab"
    _description = "Food add Lines"
    _rec_name = "package_name"

    package_name = fields.Char(string="Package name", required=False, )
    package_size = fields.Char(string="Size", required=False, )
    selling_price = fields.Float(string="Selling Price", required=False, )
    include = fields.Char(string="Include", required=False, )
    food_id = fields.Many2one(comodel_name="create.venue", string="Food ID", required=False, )


class SystemTab(models.Model):
    _name = "system.tab"
    _description = "System add Lines"
    _rec_name = "package_name"

    package_name = fields.Char(string="Package name", required=False, )
    selling_price = fields.Float(string="Selling Price", required=False, )
    include = fields.Char(string="Include", required=False, )
    system_id = fields.Many2one(comodel_name="create.venue", string="Food ID", required=False, )


class DecorationTab(models.Model):
    _name = "decoration.tab"
    _description = "Decoration add Lines"
    _rec_name = "package_name"

    package_name = fields.Char(string="Package name", required=False, )
    selling_price = fields.Float(string="Selling Price", required=False, )
    include = fields.Char(string="Include", required=False, )
    decoration_id = fields.Many2one(comodel_name="create.venue", string="Food ID", required=False, )


class OthersTab(models.Model):
    _name = "others.tab"
    _description = "Others add Lines"
    _rec_name = "package_name"

    package_name = fields.Char(string="Package name", required=False, )
    selling_price = fields.Float(string="Selling Price", required=False, )
    include = fields.Char(string="Include", required=False, )
    others_id = fields.Many2one(comodel_name="create.venue", string="Others ID", required=False, )

    # @api.depends('charge_cost')
    # def _total_cost_compute(self):
    #     for rec in self:
    #         rec.total_cost = rec.charge_cost * 2 + rec.charge_cost
    #     return rec.total_cost


#    This are the line that the controll the charge per participants
class ChargeParticipantTab(models.Model):
    _name = "participant.tab"
    _description = "Charger per participant add Lines"
    _rec_name = "day"

    day = fields.Selection(string="Day",
                           selection=[('monday', 'Monday'), ('tuesday', 'Tuesday'),
                                      ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
                                      ('friday', 'Friday'), ('saturday', 'Saturday'),
                                      ('sunday', 'Sunday'), ], required=False, )
    rate = fields.Float(string="Rate", required=False, )
    participant_id = fields.Many2one(comodel_name="create.venue", string="Section ID", )
    participant_day_id = fields.Many2one(comodel_name="participant.tab.book", string="Participant day ID",
                                         required=False, )


class VenueSection(models.Model):
    _name = "venue.section"
    _description = "Table to carry venue content"
    _rec_name = 'venue_section_name'

    venue_section_name = fields.Char(string="Section Name", required=False, )
    venue_section_size = fields.Integer(string="Size", required=False, )
    venue_section_id = fields.Many2one(comodel_name="create.venue", string="Section Name", required=False, )
