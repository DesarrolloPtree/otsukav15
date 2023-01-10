# -*- coding: utf-8 -*-
{
    'name': "ITL SO Type duplicate",

    'summary': """
        Este módulo permite seleccionar el tipo de orden a utilizar cuando se duplica una 
        orden de venta.""",

    'description': """
        Este módulo permite seleccionar el tipo de orden a utilizar cuando se duplica una 
        orden de venta.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_order_type','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_views.xml',
        'views/templates.xml',
        'wizard/duplicate_sale_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
