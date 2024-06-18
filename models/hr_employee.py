from datetime import date

from odoo import models, fields, api, exceptions
from dateutil.relativedelta import relativedelta
class Rol_Employee(models.Model):
    _name = 'hr.employee.rol'
    _description = 'Employee rol'

    name=fields.Char("Rol")
    description=fields.Char("Descripcion")
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    rol_employee = fields.Many2one('hr.employee.rol', string='Rol')
    credentials = fields.One2many('reclutamiento__kuale.credential', 'employee_id', string="Credenciales", required=True)

