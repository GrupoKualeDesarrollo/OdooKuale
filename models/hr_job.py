from odoo import fields, models, api


class hr_job(models.Model):
    _inherit = 'hr.job'

    name_kuale = fields.Char(string='Job Position Kuale', required=True, translate=True)
    city = fields.Char(string='City', required=True, translate=True)
    branch_ids = fields.Many2one('res.company', compute='_compute_branch_id',
                                 domain="[('parent_id', '=', company_id)]", store=True,
                                 readonly=False,
                                 required=False,
                                 ondelete='cascade')

    business_name = fields.Char(string='Business Name', compute="_compute_business_name", readonly=True)
    branch_address = fields.Char(string='Branch Address', compute="_compute_branch", readonly=True)
    branch_report_to = fields.Char(string='Branch Report To', compute="_compute_branch", readonly=True)

    job_tab_ids = fields.Many2one('reclutamiento__kuale.job_tab', string="Tab",
                                  default=lambda self: self.env['reclutamiento__kuale.job_tab'].search(
                                      [], limit=1),
                                  )
    basic_salary = fields.Integer(string='Basic Net Salary', required=True)
    capped_salary = fields.Integer(string='Capped Net Salary', required=True)
    subordinate_id = fields.Many2one('res.users', "Subordinate",
                                     domain="[('share', '=', False), ('company_ids', 'in', company_id)]", tracking=True)

    objective = fields.Text(string='Objective', required=True, translate=True)
    administrative = fields.Boolean(string='Administrative', default=False)

    min_employees = fields.Integer(string='Minimum Employees')
    max_employees = fields.Integer(string='Maximum  Employees')
    # process_details = fields.Text(string='Process Details', translate=True)

    requisition_ids = fields.One2many('reclutamiento__kuale.requisitions', 'job_id', string='Job Position',
                                      groups='base.group_user')

    # Contracts
    trial_period_id = fields.Many2one('reclutamiento__kuale.trial_period', compute='_compute_trial_period_id',
                                      store=True,
                                      domain="[('contract_type_id', '=', contract_type_kuale_id)]", readonly=False,
                                      ondelete='cascade')
    jornada_id = fields.Many2one('reclutamiento__kuale.jornada', compute='_compute_jornada_id',
                                 domain="[('contract_type_id', '=', contract_type_kuale_id)]", store=True,
                                 readonly=False,
                                 ondelete='cascade')
    contract_type_kuale_id = fields.Many2one('reclutamiento__kuale.contract_type',
                                             default=lambda self: self.env['reclutamiento__kuale.contract_type'].search(
                                                 [], limit=1),
                                             )

    comments_contract_type = fields.Char(string='Comments', compute="_compute_comments_contract_type", readonly=True)

    # Activities
    activities_ids = fields.Many2many('reclutamiento__kuale.activities', 'job_act_rel', 'job_id', 'act_id',
                                      string='Activities')

    # Experience
    experiences_ids = fields.Many2many('reclutamiento__kuale.experience', 'job_exp_rel', 'job_id', 'exp_id',
                                      string='Experience')
    experience_activities = fields.Char(string='Experience required for the activities', translate=True)
    comments_specifications = fields.Text(string='Comments or technical specifications', translate=True)

    # Tool and knowledge
    tool_ids = fields.Many2many('reclutamiento__kuale.tools_knowledge', 'job_toolknow_rel', 'job_id', 'tool_id',
                                string='Operational Tools', domain=[('type', '=', 'tool')])
    software_ids = fields.Many2many('reclutamiento__kuale.tools_knowledge', 'job_software_rel', 'job_id', 'soft_id',
                                    string='Operational Tools', domain=[('type', '=', 'software')])

    # Profile
    schooling_ids = fields.Many2many('reclutamiento__kuale.schooling', 'job_schooling_rel', 'job_id', 'sch_id',
                                     string='Schooling')

    age_ids = fields.Many2many('reclutamiento__kuale.age', 'job_age_rel', 'job_id', 'age_id', string='Age Range')
    gender_ids = fields.Many2many('reclutamiento__kuale.gender', 'job_gender_rel', 'job_id', 'gender_id',
                                  string='Gender')

    language_k_ids = fields.Many2many('reclutamiento__kuale.language', 'job_language_rel', 'job_id', 'lan_id',
                                      string='Language')

    # Competencies
    competence_ids = fields.Many2many('reclutamiento__kuale.competencies', 'job_competencies_rel', 'job_id', 'comp_id',
                                      string='Competencies')

    # Internal and external relations
    int_rel_ids = fields.Many2many('reclutamiento__kuale.internal_relations', 'job_internalrel_rel', 'job_id',
                                   'intrel_id', string='Internal Relations')
    ext_rel_ids = fields.Many2many('reclutamiento__kuale.external_relations', 'job_externalrel_rel', 'job_id',
                                   'extrel_id', string='External Relations')
    perf_st_ids = fields.Many2many('reclutamiento__kuale.performance_standars', 'job_performancest_rel', 'job_id',
                                   'perfst_id', string='Performance Standards')
    comments_expetations = fields.Char(string='General Comments/Expectations', translate=True)
    comments_id = fields.One2many('reclutamiento__kuale.comments_exp', 'job_id', string="General Comments/Expectations")

    # Workday
    type_workday = fields.Selection([
        ('fixed_shift', 'Fixed shift'),
        ('rotating_shift', 'Rotating shift')
    ])
    start_time_fixed = fields.Float(string='Start time', store=True)
    end_time_fixed = fields.Float(string='End time', store=True)
    workday = fields.Selection([
        ('diurnal', 'Diurnal'),
        ('nocturnal', 'Nocturnal'),
        ('mixed', 'Mixed'),
    ])
    day_ids = fields.Many2many('reclutamiento__kuale.weekdays', 'job_weekdays_rel', 'job_id', 'day_id', string='Days')
    start_time = fields.Float(string='Start time', store=True)
    end_time = fields.Float(string='End time', store=True)
    days_off = fields.Selection([
        ('rotating', 'Rotating'),
        ('monday', 'Monday'),
    ])

    # Child jobs
    parent_id = fields.Many2one('hr.job', string='Parent job', index=True, check_company=True)
    child_ids = fields.One2many('hr.job', 'parent_id', string='Child Jobs')
    parent_path = fields.Char(index=True, unaccent=False)
    is_Parent_Job = fields.Boolean(string='Is Parent Job', store=True, default=False)

    # Garments
    products = fields.One2many('reclutamiento__kuale.product_garments', 'job_id', string="Garments", required=True)

    # Filter questions
    filter_question_id = fields.Many2one(
        'survey.survey', "Survey",
        help="Choose the survey to be carried out in the job screener that will be for the exclusive use of recruiters.")

    # Life and career plan
    slide_for_ids = fields.Many2many('slide.channel', 'job_slfor_rel', 'job_id', 'slfor_id', string='Capacitaciones Para')
    slide_during_ids = fields.Many2many('slide.channel', 'job_slduring_rel', 'job_id', 'sldur_id', string='Capacitaciones Durante')
    potential_future_jobs = fields.Many2many(
        'hr.job',
        'hr_job_future_rel',
        'current_job_id',
        'future_job_id',
        string='Puestos a aspirar',
        domain=[('is_Parent_Job', '=', True)]
    )


    @api.depends('company_id')
    def _compute_business_name(self):
        for job in self:
            bussinnes = job.company_id.business_name
            job.business_name = bussinnes

    @api.depends('branch_ids')
    def _compute_branch(self):
        for job in self:
            branch_address_parts = []

            # Concatenar los diferentes campos de la dirección
            street = job.branch_ids.street
            if street:
                branch_address_parts.append(street)

            street2 = job.branch_ids.street2
            if street2:
                branch_address_parts.append(street2)

            city = job.branch_ids.city
            if city:
                branch_address_parts.append(city)

            state = job.branch_ids.state_id
            if state:
                branch_address_parts.append(state.name)

            zip_address = job.branch_ids.zip
            if zip_address:
                branch_address_parts.append(zip_address)

            country = job.branch_ids.country_id
            if country:
                branch_address_parts.append(country.name)

            job.branch_address = ', '.join(branch_address_parts)

            # Obtener el usuario relacionado
            report_to_user = job.branch_ids.reports_to
            if report_to_user:
                job.branch_report_to = report_to_user.name
            else:
                job.branch_report_to = False

    @api.depends('contract_type_kuale_id')
    def _compute_trial_period_id(self):
        for record in self:
            if record.contract_type_kuale_id:
                record.trial_period_id = record.contract_type_kuale_id.trial_period_ids[
                    0] if record.contract_type_kuale_id.trial_period_ids else False
            else:
                record.trial_period_id = False

    @api.depends('trial_period_id')
    def _compute_jornada_id(self):
        for record in self:
            if not record.trial_period_id:
                record.jornada_id = False
            else:
                jornada = record.contract_type_kuale_id.jornada_ids
                record.jornada_id = jornada[0] if jornada else False

    @api.depends('contract_type_kuale_id')
    def _compute_comments_contract_type(self):
        for contract in self:
            description = contract.contract_type_kuale_id.description
            contract.comments_contract_type = description

    @api.depends('activities_k_id')
    def _compute_knowledge_id(self):
        for record in self:
            if record.activities_k_id:
                record.a_knowledge_id = record.activities_k_id.a_knowledge_ids[
                    0] if record.activities_k_id.a_knowledge_ids else False
            else:
                record.a_knowledge_id = False

    @api.depends('activities_k_id')
    def _compute_knowledge_id(self):
        for record in self:
            if record.activities_k_id:
                record.a_knowledge_id = record.activities_k_id.a_knowledge_ids[
                    0] if record.activities_k_id.a_knowledge_ids else False
            else:
                record.a_knowledge_id = False

    @api.depends('language_k_ids')
    def _compute_level_id(self):
        for record in self:
            if not record.language_k_ids:
                record.level_ids = False
            else:
                level = record.language_k_ids.language_level_ids
                record.level_ids = level[0] if level else False

    @api.depends('company_id')
    def _compute_branch_id(self):
        for record in self:
            if not record.company_id:
                record.branch_ids = False
            else:
                branch = record.company_id.child_ids
                record.branch_ids = branch[0] if branch else False


