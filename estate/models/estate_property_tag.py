# -*- coding: utf-8 -*-
from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _sql_constraints = [
    ('check_name', 'unique(name)',
     'The Name should be unique.'),
    ]
    _order = "name desc"

    name = fields.Char(required=True)
    color = fields.Integer()
