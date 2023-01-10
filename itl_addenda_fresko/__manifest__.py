# -*- coding: utf-8 -*-
{
    'name': "ITL Addenda Fresko",

    'summary': """
        This module adds addenda for Fresko customer.""",

    'description': """
        This module adds addenda for Fresko customer.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','itl_addenda_general','l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/data.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/fresko_addenda.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
