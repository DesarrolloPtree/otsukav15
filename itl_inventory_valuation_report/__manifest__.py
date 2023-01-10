# -*- coding: utf-8 -*-
{
    'name': "ITL Inventory Valuation Report",

    'summary': """
        Adds some field to the excel report.""",

    'description': """
        Adds some field to the excel report.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','bi_inventory_valuation_reports','stock','stock_account','itl_inventory_moving'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_move_views.xml',
        'views/stock_valuation_layer_views.xml',
        'views/sales_daybook_report_product_category_wizard.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
