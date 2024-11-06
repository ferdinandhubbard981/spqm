{
    'name': 'spqm',
    'description': 'generate quotes for a solar panel system installation',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'report/spqm_installation_templates.xml',
        'report/spqm_installation_reports.xml',
        'views/spqm_installation_views.xml',
        'views/spqm_installation_zone_views.xml',
        'views/spqm_solar_panel_views.xml',
        'views/spqm_menus.xml'
    ],
    'license': 'Other proprietary'
}
