from odoo import http, fields
from odoo.addons.website.controllers.main import Website
from odoo.http import request
from odoo.tools.misc import groupby
from datetime import datetime, timedelta

from werkzeug.exceptions import BadRequest
from odoo.exceptions import AccessDenied, ValidationError, UserError


class CustomWebsite(Website):
    _jobs_per_page = 12

    def sitemap_jobs(env, rule, qs):
        if not qs or qs.lower() in '/jobs':
            yield {'loc': '/jobs'}

    @http.route(['/test'], type='http', auth="public", website=True)
    def test(self, **kwargs):
        return "Mensaje de prueba desde el controlador"

    @http.route(['/vacantes'], type='http', auth="public", website=True)
    def vacantes(self, **kwargs):
        return http.request.render('reclutamiento__kuale_vacantes_template')

    @http.route([
        '/jobs/company',
        '/jobs/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_jobs)
    def jobs_extended(self, country_id=None, department_id=None, office_id=None, contract_type_id=None,
                      is_remote=False, is_other_department=False, is_untyped=None, page=1, search=None,
                      company_id=None, **kwargs):
        # Obtiene el entorno de la solicitud
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        print("filtrar trabajos", company_id)
        # Filtrar los trabajos por compañía
        if company_id:
            Jobs = env['hr.job'].search([('company_id', '=', company_id)])
        else:
            Jobs = env['hr.job']
        return request.render('website_hr_recruitment.index', {
            'Jobs': Jobs
        })

    @http.route([
        '/jobs',
        '/jobs/<int:company_id>',
        '/jobs/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_jobs)
    def jobs(self, country_id=None, department_id=None, office_id=None, contract_type_id=None,
             is_remote=False, is_other_department=False, is_untyped=None, page=1, search=None, company_id=None,**kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        Country = env['res.country']
        Jobs = env['hr.job']
        print("hr.job", Jobs)
        Department = env['hr.department']
        # Filtrar los trabajos por compañía
        print("hola here")
        print("company_id",company_id)
        if company_id:
            Jobs = env['hr.job'].search([('company_id', '=', company_id)])
            print("hr.job filtrado por comapyby", Jobs)
        country = Country.browse(int(country_id)) if country_id else None
        department = Department.browse(int(department_id)) if department_id else None
        office_id = int(office_id) if office_id else None
        contract_type_id = int(contract_type_id) if contract_type_id else None

        # Default search by user country
        if not (country or department or office_id or contract_type_id or kwargs.get('all_countries')):
            if request.geoip.country_code:
                countries_ = Country.search([('code', '=', request.geoip.country_code)])
                country = countries_[0] if countries_ else None
                if country:
                    country_count = Jobs.search_count(AND([
                        request.website.website_domain(),
                        [('address_id.country_id', '=', country.id)]
                    ]))
                    if not country_count:
                        country = False

        options = {
            'displayDescription': True,
            'allowFuzzy': not request.params.get('noFuzzy'),
            'country_id': country.id if country else None,
            'department_id': department.id if department else None,
            'office_id': office_id,
            'contract_type_id': contract_type_id,
            'is_remote': is_remote,
            'is_other_department': is_other_department,
            'is_untyped': is_untyped,
        }
        total, details, fuzzy_search_term = request.website._search_with_fuzzy("jobs", search,
                                                                               limit=1000,
                                                                               order="is_published desc, sequence, no_of_recruitment desc",
                                                                               options=options)
        # Browse jobs as superuser, because address is restricted
        jobs = details[0].get('results', Jobs).sudo()

        def sort(records_list, field_name):
            """ Sort records in the given collection according to the given
            field name, alphabetically. None values instead of records are
            placed at the end.

            :param list records_list: collection of records or None values
            :param str field_name: field on which to sort
            :return: sorted list
            """
            return sorted(
                records_list,
                key=lambda item: (item is None, item and item[field_name] or ''),
            )

        # Countries
        if country or is_remote:
            cross_country_options = options.copy()
            cross_country_options.update({
                'allowFuzzy': False,
                'country_id': None,
                'is_remote': False,
            })
            cross_country_total, cross_country_details, _ = request.website._search_with_fuzzy("jobs",
                                                                                               fuzzy_search_term or search,
                                                                                               limit=1000,
                                                                                               order="is_published desc, sequence, no_of_recruitment desc",
                                                                                               options=cross_country_options)
            # Browse jobs as superuser, because address is restricted
            cross_country_jobs = cross_country_details[0].get('results', Jobs).sudo()
        else:
            cross_country_total = total
            cross_country_jobs = jobs
        country_offices = set(j.address_id or None for j in cross_country_jobs)
        countries = sort(set(o and o.country_id or None for o in country_offices), 'name')
        count_per_country = {'all': cross_country_total}
        for c, jobs_list in groupby(cross_country_jobs, lambda job: job.address_id.country_id):
            count_per_country[c] = len(jobs_list)
        count_remote = len(cross_country_jobs.filtered(lambda job: not job.address_id))
        if count_remote:
            count_per_country[None] = count_remote

        # Departments
        if department or is_other_department:
            cross_department_options = options.copy()
            cross_department_options.update({
                'allowFuzzy': False,
                'department_id': None,
                'is_other_department': False,
            })
            cross_department_total, cross_department_details, _ = request.website._search_with_fuzzy("jobs",
                                                                                                     fuzzy_search_term or search,
                                                                                                     limit=1000,
                                                                                                     order="is_published desc, sequence, no_of_recruitment desc",
                                                                                                     options=cross_department_options)
            cross_department_jobs = cross_department_details[0].get('results', Jobs)
        else:
            cross_department_total = total
            cross_department_jobs = jobs
        departments = sort(set(j.department_id or None for j in cross_department_jobs), 'name')
        count_per_department = {'all': cross_department_total}
        for d, jobs_list in groupby(cross_department_jobs, lambda job: job.department_id):
            count_per_department[d] = len(jobs_list)
        count_other_department = len(cross_department_jobs.filtered(lambda job: not job.department_id))
        if count_other_department:
            count_per_department[None] = count_other_department

        # Offices
        if office_id or is_remote:
            cross_office_options = options.copy()
            cross_office_options.update({
                'allowFuzzy': False,
                'office_id': None,
                'is_remote': False,
            })
            cross_office_total, cross_office_details, _ = request.website._search_with_fuzzy("jobs",
                                                                                             fuzzy_search_term or search,
                                                                                             limit=1000,
                                                                                             order="is_published desc, sequence, no_of_recruitment desc",
                                                                                             options=cross_office_options)
            # Browse jobs as superuser, because address is restricted
            cross_office_jobs = cross_office_details[0].get('results', Jobs).sudo()
        else:
            cross_office_total = total
            cross_office_jobs = jobs
        offices = sort(set(j.address_id or None for j in cross_office_jobs), 'city')
        count_per_office = {'all': cross_office_total}
        for o, jobs_list in groupby(cross_office_jobs, lambda job: job.address_id):
            count_per_office[o] = len(jobs_list)
        count_remote = len(cross_office_jobs.filtered(lambda job: not job.address_id))
        if count_remote:
            count_per_office[None] = count_remote

        # Employment types
        if contract_type_id or is_untyped:
            cross_type_options = options.copy()
            cross_type_options.update({
                'allowFuzzy': False,
                'contract_type_id': None,
                'is_untyped': False,
            })
            cross_type_total, cross_type_details, _ = request.website._search_with_fuzzy("jobs",
                                                                                         fuzzy_search_term or search,
                                                                                         limit=1000,
                                                                                         order="is_published desc, sequence, no_of_recruitment desc",
                                                                                         options=cross_type_options)
            cross_type_jobs = cross_type_details[0].get('results', Jobs)
        else:
            cross_type_total = total
            cross_type_jobs = jobs
        employment_types = sort(set(j.contract_type_id for j in jobs if j.contract_type_id), 'name')
        count_per_employment_type = {'all': cross_type_total}
        for t, jobs_list in groupby(cross_type_jobs, lambda job: job.contract_type_id):
            count_per_employment_type[t] = len(jobs_list)
        count_untyped = len(cross_type_jobs.filtered(lambda job: not job.contract_type_id))
        if count_untyped:
            count_per_employment_type[None] = count_untyped

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            url_args=request.httprequest.args,
            total=total,
            page=page,
            step=self._jobs_per_page,
        )
        offset = pager['offset']
        jobs = jobs[offset:offset + self._jobs_per_page]

        office = env['res.partner'].browse(int(office_id)) if office_id else None
        contract_type = env['hr.contract.type'].browse(int(contract_type_id)) if contract_type_id else None

        # Render page
        return request.render("reclutamiento__kuale.index", {
            'jobs': jobs,
            'countries': countries,
            'departments': departments,
            'offices': offices,
            'employment_types': employment_types,
            'country_id': country,
            'department_id': department,
            'office_id': office,
            'contract_type_id': contract_type,
            'is_remote': is_remote,
            'is_other_department': is_other_department,
            'is_untyped': is_untyped,
            'pager': pager,
            'search': fuzzy_search_term or search,
            'search_count': total,
            'original_search': fuzzy_search_term and search,
            'count_per_country': count_per_country,
            'count_per_department': count_per_department,
            'count_per_office': count_per_office,
            'count_per_employment_type': count_per_employment_type,
        })

    @http.route('/jobs/apply2/<model("hr.job"):job>', type='http', auth="public", website=True, sitemap=True)
    def jobs_apply1(self, job, **kwargs):
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        applicant = request.env['hr.applicant']
        about_vacancy_options = applicant.fields_get(['about_vacancy'])['about_vacancy']['selection']
        gender_options = applicant.fields_get(['gender'])['gender']['selection']
        applicant2 = request.env['res.company'].search([('id', '=', job.company_id.id)])
        companyName = applicant2[0].name
        schoolarship_options = applicant.fields_get(['scholarship'])['scholarship']['selection']
        return request.render("reclutamiento__kuale.apply2", {
            'job': job,
            'record': applicant,
            'error': error,
            'default': default,
            'companyName': companyName,
            'about_vacancy_options': about_vacancy_options,
            'gender_options': gender_options,
            'schoolarship_options': schoolarship_options,
        })

    @http.route('/jobs/formRecruitment/<int:applicant_id>/<string:token>', type='http', auth="public", website=True,
                sitemap=True)
    def jobs_apply(self, applicant_id, token, **kwargs):
        applicant_record = request.env['hr.applicant'].sudo().browse(applicant_id)
        vigency_record = request.env['vigency_complement'].sudo().search([('token', '=', token)], limit=1)
        current_date = fields.Datetime.now()
        # print('vigency_record: ', vigency_record.vigency,'current date: ',current_date)
        days_passed = (current_date - vigency_record.vigency).days
        print("dias:", days_passed)
        # Verificar si ya pasaron 7 días
        if days_passed >= 7:
            return request.render("reclutamiento__kuale.expiredPage", {})
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        applicant = request.env['hr.applicant']
        applicant_b = request.env['hr.applicant.beneficiary']
        beneficiary_relationship_options = \
            applicant_b.fields_get(['beneficiary_relationship'])['beneficiary_relationship']['selection']
        beneficiary_relationship_options.insert(0, ('', '   '))

        marital_status = applicant.fields_get(['marital_status'])['marital_status']['selection']
        about_vacancy_options = applicant.fields_get(['about_vacancy'])['about_vacancy']['selection']
        gender_options = applicant.fields_get(['gender'])['gender']['selection']
        schoolarship_options = applicant.fields_get(['scholarship'])['scholarship']['selection']
        clinics = request.env['reclutamiento__kuale.clinic'].search([])
        imss_clinic_options = [(clinic.id, clinic.name) for clinic in clinics]
        nationality_options = applicant.fields_get(['nationality'])['nationality']['selection']
        blood_type_options = applicant.fields_get(['blood_type'])['blood_type']['selection']
        job = applicant_record.job_id
        product_garments = job.products
        try:
            product_template_variants = {}
            for garment in product_garments:
                product_template_id = garment.product_template_id.id
                product_name = garment.product_template_id.name
                if product_template_id not in product_template_variants:
                    product_template_variants[product_template_id] = {
                        'name': product_name,
                        'variants': []
                    }
                    variants = garment.product_template_id.product_variant_ids
                    for variant in variants:
                        variant_dict = variant.read()[0]
                        product_template_variants[product_template_id]['variants'].append(variant_dict)
        except Exception as e:
            print("Error JOB GET :", e)
        # print("product_template_variants...", product_template_variants)
        return request.render("reclutamiento__kuale.formRecruitment", {
            'record': applicant,
            'applicant_record': applicant_record,
            'marital_status': marital_status,
            'beneficiary_relationship_options': beneficiary_relationship_options,
            'about_vacancy_options': about_vacancy_options,
            'gender_options': gender_options,
            'schoolarship_options': schoolarship_options,
            'imss_clinic_options': imss_clinic_options,
            'nationality_options': nationality_options,
            'blood_type_options': blood_type_options,
            'product_template_variants': product_template_variants,
            'error': error,
            'default': default
        })

