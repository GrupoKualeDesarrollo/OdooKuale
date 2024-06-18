
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.http import request
import random
import string
from datetime import date,timedelta
class mail_mail(models.Model):
    _name = 'reclutamiento__kuale.mail_mail'
    _description = "reclutamiento__kuale.mail_mail"

    email_from = fields.Text('Email From', help='Email from')
    email_to = fields.Text('Email To')
    email_cc = fields.Text('Cc')
    subject = fields.Text('Subject')
    body_html = fields.Html('Body', default='', sanitize_style=True)
    scheduled_date = fields.Date('Limit date', default=fields.Date.context_today)
    attachments = fields.Binary(string='Attachments')
    sendMail = fields.Boolean(string='Send Mail', default=True)
    templateMail = fields.Many2one(
         'mail.template',
         string='Mail Template'
     )
    @api.depends('email_from')
    def _compute_applicant_url(self):
        for record in self:
            applicant_id = self._context.get('applicant_id')
            if applicant_id:
                # Generar un token aleatorio de 8 caracteres
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                base_url = request.httprequest.host_url
                # Buscar el registro con el applicant_id especificado
                existing_record = self.env['vigency_complement'].sudo().search([('applicant_id', '=', applicant_id)], limit=1)
                if existing_record:
                    # Obtener la fecha de vigency
                    vigency_date = fields.Datetime.from_string(existing_record.vigency)
                    current_date = fields.Datetime.from_string(fields.Datetime.now())
                    #print("vigency_date: ", vigency_date,"-current_date: ",current_date)
                    # Comparar si han pasado más de 7 días
                    if current_date > vigency_date + timedelta(days=7):
                        print("Actualizar registro new token")
                        existing_record.sudo().write({
                            'token': token,
                            'vigency': fields.Datetime.now(),
                        })
                    else:
                        print("Vigency is still valid.",existing_record.token)
                        record.applicant_url = f"{base_url}/jobs/formRecruitment/{applicant_id}/{existing_record.token}"
                else:
                    print("Crear registro new token")
                    record.applicant_url = f"{base_url}/jobs/formRecruitment/{applicant_id}/{token}"
                    try:
                        self.env['vigency_complement'].sudo().create({
                            'applicant_id': applicant_id,
                            'token': token,
                            'vigency':  fields.Datetime.now(),
                        })
                    except Exception as e:
                        print("Error al crear el registro en vigency_complement:", e)

    applicant_url = fields.Char('Complement Form URL: ', compute='_compute_applicant_url')

    @api.model
    def default_get(self, fields_list):
        defaults = super(mail_mail, self).default_get(fields_list)
        applicant_id = self._context.get('applicant_id')
        applicant_record = self.env['hr.applicant'].search([('id', '=', applicant_id)], limit=1)
        if applicant_record:
            defaults['email_from'] = applicant_record.email_from
        return defaults

    def sendEmail(self):
        print("enviando...")
        template = self.templateMail
        email_from = self.email_from
        if template and email_from:
            print("template ",template)
            try:
                additional_text = "Complement Form URL: "+self.applicant_url
                rendered_body = template.body_html
                full_body = additional_text + rendered_body
                mail_values = {
                    'body_html': full_body,
                    'subject': template.subject,
                    'email_to': email_from,
                    'auto_delete': True,
                }
                template.send_mail(self.id, email_values=mail_values, force_send=True)
                #template.send_mail(self.id, email_values={'email_to': email_from},force_send=True)
                print('Correo electrónico enviado correctamente.')
            except Exception as e:
                print("Error:", e)
        else:
            print(
                'Falta el template o la dirección de correo electrónico.')
    def sendEmailSelected(self):
        print("seleccionado")
        template = self.templateMail
        email_from = self.email_from
        #Cambiar status una vez enviado correo
        applicant_id = self._context.get('applicant_id')
        applicant = self.env['hr.applicant'].search([('id', '=', applicant_id)])
        applicant.write({'stage_id': 6})
        if template and email_from:
            print("template ", template)
            try:
                template.send_mail(self.id, email_values={'email_to': email_from},force_send=True)
                print('Correo electrónico enviado.')
            except Exception as e:
                print("Error:", e)

    def cancelEmail(self):
        print('cancel')