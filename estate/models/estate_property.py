# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate"

    def _default_date_availability(self):
        return fields.Datetime.today(self) + relativedelta(months=3)

    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: self._default_date_availability())
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=False)
    state = fields.Selection([('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')], required=True, copy=False, default='new')

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", readonly=True, copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Float(copy=False, string='Total Area (sqm)', compute='_compute_total_area')
    best_price = fields.Float(copy=False, string='Best Offer', compute='_compute_best_price')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        if self.state == 'canceled':
            raise UserError(_("Canceled properties cannot be sold."))
        else:
            self.state = 'sold'

    # Recommend This Way
    # def action_sold(self):
    #     if "canceled" in self.mapped("state"):
    #         raise UserError("Canceled properties cannot be sold.")
    #     return self.write({"state": "sold"})

    def action_cancel(self):
        if self.state == 'sold':
            raise UserError(_("Sold properties cannot be canceled."))
        else:
            self.state = 'canceled'

    # Recommend This Way
    # def action_cancel(self):
    #     if "sold" in self.mapped("state"):
    #         raise UserError("Sold properties cannot be canceled.")
    #     return self.write({"state": "canceled"})