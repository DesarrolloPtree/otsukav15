# -*- coding: utf-8 -*-
{
    'name': "ITL Bancomer Reimbursement Payment",

    'summary': """
        Este módulo permite generar archivos para pagos con Bancomer.""",

    'description': """
        Este módulo permite generar archivos para pagos con Bancomer.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
        'views/templates.xml',
        'wizard/prepare_bancomer_files_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
