# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _sql_constraints = [
    ('check_price', 'CHECK(price > 0 )',
     'The Price should be positive.'),
    ]
    _order = "price desc"


    price = fields.Float()
    status = fields.Selection([('accepted','Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id= fields.Many2one("estate.property", required=True)

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    )
    
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                date = record.create_date.date()
            else:
                date = fields.Date.today()

            record.date_deadline = date + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                date = record.create_date.date()
            else:
                date = fields.Date.today()
            
            record.validity = (record.date_deadline - date).days
    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            record.update_state()
        return record

    def update_state(self):
        return self.mapped("property_id").write(
            {
                "state": "offer_received",
            }
        )
    # def action_accepted(self):
    #     if "accepted" in self.mapped("property_id.offer_ids.status"):
    #         raise UserError(_("An offer has already been accepted."))
    #     else:
    #         self.status = 'accepted'
    #         self.property_id.selling_price = self.price
    #         self.property_id.buyer_id = self.partner_id

    def action_accepted(self):
        if "accepted" in self.mapped("property_id.offer_ids.status"):
            raise UserError(_("An offer as already been accepted."))
        self.write(
            {
                "status": "accepted",
            }
        )
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer_id": self.partner_id,
            }
        )

    # def action_refused(self):
    #     self.status = 'refused'
    #     self.property_id.selling_price = 0
    #     self.property_id.buyer_id = False

    def action_refused(self):
        self.write(
            {
                "status": "refused"
            }
        )
        return self.mapped("property_id").write(
            {
                "state": "offer_received",
                "selling_price": 0,
                "buyer_id": False,
            }
        )