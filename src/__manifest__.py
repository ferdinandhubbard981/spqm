{
    'name': 'spqm',
    'description': 'generate quotes for a solar panel system installation',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/spqm_installation_views.xml',
        'views/spqm_installation_zone_views.xml',
        'views/spqm_menus.xml'
    ],
    'license': 'Other proprietary'
}
