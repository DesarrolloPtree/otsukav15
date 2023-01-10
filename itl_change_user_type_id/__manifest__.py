# -*- coding: utf-8 -*-
{
    'name': "itl_change_user_type_id",

    'summary': """
        Módulo para editar el campo de user_type_id en la cuenta""",

    'description': """
        Los diferentes subtitpos permiten la división de los reportes de contabilidad a un nivel más granular.
    """,

    'author': "ITL GLobal",
    'website': "https://www.itlglobal.tech/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '2.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
