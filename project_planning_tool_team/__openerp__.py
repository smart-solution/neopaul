{
    'name': 'Project Planning Tool Team',
    'description': """
    """,
    'version': '1.0',
    'depends': ['base', 'web', "web_kanban","project",'neopaul_project'],
    'js': [
        'static/src/js/project_planning.js',
        
         'static/src/js/moment.js',
#        "static/lib/jquery-ui-timepicker-addon.js",
    ],
    'css': [
        'static/src/css/project_planning.css'
    ],
    'qweb' : [
        'static/src/xml/project_planning.xml',
    ],
    'data':['project_view.xml'],
    'auto_install': False,
    'installable': True,
}
