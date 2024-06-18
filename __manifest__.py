# -*- coding: utf-8 -*-
{
    'name': "Reclutamiento_Kuale",

    'summary': "Módulo para administrar el reclutamiento de personal",

    'description': """
Long description of module's purpose
    """,

    'author': "DWIT",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'hr_contract',
        'website',
        'website_slides',
        # 'sale'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'data/ir_sequence_data.xml',
        'views/hr_department_views.xml',
        'views/requisitions_view.xml',
        'views/hr_job_views.xml',
        'views/catalog_segments_views.xml',
        'views/catalog_age_views.xml',
        'views/catalog_job_tab_views.xml',
        'views/catalog_contract_type_views.xml',
        'views/catalog_activities_views.xml',
        'views/catalog_tools_knowledge_views.xml',
        'views/catalog_schooling_views.xml',
        'views/catalog_language_views.xml',
        'views/catalog_competencies_views.xml',
        'views/catalog_internal_rel_views.xml',
        'views/catalog_external_rel_views.xml',
        'views/catalog_performance_stand_views.xml',
        'views/catalog_branchType_views.xml',
        'views/catalog_businessType_views.xml',
        'views/catalog_imssRegistration_views.xml',
        'views/catalog_legalRepresentative_views.xml',
        'views/catalog_stampCertificate_views.xml',
        'views/res_company_views.xml',
        'views/website_hr_recruitment_templates.xml',
        'views/vacantes_template.xml',
        'views/vacantes_page.xml',
        'views/website_menu_views.xml',
        'views/hr_applicant_views.xml',
        'views/hr_recruitment_stage.xml',
        'views/clinic_views.xml',
        'views/mail_form_interview.xml',
        'views/mail_template.xml',
        'views/website_form_recruitment.xml',
        'views/slide_channel_views.xml',
        'views/hr_employee_views.xml',
        'views/credentials_views.xml',
        'report/contract_reports.xml',
        'views/hr_contract_views.xml',
        'report/contract_templates.xml',
        'views/contract_format_views.xml',
        'views/catalog_type_format_views.xml',
        'views/hr_applicant_documentation_modal.xml',
        'views/views.xml'
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            # 'reclutamiento__kuale/static/src/fields/auto_save_hr_job_competences/*',
            'reclutamiento__kuale/static/src/**/*',
            'reclutamiento__kuale/static/src/fields/**/*',
            # 'reclutamiento__kuale/static/src/fields/skills_one2many/*',
            # 'reclutamiento__kuale/static/src/**/*',
            # 'reclutamiento__kuale/static/src/views/*.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
    ],
    'controllers': [
        'controllers/websiteController.py',
    ]
}

