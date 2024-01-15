# -*- coding: utf-8 -*-
from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"

    name = fields.Char(required=True)
