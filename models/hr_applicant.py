from datetime import date

from odoo import models, fields, api, exceptions
from dateutil.relativedelta import relativedelta

# Define la lista de selección una sola vez
RELATIONSHIP_SELECTION = [
    ('mother', 'Madre'),
    ('father', 'Padre'),
    ('sibling', 'Hermano(a)'),
    ('child', 'Hijo(a)'),
    ('spouse', 'Conyuge'),
    ('other', 'Otro'),
]
ONE_SELECTION = [
    ('yes', 'Si'),
    ('no', 'No')
]
PROGRESS_SELECTION = [
    ('viable', 'Viable'),
    ('no_viable', 'No viable'),
    ('new', 'Nuevo'),
    ('progress', 'En progreso')
]
class hr_applicant(models.Model):
    _inherit = 'hr.applicant'

    # Puesto
    position_name = fields.Char(string='Puesto', readonly=True)
    # Empresa
    company_name = fields.Char(string='Empresa', readonly=True)
    # Sucursal
    branch = fields.Char(string='Sucursal', readonly=True)
    # Requisition - sutituir por el Branch
    requisition_id = fields.Many2one("reclutamiento__kuale.requisitions", string="Sucursal")
    # ¿Cómo te enteraste de la vacante?
    about_vacancy = fields.Selection([
        ('friendship', 'Amistad'),
        ('networking', 'Redes'),
        ('initiative', 'Iniciativa propia'),
        ('other', 'Otro'),
    ], string='¿Cómo te enteraste de la vacante?', required=True)
    # Otra razon-especificar
    other_reason = fields.Char(string='Otro (especifique)')
    # CURP
    curp = fields.Char(string='CURP', required=True, store=True)
    # ¿Has laborado anteriormente con nosotros?
    previous_experience = fields.Selection(ONE_SELECTION, string='Ha laborado con nosotros')
    # full_name = fields.Char(string='Fullname')
    # Apellido paterno
    last_name = fields.Char(string='Apellido paterno', required=True)
    # Apellido materno
    last_name2 = fields.Char(string='Apellido materno', required=True)
    # Teléfono celular 2
    phone_number = fields.Char(string='Teléfono celular 2', size=10, required=True)
    job_tab_id = fields.Many2one(
        related='job_id.job_tab_ids',
        string="Tabulador",
        readonly=True,
        store=True
    )
    # Fecha de Nacimiento
    birthdate = fields.Date(string='Fecha de Nacimiento', default=fields.Date.context_today, required=True)
    # Lugar de nacimiento
    birthplace = fields.Char(string='Lugar de nacimiento')
    # Entidad federativa de nacimiento
    state_birth = fields.Char(string='Entidad federativa de nacimiento')
    # Edad
    age = fields.Integer(string='Edad', readonly=True, compute='_compute_age')
    # Genero
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ], string='Genero', readonly=True)
    # Escolaridad
    scholarship = fields.Selection([
        ('none', 'Ninguno'),
        ('primary', 'Primaria'),
        ('secondary', 'Secundaria'),
        ('high_school', 'Preparatoria'),
        ('career', 'Carrera'),
        ('other', 'Otro')
    ], string='Escolaridad', default='none', required=True)
    other_scholarship = fields.Char(string='Otro')
    # ¿Estudia actualmente?
    is_studying = fields.Selection(ONE_SELECTION, string='Estudia actualmente', default='no', required=True)
    # Horario, depends='is_studying'
    current_schedule = fields.Char(string='Horario',
                                   required=False)
    # Carrera , depends='is_studying'
    current_degree = fields.Char(string='Carrera',
                                 required=False)
    # INE
    has_ine = fields.Selection(ONE_SELECTION, string='¿Cuentas con INE vigente?', required=True)
    # ,required=lambda self: (self.has_ine == 'yes')[1] if self.has_ine else False
    ine_document = fields.Binary(string='Adjuntar archivo INE')
    # Domicilio Actual
    current_address = fields.Char(string='Domicilio actual', required=True)
    exterior_number = fields.Integer(string='No. Exterior', required=True)
    interior_number = fields.Integer(string='No. Interior', required=False)
    colony = fields.Char(string='Colonia', required=True)
    municipality = fields.Char(string='Municipio', required=True)
    state = fields.Char(string='Estado', required=True)
    full_address = fields.Char(string='Domicilio actual', required=True, compute='_compute_address')
    # Codigo postal
    postal_code = fields.Char(string='Codigo postal', size=5, help='Only 5 digits allowed.', required=True)
    # NSS
    has_social_security = fields.Selection(ONE_SELECTION, string='Cuenta con Número de Seguridad Social', required=True)
    # required=lambda self: (self.has_social_security == 'yes')[1] if self.has_social_security else False
    social_security_number = fields.Char(string='Número de Seguridad Social')
    nss_files = fields.One2many('multiples_files', 'partner_id', string='NSS Files')
    # RFC
    has_rfc = fields.Selection(ONE_SELECTION, string='Tiene RFC', required=True)
    # required=lambda self: (self.has_rfc == 'yes')[1] if self.has_rfc else False
    rfc_number = fields.Char(string='RFC', size=13, default="")
    rfc_files = fields.One2many('multiples_files', 'partner_id', string='RFC Files')
    # Licencia de manejo
    has_driver_license = fields.Selection(ONE_SELECTION, string='Tiene licencia de manejo', required=True)
    driver_license_number = fields.Char(string=' Licencia de manejo')
    driver_license_validity = fields.Date(string='Vigencia de licencia de manejo', default=fields.Date.context_today)
    driver_files = fields.One2many('multiples_files', 'partner_id', string='Adjuntar archivo Licencia de Manejo')
    # Experiencia laboral
    has_experience = fields.Selection(ONE_SELECTION, string='Experiencia laboral actual/anterior', default='no')
    experiencies_ids = fields.One2many('hr.applicant.experience', 'applicant_id', string="Experiencia laboral")
    # Adjuntar complementos según perfil
    is_minor = fields.Boolean(string='', default=False)
    # en caso de ser menor adjuntar ine tutor legal
    attachments = fields.One2many('job.application.attachment', 'application_id', string='Attachments')
    # , required=lambda self: self.is_minor
    ineTutor_document = fields.Binary(string='INE Document')
    # Terminos y condiciones
    terms_conditions = fields.Boolean(string='', default=False, required=True)
    # ADICIONALES
    marital_status = fields.Selection([
        ('single', 'Soltero'),
        ('married', 'Casado'),
        ('common', 'Unión libre')
    ], string='Estado Civil')
    nationality = fields.Selection([
        ('mexican', 'Mexicana'),
        ('other', 'Otra')
    ], string='Nacionalidad')
    other_nationality = fields.Char(string='Nacionalidad')
    desk_phone = fields.Char(string='Teléfono Fijo')
    fiscal_address = fields.Char(string='Domicilio Fiscal')
    full_fiscal_address = fields.Char(string='Domicilio Fiscal', required=True, compute='_compute_fiscal_address')
    exterior_number_fiscal = fields.Integer(string='No. Exterior', required=True)
    interior_number_fiscal = fields.Integer(string='No. Interior', required=False)
    colony_fiscal = fields.Char(string='Colonia', required=True)
    municipality_fiscal = fields.Char(string='Municipio', required=True)
    state_fiscal = fields.Char(string='Estado', required=True)
    postal_code_fiscal = fields.Char(string='Código Postal', size=5, help='Only 5 digits allowed.', required=True)
    between_streets = fields.Text(string='Entre Calles')
    additional_ref = fields.Char(string='Referencias adicionales')
    address_details = fields.Text(string='Características del domicilio')
    clothing_size = fields.One2many('hr.applicant.product', 'applicant_id', string="Talla Uniforme")
    bank_account_ids = fields.One2many('bank.account', 'applicant_id', string="Cuentas")
    beneficiaries_ids = fields.One2many('hr.applicant.beneficiary', 'applicant_id', string="Beneficiarios")
    know_clinic = fields.Selection(ONE_SELECTION, string='Do you know which IMSS clinic corresponds to you?')
    imss_clinic = fields.Many2one(
        'reclutamiento__kuale.clinic',
        string='Clinica'
    )
    medical_unity = fields.Char(string='Unidad Medica Familiar')
    blood_type = fields.Selection([
        ('a_p', 'A+'),
        ('a_n', 'A-'),
        ('b_p', 'B+'),
        ('b_n', 'B-'),
        ('ab_p', 'AB+'),
        ('ab_n', 'AB-'),
        ('o_p', 'O+'),
        ('o_n', 'O-')
    ], string='Tipo de sangre')
    has_allergy = fields.Selection(ONE_SELECTION, string='¿Eres alérgico a algún medicamento/alimento?', required=True,
                                   default='no')
    allergy = fields.Char(string='¿Cuál alergia padece?')
    has_medical_tx = fields.Selection(ONE_SELECTION, string='¿Recibe algún tratamiento médico?', required=True,
                                      default='no')
    medical_tx = fields.Char(string='¿Qué tratamiento recibe?')
    emergency_contacts = fields.One2many('hr.applicant.emergency', 'applicant_id', string="Contactos de emergencia")

    # REINGRESO
    rehired = fields.Boolean(string='Recontratar', default=False)
    re_company = fields.Char(string='Empresa')
    re_branch = fields.Char(string='Sucursal')
    re_boss = fields.Char(string='Jefe inmediato')
    re_date = fields.Date(string='Fecha renuncia')
    re_lastDay = fields.Date(string='Último día laborado')
    termination_Date = fields.Date(string='Fecha finiquito')
    re_reason = fields.Char(string='Motivo de baja')
    re_comments = fields.Text(string='Comentarios')
    status_stage_id = fields.Integer(string='Status', compute='_compute_stage_id')
    #
    process = fields.Selection(PROGRESS_SELECTION, default='progress',string="Progreso")
    color_process = fields.Integer(compute='_compute_color')

    @api.depends('process')
    def _compute_color(self):
        for record in self:
            if record.process == 'new':
                record.color_process = 7 #Grey
            elif record.process == 'viable':
                record.color_process = 10 #Green
            elif record.process == 'no_viable':
                record.color_process = 1 #Red
            else:
                record.color_process = 3 #Yellow

    @api.model
    def default_getName(self, fields_list):
        print("default get name")
        defaults = super(hr_applicant, self).default_getName(fields_list)
        full_name = ", ".join(filter(None, [
            defaults['partner_name'], defaults['last_name'], defaults['last_name2']
        ]))
        print("full_name ", full_name)
        defaults['partner_name'] = full_name
        return defaults


    def update_garments(self):
        if self.job_id:
            job_products = self.job_id.products.mapped('product_template_id')
            applicant_products = self.clothing_size.mapped('product_template_id')
            missing_products = job_products - applicant_products
            product_list = []
            for product_id in missing_products.ids:
                product = self.env['product.product'].search([('product_tmpl_id', '=', product_id)], limit=1)
                product_list.append((0, 0, {
                    'applicant_id': self.id,
                    'quantity': 1,
                    'product_id': product.id,
                    'product_template_id': product_id,
                    'job_id': self.job_id.id
                }))
            self.write({'clothing_size': product_list})


    @api.depends('partner_name', 'last_name', 'last_name2')
    def _compute_name(self):
        for record in self:
            record.partner_name = ", ".join(filter(None, [
                record.partner_name,
                record.last_name,
                record.last_name2
            ]))


    @api.depends('current_address', 'exterior_number', 'interior_number', 'colony', 'municipality', 'state',
                 'postal_code')
    def _compute_address(self):
        for record in self:
            record.full_address = ", ".join(filter(None, [
                record.current_address,
                str(record.exterior_number),
                str(record.interior_number),
                record.colony,
                record.municipality,
                record.state,
                record.postal_code
            ]))


    @api.depends('fiscal_address', 'exterior_number_fiscal', 'interior_number_fiscal', 'colony_fiscal',
                 'municipality_fiscal', 'state_fiscal',
                 'postal_code_fiscal')
    def _compute_fiscal_address(self):
        for record in self:
            record.full_fiscal_address = ", ".join(filter(None, [
                record.fiscal_address,
                str(record.exterior_number_fiscal),
                str(record.interior_number_fiscal),
                record.colony_fiscal,
                record.municipality_fiscal,
                record.state_fiscal,
                record.postal_code_fiscal
            ]))

    @api.onchange('stage_id')
    def _change_stage_id(self):
        for record in self:
            print("cambio a: ",record.stage_id)
    @api.depends('stage_id')
    def _compute_stage_id(self):
        for record in self:
            stage = record.stage_id
            if stage:
                sequence = stage.sequence
                record.status_stage_id = sequence


    # Age automatically
    @api.depends('birthdate')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birthdate:
                birthdate = fields.Date.from_string(record.birthdate)
                age = relativedelta(today, birthdate).years
                record.age = age
                record.is_minor = age < 18  # INDICA SI ES MENOR DE EDAD
            else:
                record.age = 0


    # Get gender
    @api.depends('curp')
    def _compute_gender(self):
        for record in self:
            if record.curp:
                gender_char = record.curp[10].upper()
                if gender_char == 'H':
                    record.gender = 'male'
                elif gender_char == 'M':
                    record.gender = 'female'
                else:
                    record.gender = 'other'
            else:
                record.gender = False


    def rehire_action(self, **kwargs):
        try:
            print('Accion de recontratar')
            applicant_id = self.id
            print('applicant_id ', applicant_id)
            applicant = self.env['hr.applicant'].browse(applicant_id)
            print('applicant ', applicant)
            # Actualizar el campo application_status a 'Hired'
            applicant.write({'application_status': 'hired'})
        except Exception as e:
            print("Error al ercontrar:", e)


    def interview_modal(self):
        print('button abrir modal correo- ', self.id)
        template_id = self.env.ref('reclutamiento__kuale.mail_template_interview').id
        # 'view_id': self.env.ref('reclutamiento__kuale.view_modal_form_mail_mail').id,
        return {
            'name': 'Send Interview',
            'type': 'ir.actions.act_window',
            'res_model': 'mail.template',
            'view_mode': 'form',
            'res_id': template_id,
            'target': 'new',
            'context': {'applicant_id': self.id},
        }


    def send_interview(self):
        print("sending interview...-")
        # cambiar status del applicant a “Primera entrevista”.
        template_id = self.env.ref('reclutamiento__kuale.mail_template_interview').id
        template = self.env['mail.template'].browse(template_id)
        email_from = self.email_from
        if template and email_from:
            try:
                # template = self.env.ref('reclutamiento__kuale.mail_template_interview').with_context(
                #    default_model='mail.template')
                print("email to en default", template.email_to)
                emails = template.email_to
                print("emails", emails)
                email_list = emails.split(',')
                print("email_list", email_list)
                email_list.append(email_from)
                print("email_list append", email_list)
                for email in email_list:
                    template.send_mail(self.id, email_values={'email_to': email}, force_send=True)
                    # template.send_mail(template, email_values=mail_values, force_send=True, model='mail.template')
                    print('Correo inteview enviado.', email)
            except Exception as e:
                print("Error:", e)


    def consult_interview(self):
        print('consultar formulario de reclutamiento')


    def request_complement(self):
        print('abrir complemento')
        return {
            'name': 'Send complement',
            'type': 'ir.actions.act_window',
            'res_model': 'reclutamiento__kuale.mail_mail',
            'view_mode': 'form',
            'view_id': self.env.ref('reclutamiento__kuale.view_modal_form_mail_complement').id,
            'target': 'new',
            'context': {'applicant_id': self.id},
        }


    def request_documentation(self):
        print('abrir documentation:', self.id)
        doc = self.env.ref('reclutamiento__kuale.hr_applicant_view_request_documentation')
        print('documentation:', doc)
        doc_id = doc.id
        print('doc_id:', doc_id)
        return {
            'name': 'Request Documentation',
            'type': 'ir.actions.act_window',
            'res_model': 'hr_applicant_doc',
            'view_mode': 'form',
            'view_id': doc_id,
            'target': 'new',
            'context': {'default_applicant_id': self.id},
        }


    def modal_selected(self):
        print("accion seleeccionar")
        view_id = self.env.ref('reclutamiento__kuale.view_modal_form_mail_selected').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Selected',
            'res_model': 'reclutamiento__kuale.mail_mail',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'applicant_id': self.id}
        }


    def toggle_active(self):
        self.write({'process': 'viable'})
        job = self.env['hr.job'].search([('id', '=', self.job_id.id), ('active', '=', True)], limit=1)
        if job:
            res = super(hr_applicant, self).toggle_active()
            self.write({'stage_id': 2})  # Calificacion inicial
        else:
            msjError = "No es posible restaurar, ya no existe la requisicion para el puesto: " + self.job_id.name
            raise exceptions.ValidationError(msjError)
            # raise exceptions.UserError('Operación no permitida', msjError)
    def set_viable(self):
        self.write({'process': 'viable'})

