from odoo import models, fields, api


class job_tab(models.Model):
    _name = 'reclutamiento__kuale.job_tab'
    _description = 'reclutamiento__kuale.job_tab'

    active = fields.Boolean(default=True)
    name = fields.Char('Name', required=True, translate=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company, required=True)
    department_id = fields.Many2one('hr.department', "Department", check_company=True, required=True)
    salary = fields.Integer('Salary')
    # report_to_id = fields.Many2one('res.users', 'Report to', check_company=True)
    report_to_id = fields.Many2one(
        'hr.employee', 'Report To', compute='_compute_parent_id', store=True, readonly=False,
        check_company=True)
    address = fields.Char('Address')
    # subordinates_ids = fields.Many2many('res.users', string='Subordinates', domain="[('share', '=', False),
    # ('company_ids', 'in', company_id)]")
    subordinates_ids = fields.Many2many('hr.employee', 'Subordinates', compute='_compute_subordinate_ids', store=True,
                                        readonly=False,
                                        check_company=True)

    business_name = fields.Char('Business Name')
    daily_salary_contract = fields.Integer('Daily Contract Salary')
    daily_salary_integrated = fields.Integer('Integrated Daily Salary')
    net_monthly_salary = fields.Integer('Net Monthly Salary')
    capped_net_monthly_salary = fields.Integer('Capped Net Monthly Salary')
    gross_monthly_salary = fields.Integer('Gross Monthly Salary ')
    type_benefits = fields.Char('Type')
    benefits = fields.Char('Benefits')
    description_policies = fields.Char('Description/Policies')
    type_bonus = fields.Char('Type')
    name_bonus = fields.Char('Name')
    amount_bonus = fields.Integer('amount')

    # employee_ids = fields.Many2many('hr.employee', 'employee_category_rel', 'category_id', 'emp_id',
    #                                string='Employees')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Job Tab name already exists!"),
    ]

    @api.depends('department_id')
    def _compute_parent_id(self):
        for employee in self.filtered('department_id.manager_id'):
            employee.report_to_id = employee.department_id.manager_id

    @api.depends('department_id')
    def _compute_subordinate_ids(self):
        for employee in self.filtered('department_id.manager_id'):
            employee.subordinates_ids = employee.department_id.manager_id
