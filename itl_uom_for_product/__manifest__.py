# -*- coding: utf-8 -*-
{
    'name': "ITL UoMs for product",

    'summary': """
        This module allow to define the UoMs that the product should use in SO an PO.""",

    'description': """
        This module allow to define the UoMs that the product should use in SO an PO.
    """,

    'author': "ITLglobal",
    'website': "https://itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
