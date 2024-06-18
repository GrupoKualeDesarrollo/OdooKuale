from odoo import fields, models, api
# Modelo para Registro Patronal (IMSS)
class IMSSRegistration(models.Model):
    _name = 'reclutamiento__kuale.imss.registration'
    _description = 'IMSS registration number'

    name = fields.Char(string='Name', required=True)
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip_code = fields.Char(string='Zip Code')
    job = fields.Char(string='Job')
    risk_class = fields.Char(string='Risk class')
    risk_fraction = fields.Char(string='Risk fraction')
    status = fields.Selection([
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ], string='Estatus', default='Activo', required=True)
