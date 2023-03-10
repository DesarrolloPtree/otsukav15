# -*- coding: utf-8 -*-
{
    'name': "itlighten_xml_to_invoice",

    'summary': """
        This module extend functionality when import xml to create invoice.""",

    'description': """
        This module extend functionality when import xml to create invoice.
    """,

    'author': "AMB",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','partner_extended', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/xml_to_invoice.xml',
        'views/company.xml',
        'views/templates.xml',
        'views/legacy_invoice_product.xml',
        'views/product_words.xml',
        'wizard/sh_message_wizard.xml',
        'wizard/create_partner.xml',
        'wizard/create_product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}