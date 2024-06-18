# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Segments(models.Model):
    _name = 'reclutamiento__kuale.segments'
    _description = 'reclutamiento__kuale.segments'

    active = fields.Boolean(default=True)
    name = fields.Char()
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    department_ids = fields.Many2many('hr.department', 'department_segment_rel', 'segment_id', 'dep_id',
                                      string='Department')

    # employee_ids = fields.Many2many('hr.employee', 'employee_category_rel', 'category_id', 'emp_id',
    #                                string='Employees')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Segment name already exists!"),
    ]