{
    'name': 'Booking System',
    'version': '12.0.1.0.0',
    'category': 'Extra Tool',
    'summary': 'Booking and reservation system',
    'author': 'Loomoni Morwo',
    'company': 'Kalen Limited',
    'website': "https://www.kalen.tz.co",
    'depends': ['account', 'base', 'sale', 'board', 'base_setup', 'product', 'analytic', 'portal', 'digest'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizards/create_down_payment.xml',
        'views/create_venue.xml',
        'views/booking.xml',
        'views/venuepayment.xml',
        'views/settings.xml',
        'views/report.xml',
        'views/payment_over_view.xml',
        'data/sequence.xml',
        'data/mail_template.xml',
        'reports/report.xml',
        'reports/report_template.xml',

    ],
    'qweb': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}