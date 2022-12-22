# -*- coding: utf-8 -*-
{
    'name': "Transfer And Return From POS",
    'summary': """ Transfer And Return From Pos """,
    'description': """
        Create a transfer or return from POS with a specific operation type that you
        can define more than one operation type for transfer and return in POS configuration. 
    """,
    'author': "Ahmed Alsayed Aldamhogy",
    'version': '15.0',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'views/pos_config.xml',
        'views/stock_picking.xml',
        'views/product.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'transfer_return_from_pos/static/src/js/pos_transfer.js',
            'transfer_return_from_pos/static/src/js/pos_transfer_popup.js',
            'transfer_return_from_pos/static/src/js/pos_return.js',
            'transfer_return_from_pos/static/src/js/pos_return_popup.js',
        ],
        'web.assets_qweb': [
            'transfer_return_from_pos/static/src/xml/pos.xml',
            'transfer_return_from_pos/static/src/xml/transfer_popup.xml',
            'transfer_return_from_pos/static/src/xml/return_popup.xml',
        ],
    },

}
