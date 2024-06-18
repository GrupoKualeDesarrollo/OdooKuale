from odoo import models, fields, api


class Activities(models.Model):
    _name = 'reclutamiento__kuale.activities'
    _description = 'reclutamiento__kuale.activities'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text('Description')
    a_knowledge_ids = fields.One2many('reclutamiento__kuale.a_knowledge', 'activities_k_id', string="Knowledge")

    knowledge_ids = fields.Many2many('reclutamiento__kuale.a_knowledge', 'act_knowledge_rel', string="Knowledge",
                                     domain="[('activities_k_id', '=', active_id)]")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Activity name already exists!"),
    ]

    @api.model
    def default_get(self, fields):
        res = super(Activities, self).default_get(fields)
        res['knowledge_ids'] = self._context.get('active_id', False)
        return res
