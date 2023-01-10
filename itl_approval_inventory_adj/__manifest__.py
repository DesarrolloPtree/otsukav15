# -*- coding: utf-8 -*-
{
    'name': "ITL Approval Inventory Adjusment",

    'summary': """
        This module adds approval functionality for inventory adjusment.""",

    'description': """
        This module adds approval functionality for inventory adjusment.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_account','itl_approvals_general'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_inventory_views.xml',
        'views/res_config_settings_views.xml',
        'views/approval_request_views.xml',
        'views/templates.xml',
        'data/approval_category_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
