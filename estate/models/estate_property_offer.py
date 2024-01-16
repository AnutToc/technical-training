# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"

    price = fields.Float()
    status = fields.Selection([('accepted','Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id= fields.Many2one("estate.property", required=True)

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

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

    def action_accepted(self):
        if "accepted" in self.mapped("property_id.offer_ids.status"):
            raise UserError(_("An offer has already been accepted."))
        else:
            self.status = 'accepted'
            self.property_id.selling_price = self.price
            self.property_id.buyer_id = self.partner_id

    # Recommend This Way
    # def action_accept(self):
    #     if "accepted" in self.mapped("property_id.offer_ids.state"):
    #         raise UserError("An offer as already been accepted.")
    #     self.write(
    #         {
    #             "state": "accepted",
    #         }
    #     )
    #     return self.mapped("property_id").write(
    #         {
    #             "state": "offer_accepted",
    #             "selling_price": self.price,
    #             "buyer_id": self.partner_id.id,
    #         }
    #     )

    def action_refused(self):
        self.status = 'refused'

    # Recommend This Way
    # def action_refuse(self):
    #     return self.write(
    #         {
    #             "state": "refused",
    #         }
    #     )