class HrApplicantProduct(models.Model):
    _name = 'hr.applicant.product'
    _description = 'Applicant Product'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Garments", required=True,
                                 domain="[('product_tmpl_id', '=', product_template_id)]")
    product_template_id = fields.Many2one('product.template', string="Product Template",
                                          domain="[('id', 'in', allowed_product_templates)]")
    quantity = fields.Integer(string="Cantidad")
    job_id = fields.Many2one('hr.job', string="Job")
    allowed_product_templates = fields.Many2many(
        'product.template', string="Allowed Product Templates", compute='_compute_allowed_product_templates'
    )

    @api.depends('applicant_id')
    def _compute_allowed_product_templates(self):
        for record in self:
            job = record.applicant_id.job_id
            jobs = job.products.mapped('product_template_id.id')
            record.allowed_product_templates = [(6, 0, jobs)]


class BeneficiaryApplicant(models.Model):
    _name = 'hr.applicant.beneficiary'
    _description = 'Applicant Beneficiary'
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", required=True)
    beneficiary_name = fields.Char(string='Nombre del beneficiario')
    beneficiary_relationship = fields.Selection(RELATIONSHIP_SELECTION, string='Parentesco del beneficiario')
    other_relationship = fields.Char(string='Otro')
    beneficiary_percentage = fields.Char(string=' Porcentaje del beneficiario')

    @api.model
    def create(self, vals):
        if 'applicant_id' in vals:
            applicant = self.env['hr.applicant'].browse(vals['applicant_id'])
            if len(applicant.beneficiaries_ids) >= 4:
                raise exceptions.ValidationError("Solo 4 beneficiarion permitidos")
        return super(BeneficiaryApplicant, self).create(vals)

    def write(self, vals):
        if 'applicant_id' in vals:
            for record in self:
                applicant = self.env['hr.applicant'].browse(vals['applicant_id'])
                if len(applicant.beneficiaries_ids) >= 4 and vals['applicant_id'] != record.applicant_id.id:
                    raise exceptions.ValidationError("Solo son permitidos 4 beneficiarion")
        return super(BeneficiaryApplicant, self).write(vals)


