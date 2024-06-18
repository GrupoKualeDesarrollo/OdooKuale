from odoo import models, fields, api


class Competencies(models.Model):
    _name = 'reclutamiento__kuale.competencies'
    _description = 'reclutamiento__kuale.competencies'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    # Relation Job
    job_ids = fields.Many2many('hr.job', 'job_competencies_rel', 'comp_id', 'job_id', string='Job')
    # job_id = fields.Many2one('hr.job', 'Job', readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Competencies name already exists!"),
    ]
