# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Schooling(models.Model):
    _name = 'reclutamiento__kuale.schooling'
    _description = "reclutamiento__kuale.schooling"
    _order = "name"

    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text('Description')

    job_ids = fields.Many2many('hr.job', 'job_schooling_rel', 'sch_id', 'job_id', string='Job')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Competencies name already exists!"),
    ]