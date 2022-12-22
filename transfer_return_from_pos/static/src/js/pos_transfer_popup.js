odoo.define('transfer_return_from_pos.TransferInputPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { useListener } = require('web.custom_hooks');
    var { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var module = require('point_of_sale.models');


    var _super_order = module.Order.prototype;
    module.Order = module.Order.extend({
        initialize: function () {
            _super_order.initialize.apply(this, arguments);
            this.save_to_db();
        },

        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
             json.return_picking_type_id = this.pos.config.return_picking_type_id[0];
            return json;
        },
    });


    class TransferInputPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }

        async _showCreatedTransfer(url, transfer) {
            const {confirmed} = await this.showPopup('ConfirmPopup', {
                  confirmText: _lt('Open Transfer'),
                  cancelText: _lt('Close'),
                 'title': 'Transfer Created',
                 'body': transfer,
            });

            if (confirmed) {
                window.open(url);
            }
        }

        async _clickTransfer() {
            self = this;
            var order = self.env.pos.get_order();
            var data = order.export_as_JSON();
            data.transfer_note = this.state.inputValue;
            data.pos_session = self.env.pos.pos_session ? self.env.pos.pos_session.id : false
            rpc.query({
                model: 'stock.picking',
                method: 'create_transfer_from_pos',
                args: [data],
            }).then(function (transfer_data) {
                if (transfer_data['result']) {
                    var url = window.location.origin + '/web#cids=1&action=351&model=stock.picking&view_type=list&menu_id=227';
                    var transfer = transfer_data['result']
                    self._showCreatedTransfer(url, transfer)
                }else{
                    Gui.showPopup('ConfirmPopup', {
                        'title': 'The following products are not available',
                        'body': transfer_data['products'],
                    });
                }
            }, function (err, event) {
                Gui.showPopup('ErrorPopup', {
                    'title': 'Error: Could not Save Changes',
                    'body': 'Your Internet connection is probably down.',
                });
            });
        }
    }

    TransferInputPopup.template = 'TransferInputPopup';
    TransferInputPopup.defaultProps = {
        confirmText: _lt('Save'),
        cancelText: _lt('Cancel'),
        title: '',
        body: '',
        startingValue: '',
        args_data: '',
    };

    Registries.Component.add(TransferInputPopup);

    return TransferInputPopup;
});
