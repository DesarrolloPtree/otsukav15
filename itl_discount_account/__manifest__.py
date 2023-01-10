# -*- coding: utf-8 -*-
{
    'name': "ITL Discount Account",

    'summary': """
        Este módulo permite modificar la contabilidad de ordenes de venta 
        de tipo Discount.""",

    'description': """
        Este módulo permite modificar la contabilidad de ordenes de venta 
        de tipo Discount.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_order_type'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_type_view.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
