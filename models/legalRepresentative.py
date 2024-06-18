from odoo import models, fields, api
# Modelo para Representantce Legal
class LegalRepresentative(models.Model):
    _name = 'reclutamiento__kuale.legal.representative'
    _description = 'Legal Representative'
    name = fields.Char(string='Name', required=True)
    company_branch = fields.Many2one('res.company', string='Company – Branch', required=True)
    street = fields.Char(string='Address')
    zip_code = fields.Char(string='Zip Code')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile Number')
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ], string='Estatus', default='Activo', required=True)
