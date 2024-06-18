import base64
import json
from markupsafe import Markup
from odoo import http, SUPERUSER_ID, _, _lt
from odoo.http import request
from psycopg2 import IntegrityError
from odoo.tools import plaintext2html
from odoo.addons.base.models.ir_qweb_fields import nl2br, nl2br_enclose
from werkzeug.exceptions import BadRequest
from odoo.exceptions import AccessDenied, ValidationError, UserError
from odoo.tools.misc import hmac, consteq


class WebsiteForm(http.Controller):

    @http.route('/website/form3/<string:model_name>', type='http', auth="public", methods=['POST'], website=True,
                csrf=False)
    def website_form(self, model_name, **kwargs):
        csrf_token = request.params.pop('csrf_token', None)
        if request.session.uid and not request.validate_csrf(csrf_token):
            raise BadRequest('Session expired (invalid CSRF token)')
        try:
            with request.env.cr.savepoint():
                if request.env['ir.http']._verify_request_recaptcha_token('website_form'):
                    # request.params was modified, update kwargs to reflect the changes
                    kwargs = dict(request.params)
                    kwargs.pop('model_name')
                    return self._handle_website_form(model_name, **kwargs)
            error = _("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({
            'error': error,
        })

    def _handle_website_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search(
            [('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })
        requisition_ids = kwargs.get('requisition_id', '').split(',')
        for req_id in requisition_ids:
            req_id = req_id.strip()
            try:
                # Por cada application.id antes de insertar
                applicant_id = 0
                if not req_id:
                    applicant_id = kwargs.get('status_stage_id')
                # data = self.extract_data(model_record, kwargs)
                data = self.extract_data(model_record, kwargs, req_id, applicant_id)
            # If we encounter an issue while extracting data
            except ValidationError as e:
                # I couldn't find a cleaner way to pass data to an exception
                return json.dumps({'error_fields': e.args[0]})

            try:
                id_record = self.insert_record(request, model_record, data['record'], data['custom'], req_id,
                                               applicant_id, data['experiences'],data.get('meta'))
                if id_record:
                    self.insert_attachment(model_record, id_record, data['attachments'])
                    # in case of an email, we want to send it immediately instead of waiting
                    # for the email queue to process

                    if model_name == 'mail.mail':
                        form_has_email_cc = {'email_cc', 'email_bcc'} & kwargs.keys() or \
                                            'email_cc' in kwargs["website_form_signature"]
                        # remove the email_cc information from the signature
                        kwargs["website_form_signature"] = kwargs["website_form_signature"].split(':')[0]
                        if kwargs.get("email_to"):
                            value = kwargs['email_to'] + (':email_cc' if form_has_email_cc else '')
                            hash_value = hmac(model_record.env, 'website_form_signature', value)
                            if not consteq(kwargs["website_form_signature"], hash_value):
                                raise AccessDenied('invalid website_form_signature')
                        request.env[model_name].sudo().browse(id_record).send()
                        # Some fields have additional SQL constraints that we can't check generically
                        # Ex: crm.lead.probability which is a float between 0 and 1
                        # TODO: How to get the name of the erroneous field ?
            except IntegrityError:
                return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record
        return json.dumps({'id': id_record})

    def extract_data(self, model, values, requisition_id, applicant_id):
        dest_model = request.env[model.sudo().model]
        data = {
            'record': {},  # Values to create record
            'attachments': [],  # Attached files
            'custom': '',  # Custom fields values
            'meta': '',  # Add metadata if enabled
            'experiences': []
        }
        try:
            authorized_fields = model.with_user(SUPERUSER_ID)._get_form_writable_fields()
            error_fields = []
            custom_fields = []
        except Exception as e:
            print("Error occurred:", e)
        bank_comp = False
        account1 = {}
        account2 = {}
        data_card1 = ["account_number", "interbank_clabe", "bank", "payroll_card_number"]
        data_card2 = ["account_number2", "interbank_clabe2", "bank2", "payroll_card_number2"]
        data_beneficiary_prefixes = ["beneficiary_name", "beneficiary_relationship", "other_relationship",
                                     "beneficiary_percentage"]
        beneficiaries = {}
        data_experience_prefixes = ["companyE", "cityE", "periodE","positionE", "salaryE", "supervisorE", "referenceE", "reasonE"]
        experiences = {}
        print("values",values.items())
        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                field_name = field_name.split('[', 1)[0]
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                    field_value.stream.seek(0)  # do not consume value forever
                    if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                        data['record'][field_name + "_filename"] = field_value.filename
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                    job = request.env.context.get('job')
                    if job:
                        job_id = job.id
                        data['record']['job_id'] = job_id

                except ValueError:
                    error_fields.append(field_name)

                if dest_model._name == 'mail.mail' and field_name == 'email_from':
                    custom_fields.append((_('email'), field_value))

            # If it's a custom field
            elif field_name not in ('context', 'website_form_signature'):
                try:
                    if field_name == 'requisition_id' and requisition_id:
                        data['record']['requisition_id'] = requisition_id
                    elif field_name != 'status_stage_id':
                        if field_name == 'clothing_size' and applicant_id != 0:
                            try:
                                product_ids = field_value.split(',')
                                product_list = []
                                applicant = request.env['hr.applicant'].sudo().search([('id', '=', applicant_id)], limit=1)
                                for product_id in product_ids:
                                    product = product_id.split(':')
                                    new_product = request.env['hr.applicant.product'].with_user(SUPERUSER_ID).with_context(
                                        mail_create_nosubscribe=True,
                                    ).create({
                                        'applicant_id': applicant_id,
                                        'product_id': int(product[1]),
                                        'quantity': 1,
                                        'product_template_id': int(product[0]),
                                        'job_id': applicant.job_id.id
                                    })
                                    product_list.append(new_product.id)
                                data['record']['clothing_size'] = [(6, 0, product_list)]
                            except Exception as e:
                                print("Error occurred en clothing:", e)
                        elif field_name in data_card1 and field_value:
                            bank_comp = True
                            account1[field_name] = field_value
                        elif field_name in data_card2 and field_value:
                            account2[field_name[:-1]] = field_value
                        else:
                            prefix = field_name[:-1]
                            index = field_name[-1]
                            if prefix in data_beneficiary_prefixes:
                                if index not in beneficiaries:
                                    beneficiaries[index] = {}
                                if field_value:
                                    beneficiaries[index][prefix] = field_value
                            elif prefix in data_experience_prefixes:
                                if index not in experiences:
                                    experiences[index] = {}
                                if field_value:
                                    experiences[index][prefix] = field_value
                            else:
                                data['record'][field_name] = field_value
                except Exception as e:
                    print("Error occurred en ciclo for:", e)

        if (bank_comp):
            bank_list = []
            account1['applicant_id'] = applicant_id
            account1_create = request.env['bank.account'].with_user(SUPERUSER_ID).with_context(
                mail_create_nosubscribe=True,
            ).create(account1)
            bank_list.append(account1_create.id)
            if account2:
                account2['applicant_id'] = applicant_id
                account2_create = request.env['bank.account'].with_user(SUPERUSER_ID).with_context(
                    mail_create_nosubscribe=True,
                ).create(account2)
                bank_list.append(account2_create.id)
            data['record']['bank_account_ids'] = [(6, 0, bank_list)]
            array_beneficiaries = [beneficiary for key, beneficiary in sorted(beneficiaries.items())]
            data_list = []
            for beneficiary in array_beneficiaries:
                beneficiary['applicant_id'] = applicant_id
                data_create = request.env['hr.applicant.beneficiary'].with_user(SUPERUSER_ID).with_context(
                        mail_create_nosubscribe=True,
                ).create(beneficiary)
                data_list.append(data_create.id)
                data['record']['beneficiaries_ids'] = [(6, 0, data_list)]
        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])
        if requisition_id:
            print("expreinciaprevia",experiences)
            data['experiences']=experiences
            print("data['experiences']", data['experiences'])
            # Buscar  búsqueda mediante la CURP con ex – empleados “Archivados” que hayan trabajado en alguna de las empresas – sucursales.
            exEmpleado = data['record']['previous_experience']
            # Obtener la CURP
            curp = data['record']['curp']
            job_id = data['record']['job_id']
            if exEmpleado:
                print('exEmpleado')
                # Importar el modelo hr.employee
                employee = request.env['hr.applicant']
                try:
                    # Filtrar los registros de empleados archivados que coinciden con la CURP
                    archived_employees = employee.search(
                        [('application_status', '=', 'archived'), ('curp', '=', curp), ('job_id', '=', job_id)])
                    print('archived_employees', archived_employees)
                    # si se encuentra, activar bandera REHIRED,enviar NOTIFICACION, y mapear datos de recontratacion
                    if archived_employees:
                        print('Empleado archivado: ', job_id)
                        data['record']['rehired'] = True
                except Exception as e:
                    print("Error archived_employees :", e)
            try:
                applicant = request.env['hr.applicant']
                users_applicant = applicant.search([('curp', '=', curp), ('job_id', '=', job_id)])
                if users_applicant:
                    print('Ya existe aplicante con la misma CURP ')
                    # enviar NOTIFICACION
            except Exception as e:
                print("Error users_applicant :", e)
        # Add metadata if enabled  # ICP for retrocompatibility
        if request.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ = request.httprequest.headers.environ
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP", environ.get("REMOTE_ADDR"),
                "USER_AGENT", environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER", environ.get("HTTP_REFERER")
            )

        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items() if
                                   field['required'] and label not in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)

        return data

    def insert_record(self, request, model, values, custom, req_id, applicant_id, experiences, meta=None):
        model_name = model.sudo().model
        if model_name == 'mail.mail':
            email_from = _('"%s form submission" <%s>') % (request.env.company.name, request.env.company.email)
            values.update({'reply_to': values.get('email_from'), 'email_from': email_from})

        try:
            if req_id:
                record = request.env[model_name].with_user(SUPERUSER_ID).with_context(
                    mail_create_nosubscribe=True,
                ).create(values)
                #Experiencia previa
                if experiences:
                    array_experiences = [experiences for key, experiences in sorted(experiences.items())]
                    data_listE = []
                    for experience in array_experiences:
                        experience['applicant_id'] = record.id
                        dataE_create = request.env['hr.applicant.experience'].with_user(SUPERUSER_ID).with_context(
                            mail_create_nosubscribe=True,
                        ).create(experience)
                        data_listE.append(dataE_create.id)
                    record.write({'experiencies_ids': [(6, 0, data_listE)]})
                company_name = values.get('company_name')
                company = request.env['res.company'].search([('name', '=', company_name)])
                #self.send_job_notification(jobid)
                #Following applicant
                employees = request.env['hr.employee'].search([('company_id', '=', company.id),('rol_employee', '=', 'LGP')])
                print("employees para following", employees)
                for user in employees:
                    print("manager", user)
                    manager_id=user.id
                    if manager_id:
                        record.message_subscribe([manager_id])
                    else:
                        print("No user found")

            else:
                applicant_id = int(applicant_id)
                record = request.env[model_name].browse(applicant_id)
                record.write(values)
        except Exception as e:
            print("Error :", e)
        if custom or meta:
            _custom_label = "%s\n___________\n\n" % _("Other Information:")  # Title for custom fields
            if model_name == 'mail.mail':
                _custom_label = "%s\n___________\n\n" % _("This message has been posted on your website!")
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
            custom_content = (default_field_data + "\n\n" if default_field_data else '') \
                             + (_custom_label + custom + "\n\n" if custom else '') \
                             + (self._meta_label + "\n________\n\n" + meta if meta else '')

            if default_field.name:
                if default_field.ttype == 'html' or model_name == 'mail.mail':
                    custom_content = nl2br_enclose(custom_content)
                record.update({default_field.name: custom_content})
            elif hasattr(record, '_message_log'):
                record._message_log(
                    body=nl2br_enclose(custom_content, 'p'),
                    message_type='comment',
                )

        return record.id

    def insert_attachment(self, model, id_record, files):
        orphan_attachment_ids = []
        model_name = model.sudo().model
        record = model.env[model_name].browse(id_record)
        authorized_fields = model.with_user(SUPERUSER_ID)._get_form_writable_fields()
        for file in files:
            custom_field = file.field_name not in authorized_fields
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                'res_model': model_name,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            if attachment_id and not custom_field:
                record_sudo = record.sudo()
                value = [(4, attachment_id.id)]
                if record_sudo._fields[file.field_name].type == 'many2one':
                    value = attachment_id.id
                record_sudo[file.field_name] = value
            else:
                orphan_attachment_ids.append(attachment_id.id)

        if model_name != 'mail.mail' and hasattr(record, '_message_log') and orphan_attachment_ids:
            # If some attachments didn't match a field on the model,
            # we create a mail.message to link them to the record
            record._message_log(
                attachment_ids=[(6, 0, orphan_attachment_ids)],
                body=Markup(_('<p>Attached files: </p>')),
                message_type='comment',
            )
        elif model_name == 'mail.mail' and orphan_attachment_ids:
            # If the model is mail.mail then we have no other choice but to
            # attach the custom binary field files on the attachment_ids field.
            for attachment_id_id in orphan_attachment_ids:
                record.attachment_ids = [(4, attachment_id_id)]

    # Dict of dynamically called filters following type of field to be fault tolerent
    _meta_label = _lt("Metadata")  # Title for meta data

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def floating(self, field_label, field_input):
        return float(field_input)

    def html(self, field_label, field_input):
        return plaintext2html(field_input)

    def boolean(self, field_label, field_input):
        return bool(field_input)

    def binary(self, field_label, field_input):
        return base64.b64encode(field_input.read())

    def one2many(self, field_label, field_input):
        return [int(i) for i in field_input.split(',')]

    def many2many(self, field_label, field_input, *args):
        return [(args[0] if args else (6, 0)) + (self.one2many(field_label, field_input),)]

    _input_filters = {
        'char': identity,
        'text': identity,
        'html': html,
        'date': identity,
        'datetime': identity,
        'many2one': integer,
        'one2many': one2many,
        'many2many': many2many,
        'selection': identity,
        'boolean': boolean,
        'integer': integer,
        'float': floating,
        'binary': binary,
        'monetary': floating,
    }

    def send_job_notification(self, job_id):
        employees = request.env['hr.employee.public'].search([('job_id', '=', job_id)])
        print('employees: ', employees)
        for user in employees:
            print('employee: ', user)
            email_values = [user.work_email]
            print('email a enviar: ', email_values)
            body = "Solicitud de trabajo recibida"
            try:
                mail = request.env['mail.mail'].sudo().create({
                    'email_from': 'santiagovco80@gmail.com',
                    'body_html': body,
                    'subject': _('Job applicant!'),
                    'email_to': ','.join(email_values),
                    'auto_delete': True,
                })
                mail.send()
                print('mail creado y enviado:', email_values)
                user = request.env['res.users'].sudo().browse(user.id)
                request.env['mail.message'].create({
                    'model': 'res.users',
                    'res_id': user.id,
                    'subject': 'NOTI',
                    'body': body,
                    'message_type': 'notification',
                })
            except Exception as e:
                print("Error al enviar:", e)
