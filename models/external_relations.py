from odoo import models, fields, api


class ExternalRelations(models.Model):
    _name = 'reclutamiento__kuale.external_relations'
    _description = 'reclutamiento__kuale.external_relations'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    # Relation Job
    job_ids = fields.Many2many('hr.job', 'job_externalrel_rel', 'extrel_id', 'job_id', string='Job')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "External relation name already exists!"),
    ]
