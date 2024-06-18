from odoo import fields, models, api
#Modelo  para Tipo de Sucursal
class BranchType(models.Model):
    _name = 'reclutamiento__kuale.branch.type'
    _description = 'Branch Type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ], string='Status', default='Active', required=True)
