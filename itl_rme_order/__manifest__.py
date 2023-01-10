# -*- coding: utf-8 -*-
{
    'name': "ITL RME Order",

    'summary': """
        Module for RME Orders.""",

    'description': """
        Module for RME Orders.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','itl_inventory_moving'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_type_views.xml',
        'views/sale_views.xml',
        'views/stock_picking_views.xml',
        'views/templates.xml',
        'data/mail_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