class BankAccount(models.Model):
    _name = 'bank.account'
    _description = 'Bank Account'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant", required=True)
    account_number = fields.Char(string="No. de Cuenta", required=True)
    interbank_clabe = fields.Char(string="Clabe Interbancaria", required=True)
    payroll_card_number = fields.Char(string="Número de tarjeta de nómina")
    bank = fields.Char(string="Banco", required=True)

    @api.model
    def create(self, vals):
        if 'applicant_id' in vals:
            applicant = self.env['hr.applicant'].browse(vals['applicant_id'])
            if len(applicant.bank_account_ids) >= 2:
                raise exceptions.ValidationError("Solo dos cuentas son permitidas")
        return super(BankAccount, self).create(vals)

    def write(self, vals):
        if 'applicant_id' in vals:
            for record in self:
                applicant = self.env['hr.applicant'].browse(vals['applicant_id'])
                if len(applicant.bank_account_ids) >= 2 and vals['applicant_id'] != record.applicant_id.id:
                    raise exceptions.ValidationError("Solo dos cuentas son permitidas")
        return super(BankAccount, self).write(vals)


class ExperienceApplicant(models.Model):
    _name = 'hr.applicant.experience'
    _description = 'Previous experience'
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", required=True)
    companyE = fields.Char(string='Empresa')
    cityE = fields.Char(string='Ciudad')
    periodE = fields.Integer(string='Periodo')
    positionE = fields.Char(string='Puesto')
    salaryE = fields.Integer(string='Sueldo')
    supervisorE = fields.Char(string='Nombre del jefe directo')
    referenceE = fields.Char(string='No. Contacto para referencias')
    reasonE = fields.Char(string='Motivo de salida')


class EmergencyApplicant(models.Model):
    _name = 'hr.applicant.emergency'
    _description = 'Emergency contacts'
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", required=True)
    name = fields.Char(string='Nombre')
    relationship = fields.Selection(RELATIONSHIP_SELECTION, string='Parentesco')
    phone_number = fields.Char(string='Teléfono')
