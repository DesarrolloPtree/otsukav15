# -*- coding: utf-8 -*-
{
    'name': "ITL Invoices Redirect",

    'summary': """
        This module allows to redirect to invoices by file and then applying payment.""",

    'description': """
        This module allows to redirect to invoices by file and then applying payment.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/load_invoices_views.xml',
        'views/account_move_reversal_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
