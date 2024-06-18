from odoo import models, fields, api


class InternalRelations(models.Model):
    _name = 'reclutamiento__kuale.internal_relations'
    _description = 'reclutamiento__kuale.internal_relations'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    # Relation Job
    job_ids = fields.Many2many('hr.job', 'job_internalrel_rel', 'intrel_id', 'job_id', string='Job')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Internal relation name already exists!"),
    ]


class CommentsExp(models.Model):
    _name = 'reclutamiento__kuale.comments_exp'
    _description = 'reclutamiento__kuale.comments_exp'

    # job_ids = fields.Many2many('hr.job', 'job_exp_rel', 'exp_id', 'job_id', string='Job')

    job_id = fields.Many2one("hr.job", string="Job")
    active = fields.Boolean(default=True)
    name = fields.Char(string='General Comments/Expectations', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Activity name already exists!"),
    ]
