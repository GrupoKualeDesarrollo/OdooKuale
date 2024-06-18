from odoo import models, fields, api
# Modelo para Tipo de Giro
class BusinessType(models.Model):
    _name = 'reclutamiento__kuale.business.type'
    _description = 'Business Type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ], string='Estatus', default='Activo', required=True)
