# -*- coding: utf-8 -*-
{
    'name': "ITL Post With Account",

    'summary': """
        This module allow to select a default account to post the bills.""",

    'description': """
        This module allow to select a default account to post the bills.
    """,

    'author': "ITLglobal",
    'website': "https://itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_validate_move_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