class Weekdays(models.Model):
    _name = 'reclutamiento__kuale.weekdays'

    name = fields.Char()
    job_ids = fields.Many2many('hr.job', 'job_weekdays_rel', 'day_id', 'job_id', string='Job')


class Gender(models.Model):
    _name = 'reclutamiento__kuale.gender'

    name = fields.Char()
    job_ids = fields.Many2many('hr.job', 'job_gender_rel', 'gender_id', 'job_id', string='Job')


class ProductsGarments(models.Model):
    _name = 'reclutamiento__kuale.product_garments'

    # Relation Job
    # job_ids = fields.Many2many('hr.job', 'job_garments_rel', 'garment_id', 'job_id', string='Job')

    job_id = fields.Many2one("hr.job", string="Job")

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('product_tmpl_id', '=', product_template_id)]"
    )

    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        required=True,
        search='_search_product_template_id',
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.
        domain=[('sale_ok', '=', True)])

    quantity = fields.Integer(string='Quantity', required=True)

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.onchange('product_template_id')
    def _compute_product(self):
        for record in self:
            product_id = self.product_template_id.id
            if product_id:
                product = self.env['product.product'].search([('product_tmpl_id', '=', product_id)], limit=1)
                record.product_id = product.id

class Experience(models.Model):
    _name = 'reclutamiento__kuale.experience'
    _description = 'reclutamiento__kuale.experience'

    job_ids = fields.Many2many('hr.job', 'job_exp_rel', 'exp_id', 'job_id', string='Job')

    active = fields.Boolean(default=True)
    name = fields.Char(string='Experience required for the activities', required=True)
    comments = fields.Text(string='Comments or technical specifications', translate=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Activity name already exists!"),
    ]


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    job_slfor_id = fields.Many2many('hr.job', 'job_slfor_rel', 'slfor_id', 'job_id',
                                    string='Formación profesional para',
                                    help="Puestos de trabajo que necesitan de este curso en un futuro.")
    job_slduring_id = fields.Many2many('hr.job', 'job_slduring_rel', 'sldur_id', 'job_id',
                                       string='Formación profesional durante',
                                       help="Puestos de trabajo que necesitan de este curso.")
