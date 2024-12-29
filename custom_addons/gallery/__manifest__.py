{
    'name': 'Gallery Module',
    'version': '1.0',
    'summary': 'Manage gallery images with details',
    'author': 'Takeshi',
    'depends': ['website', 'base'],
    'data': [
        'views/gallery_view.xml',
        'views/gallery_template.xml',
        # 'views/gallery_form.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'views/gallery_template.xml',
    ],
    'installable': True,
    'application': True,
}
