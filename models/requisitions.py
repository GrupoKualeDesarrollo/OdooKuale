import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import models, fields, api


class RequisitionReasons(models.Model):
    _name = 'reclutamiento__kuale.requisition_reasons'
    _description = 'reclutamiento__kuale.requisition_reasons'

    active = fields.Boolean(default=True, readonly=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Reason name already exists!"),
    ]


class Shifts(models.Model):
    _name = 'reclutamiento__kuale.shifts'
    _description = 'reclutamiento__kuale.shifts'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Shift name already exists!"),
    ]


class RequisitionDetails(models.Model):
    _name = "reclutamiento__kuale.requisitions_details"
    _description = "Requisitions Details"
    _order = "id"

    requisition_id = fields.Many2one("reclutamiento__kuale.requisitions", string="Requisitions")
    active = fields.Boolean('Active', default=True)
    quantity = fields.Integer('Quantity', required=True, default=1)
    quantity_auth = fields.Integer('Vacancies approved', default=0)
    shift = fields.Many2one('reclutamiento__kuale.shifts', string="Shift", required=True)
    reason = fields.Many2one('reclutamiento__kuale.requisition_reasons', string="Reason", required=True)
    student = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ])
    description = fields.Char("Specify")

    @api.constrains('quantity')
    def _check_campo_entero(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("The value of the number of vacancies must be greater than zero.")


class Requisitions(models.Model):
    _name = "reclutamiento__kuale.requisitions"
    _description = "Requisitions"
    _order = "id"
    _inherit = ['mail.thread']
    # _parent_store = True

    active = fields.Boolean('Active', default=True)
    sequence = fields.Char('Sequence', default=lambda self: _('New'), copy=False, readonly=True, tracking=True)
    color = fields.Integer('Color Index', default=0)

    name = fields.Char('Folio', readonly=True, store=True)
    status_requisition = fields.Char('Status', readonly=True, default="New")
    status = fields.Integer('Status', default=10)
    # 10= Nuevo,  20 = Pendiente, 30=Autorizado, 40= Publicado, 50=Completado, 60= Rechazado, 70= Cancelado
    last_status = fields.Integer('Last Status')

    # job_id = fields.Integer('Vacancy to apply for')
    job_id = fields.Many2one('hr.job', 'Job Position', check_company=True, domain="[('is_Parent_Job', '=', True)]",
                             required=True)

    no_requisitions = fields.Integer('Quantity Request', compute="_compute_quantity_requisitions", store=True)
    # no_requisitions = fields.Integer('Quantity Request', store=True)
    date_entry = fields.Date('Date Entry', required=True)
    date_end = fields.Date('Deadline')
    inmediate_job_id = fields.Many2one('res.users', 'Manager', store=True, readonly=False, required=True)
    # inmediate_job_id = fields.Many2one('res.users', 'Inmediate Job', related='resource_id.user_id', store=True,
    #                                  readonly=False)

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company,
                                 required=True)
    # subsidiary_id = fields.Many2one('res.company', string='Subsidiary', index=True)
    branch_ids = fields.Many2one('res.company', compute='_compute_branch_id',
                                 domain="[('parent_id', '=', company_id)]", store=True,
                                 readonly=False,
                                 required=True,
                                 ondelete='cascade')

    department_id = fields.Many2one('hr.department', "Department", check_company=True, required=True)
    # department_id = fields.Many2one('hr.department', "Department", compute='_compute_department_id', store=True,
    # compute_sudo=True)

    total_employee_current = fields.Integer(compute='_compute_total_employee', string='Current Employees', store=True)
    total_employee_absents = fields.Integer(compute='_compute_total_employee_absent', string='Absent employees',
                                            store=True)

    # no_employees = fields.Integer('Current Employees')
    # no_employees_absents = fields.Integer('Absent employees')
    # reason_id = fields.Integer('Reason/Cause/Justifying Vacancy')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('indistinct', 'Indistinct')
    ])

    # age_id = fields.Integer('Age Range')
    age_id = fields.Many2one('reclutamiento__kuale.age', string='Age Range')
    is_age_other = fields.Boolean("Is Other Age", compute='_compute_age_id')
    age_other = fields.Char('Age Range (Other)', translate=True)

    workday_calendar_id = fields.Many2one('resource.calendar', string="Availability of schedule", check_company=True)

    # workday_id = fields.Integer('Availability of schedule')
    no_requisitions_auth = fields.Integer('Vacancies approved', compute="_compute_quantity_requisitions", store=True)

    details = fields.One2many('reclutamiento__kuale.requisitions_details', 'requisition_id', string="Details",
                              required=True)
    reason_vacancy = fields.Many2one('reclutamiento__kuale.requisition_reasons',
                                     string="Reason/Cause/Justification of vacancy")
    # referencia a postulaciones
    applicant_ids = fields.One2many('hr.applicant', 'requisition_id', string="Applicants")
    application_count = fields.Integer(compute='_compute_application_count', string="Application Count")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Folio already exists!"),
    ]
    """"@api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('reclutamiento__kuale.requisitions')
                # vals['name'] = vals.get('folio') + "-" + vals.get('sequence')
            vals['status_requisition'] = "Pendiente"
        return super().create(vals_list)"""

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Cambia el estatus de nuevo a Pendiente
            vals['last_status'] = 10
            vals['status'] = 20
            vals['status_requisition'] = "Pendiente"
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('reclutamiento__kuale.requisitions')
            company = self.env['res.company'].browse(vals.get('company_id')) or self.env.company
            branch = self.env['res.company'].browse(vals.get('branch_ids')) or self.env.company
            department = self.env['hr.department'].browse(vals.get('department_id')) or self.env.company
            current_year = str(datetime.datetime.now().year)
            folio_seq = company.name[:2] + "-" + branch.name[:3] + "-" + current_year + "-" + department.acronym[:3] + "-" + vals['sequence']
            vals['name'] = folio_seq
        return super().create(vals_list)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if not default.get('name'):
            default['sequence'] = self.env['ir.sequence'].next_by_code('reclutamiento__kuale.requisitions')
            nameSeq = self.name.rfind("-")
            default['name'] = self.name[:nameSeq + 1] + default['sequence']
        return super(Requisitions, self).copy(default)

    @api.depends('company_id', 'branch_ids', 'department_id', 'sequence')
    def _compute_folio(self):
        for record in self:
            if not record.company_id and not record.branch_ids and not record.department_id:
                record.name = False
            else:
                nameCompany = record.company_id.name
                nameBranch = record.branch_ids.name
                if not record.department_id:
                    record.name = False
                else:
                    nameDepartment = record.department_id.acronym
                    current_year = str(datetime.datetime.now().year)
                    # folio = nameCompany[:2] + "-" + nameBranch[:3] + "-" + current_year + "-" + nameDepartment[:3]
                    # + "-" + record.sequence.lstrip('0')
                    folio = nameCompany[:2] + "-" + nameBranch[:3] + "-" + current_year + "-" + nameDepartment[
                                                                                                :3] + "-" + record.sequence.lstrip(
                        '0')
                    record.name = folio

    @api.depends('company_id')
    def _compute_branch_id(self):
        for record in self:
            if not record.company_id:
                record.branch_ids = False
            else:
                branch = record.company_id.child_ids
                record.branch_ids = branch[0] if branch else False

    @api.depends('age_id')
    def _compute_age_id(self):
        for record in self:
            if not record.age_id:
                record.is_age_other = False
            else:
                if record.age_id.name == "Otro":
                    record.is_age_other = True
                else:
                    record.is_age_other = False

    @api.depends('details.quantity', 'details.quantity_auth')
    def _compute_quantity_requisitions(self):
        for requisition in self:
            requisition.no_requisitions = sum(requisition.details.mapped('quantity'))
            requisition.no_requisitions_auth = sum(requisition.details.mapped('quantity_auth'))

    @api.depends('branch_ids')
    def _compute_total_employee(self):
        for record in self:
            if not record.branch_ids:
                record.total_employee_current = 0
            else:
                company_id = record.company_id.id

                if company_id:
                    emp_data = self.env['hr.employee'].read_group(
                        [('company_id', '=', company_id)],
                        ['company_id'],
                        ['company_id'],
                        lazy=False,
                        orderby='company_id',
                        offset=0,
                        limit=None
                    )

                    result = {company['company_id'][0]: company['__count'] for company in emp_data}
                    record.total_employee_current = result.get(company_id, 0)

    @api.depends('branch_ids')
    def _compute_total_employee_absent(self):
        for record in self:
            if not record.branch_ids:
                record.total_employee_absents = 0
            else:
                company_id = record.branch_ids.id

                if company_id:
                    emp_data = self.env['hr.employee'].read_group(
                        [('company_id', '=', company_id)],
                        ['company_id'],
                        ['company_id'],
                        lazy=False,
                        orderby='company_id',
                        offset=0,
                        limit=None
                    )

                    result = {company['company_id'][0]: company['__count'] for company in emp_data}
                    record.total_employee_absents = result.get(company_id, 0)

    @api.constrains('details')
    def _check_details(self):
        for requisition in self:
            if not requisition.details:
                raise ValidationError("You must create at least one vacancy in the Vacancy section.")

    @api.depends('details.quantity_auth')
    def authorize_requisition(self):
        for requisition in self:
            isvalid = False
            if not requisition.details:
                raise ValidationError("You must create at least one vacancy in the Vacancy section.")
            else:
                if requisition.no_requisitions_auth <= 0:
                    raise ValidationError("The Vacancies approved is required")
                else:
                    isvalid = True

            if isvalid:
                # Se actualiza el Job y el estatus
                requisition.job_id.no_of_recruitment = requisition.job_id.no_of_recruitment + requisition.no_requisitions_auth
                requisition.write({'status': 30, 'last_status': 20, 'status_requisition': 'Autorizado'})

    def refuse_requisition(self):
        for requisition in self:
            last_status = requisition.status
            requisition.write(
                {'status': 60, 'last_status': last_status, 'status_requisition': 'Rechazado'})

    def cancel_requisition(self):
        for requisition in self:
            last_status = requisition.status
            requisition.write(
                {'status': 70, 'last_status': last_status, 'status_requisition': 'Cancelado'})

    def _compute_application_count(self):
        read_group_result = self.env['hr.applicant']._read_group([('requisition_id', 'in', self.ids)], ['requisition_id'], ['__count'])
        result = {job.id: count for job, count in read_group_result}
        for job in self:
            job.application_count = result.get(job.id, 0)