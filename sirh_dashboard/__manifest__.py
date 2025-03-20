# -*- coding: utf-8 -*-
{
    'name': 'Fleet Dashboard',
    'version': '1.1',
    'category': 'Fleet',
    'sequence': 0,
    'summary': 'Dashboard de gestion des véhicules et conducteurs',
    'description': "Affichage des statistiques de la flotte de véhicules et suivi de l'entretien.",
    'website': 'https://www.odoo.com/app/employees',
    'author': 'Votre Nom / Entreprise',
    'depends': [
        'base_setup',
        'mail',
        'web',
        # 'fleet',
    ],
    'data': [
        'views/wms_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sirh_dashboard/static/src/lib/highcharts/highcharts.js',
            'sirh_dashboard/static/src/lib/highcharts/highcharts-more.js',
            'sirh_dashboard/static/src/lib/highcharts/modules/variable-pie.js',
            'sirh_dashboard/static/src/js/highchart/drilldown.js',
            'sirh_dashboard/static/src/js/highchart/annotations.js',
            'sirh_dashboard/static/src/js/tools.js',
            'sirh_dashboard/static/src/js/wms_dashboard.js',
            'sirh_dashboard/static/src/lib/highcharts/css/highcharts.css',
            'sirh_dashboard/static/src/css/wms_style.css',
            # 'sirh_dashboard/static/src/xml/wms_dashboard.xml',
        ],
        'web.assets_qweb': [
            'sirh_dashboard/static/src/xml/wms_dashboard.xml'
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
