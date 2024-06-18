from odoo import models, fields, api


class PerformanceStandars(models.Model):
    _name = 'reclutamiento__kuale.performance_standars'
    _description = 'reclutamiento__kuale.performance_standars'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    # Relation Job
    job_ids = fields.Many2many('hr.job', 'job_performancest_rel', 'perfst_id', 'job_id', string='Job')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "External relation name already exists!"),
    ]
