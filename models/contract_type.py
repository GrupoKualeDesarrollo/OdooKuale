from odoo import models, fields, api


class ContractType(models.Model):
    _name = 'reclutamiento__kuale.contract_type'
    _description = 'reclutamiento__kuale.contract_type'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company, required=True)
    trial_period_ids = fields.One2many('reclutamiento__kuale.trial_period', 'contract_type_id', string="Trial Period")
    jornada_ids = fields.One2many('reclutamiento__kuale.jornada', 'contract_type_id', string="Levels")
    description = fields.Text('Description')


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Contract type name already exists!"),
    ]
