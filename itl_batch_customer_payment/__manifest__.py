# -*- coding: utf-8 -*-
{
    'name': "ITL Batch Customer Payment",

    'summary': """
        Este módulo permite conciliar automáticamente un pago a distintas facturas.""",

    'description': """
        Este módulo permite conciliar automáticamente un pago a distintas facturas.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlighten.com",

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
        'views/account_payment_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
