from odoo import models, fields

class multiples_files(models.Model):
    _name = 'multiples_files'
    _description = 'Model to store multiple files'

    name = fields.Char(string='File Name', required=True)
    file = fields.Binary(string='File', required=True)
    partner_id = fields.Many2one('hr.applicant', string='Related Model', ondelete='cascade')
