from odoo import fields, models, api

# Modelo para Certificado de Timbrado
class DigitalStampCertificate(models.Model):
    _name = 'reclutamiento__kuale.digital.stamp.certificate'
    _description = 'Stamping certificate'

    name = fields.Char(string='Name', required=True)
    imss_registration_id = fields.Many2one('reclutamiento__kuale.imss.registration', string='Registration', required=True)
    certificate_number = fields.Char(string='Certificate Number', required=True)
    password = fields.Char(string='Password', required=True)
    confirmation = fields.Char(string='Confirmation', required=True)
    validity = fields.Date(string='Validity', required=True)
    valid_from = fields.Date(string='From', required=True)
    valid_to = fields.Date(string='To', required=True)
    status = fields.Selection([
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ], string='Estatus', default='Activo', required=True)

