# -*- coding: utf-8 -*-
{
    'name': "ITL Sales Analysis Report",

    'summary': """
        Report for sales analysis with stock moves and invoice moves.""",

    'description': """
        Report for sales analysis with stock moves and invoice moves.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/res_config_settings_views.xml',
        'wizard/inventory_analysis_report_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
