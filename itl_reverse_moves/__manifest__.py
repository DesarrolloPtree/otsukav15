# -*- coding: utf-8 -*-
{
    'name': "ITL Reverse Moves",

    'summary': """
        This module allow to reverse and create new draft invoices for many invoices at same time.""",

    'description': """
        This module allow to reverse and create new draft invoices for many invoices at same time.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_mx_edi', 'stock_account','itl_inventory_moving','itl_rme_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'views/templates.xml',
        'views/res_config_settings_views.xml',
        'views/sale_views.xml',
        'data/account_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
