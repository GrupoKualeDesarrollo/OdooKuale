from odoo import models, fields

class JobApplicationAttachment(models.Model):
    _name = 'job.application.attachment'

    name = fields.Char(string='Name')
    file = fields.Binary(string='File')
    filename = fields.Char(string='Filename')
    application_id = fields.Many2one('job.application', string='Application')