from odoo import models, fields, api


class Age(models.Model):
    _name = 'reclutamiento__kuale.age'
    _description = 'reclutamiento__kuale.age'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    job_ids = fields.Many2many('hr.job', 'job_age_rel', 'age_id', 'job_id', string='Job')

    # employee_ids = fields.Many2many('hr.employee', 'employee_category_rel', 'category_id', 'emp_id',
    #                                string='Employees')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Age range name already exists!"),
    ]
