from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime,timedelta


class weekly_schedule(models.Model):
    _name = 'weekly_schedule'
    _description = 'weekly_schedule'

    name = fields.Char(string='Nombre', required=True)
    day_of_week = fields.Selection([
        ('monday', 'Lunes'),
        ('tuesday', 'Martes'),
        ('wednesday', 'Miércoles'),
        ('thursday', 'Jueves'),
        ('friday', 'Viernes'),
        ('saturday', 'Sábado'),
        ('sunday', 'Domingo')
    ], string='Día de la semana')
    rest_day = fields.Boolean(string='Descanso')
    start_time = fields.Char(string='Hora de inicio', required=True)
    end_time = fields.Char(string='Hora fin', required=True)
    break_time = fields.Integer(string='Tiempo descanso', required=True)
    break_start_time = fields.Char(string='Inicio descanso', required=True)
    break_end_time = fields.Char(string='Fin descanso', required=True, compute="_compute_break_end_time")

    @api.constrains('start_time', 'end_time', 'break_start_time', 'break_end_time')
    def _check_time_values(self):
        for record in self:
            print('record  weekly',record)
            if record.start_time:
                self._validate_time(record.start_time)
            if record.end_time:
                self._validate_time(record.end_time)
            if record.break_start_time:
                self._validate_time(record.break_start_time)
            if record.break_end_time:
                self._validate_time(record.break_end_time)

    def _validate_time(self, time_str):
        try:
            hour, minute = map(int, time_str.split(':'))
            if hour < 1 or hour > 23 or minute < 0 or minute > 59:
                raise ValidationError("Formato invalido.La hora debe estar entre 01:00 y 23:59.")
        except ValueError:
            raise ValidationError("Formato invalido. La hora debe estar en el formato HH:MM.")

    @api.depends('break_end_time')
    def _compute_break_end_time(self):
        for record in self:
            print('_compute_break_end_time',record)
            if record.break_start_time and record.break_time:
                print("data: ", record.break_start_time, " - ", record.break_time)
                record.break_end_time = record.break_start_time + str(record.break_time)


class hr_applicant_doc(models.Model):
    _name = 'hr_applicant_doc'
    _description = 'Documentation schedule'
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    datetimeSession = fields.Datetime(string='Fecha y Hora', required=True)
    place = fields.Many2one(
        'res.company',
        string='Lugar', required=True
    )
    contactSession = fields.Many2one(
        'hr.employee',
        string='Contacto sesión contratación', required=True
    )
    workDate = fields.Date(string='Fecha laboral')
    weekly_schedule = fields.Many2many(
        'weekly_schedule',
        string='Horario semanal', required=True
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super(hr_applicant_doc, self).default_get(fields_list)
        applicant_id = self._context.get('default_applicant_id')
        print("obtener applicant default:",applicant_id)
        defaults['applicant_id'] = int(applicant_id)
        return defaults

    @api.model
    def create(self, vals):
        record = super(hr_applicant_doc, self).create(vals)
        #agendar en calendario
        try:
            fecha_start_str=vals.get('datetimeSession')
            fecha_start = datetime.strptime(fecha_start_str, '%Y-%m-%d %H:%M:%S')
            contacto=vals.get('contactSession')
            fecha_stop = fecha_start + timedelta(hours=1)
            calendar_value = {
                'name': 'Recibir candidato a contratación',
                'start': fecha_start,
                'stop': fecha_stop,
                'partner_ids': [(4, contacto)]
            }
            calendar_id = self.env['calendar.event'].sudo().create(calendar_value)
        except Exception as e:
            print("Error calendar:", e)
        #enviar correo
        template_id = self.env.ref('reclutamiento__kuale.mail_template_pre_hired').id
        template = self.env['mail.template'].browse(template_id)
        applicant_id = vals.get('applicant_id')
        applicant_record = self.env['hr.applicant'].search([('id', '=', self._context.get('default_applicant_id'))], limit=1)
        email_from = applicant_record.email_from
        if template and email_from:
            try:
                additional_text = " "+applicant_record.company_name
                rendered_body = template.body_html
                full_body = rendered_body + additional_text+" Debera presentarse en Fecha y hora: "+vals.get('datetimeSession')
                emails = template.email_to
                print("emails", emails)
                email_list = emails.split(',')
                print("email_list", email_list)
                email_list.append(email_from)
                print("email_list append", email_list)
                for email in email_list:
                    email = email.strip()
                    print("email to", email)
                    mail_values = {
                        'body_html': full_body,
                        'subject': template.subject,
                        'email_to': email,
                        'auto_delete': True,
                    }
                    template.send_mail(self.id, email_values=mail_values, force_send=True)
                    print('Correo seleccionado enviado.')
            except Exception as e:
                print("Error:", e)
        return record