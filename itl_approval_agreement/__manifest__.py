# -*- coding: utf-8 -*-
{
    'name': "itl_approval_agreement",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','itl_approvals_general','agreement','agreement_legal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/agreement_views.xml',
        'views/approval_request_views.xml',
        'views/res_config_setting_views.xml',
        'wizard/send_message_feedback.xml',
        'wizard/create_agreement_wizard.xml',
        'views/templates.xml',
        'data/approval_category.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
