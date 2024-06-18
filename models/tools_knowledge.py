# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OperationalTools(models.Model):
    _name = 'reclutamiento__kuale.tools_knowledge'
    _description = "reclutamiento__kuale.tools_knowledge"
    _order = "name"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    type = fields.Selection([
        ('tool', 'Tool'),
        ('software', 'Software')
    ], required=True)
    description = fields.Text('Description')

    # Relation Job
    job_ids = fields.Many2many('hr.job', 'job_toolknow_rel', 'tool_id', 'job_id', string='Job')
    job_soft_ids = fields.Many2many('hr.job', 'job_software_rel', 'soft_id', 'job_id', string='Job')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tool knowledge name already exists!"),
    ]
