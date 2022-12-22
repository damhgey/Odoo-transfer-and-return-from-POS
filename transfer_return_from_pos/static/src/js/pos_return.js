odoo.define("transfer_return_from_pos.CreateReturnButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const { useListener } = require("web.custom_hooks");
    const Registries = require("point_of_sale.Registries");

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
        json.return_picking_type_id = selected_operation_type_id;
        return json;
        },
    });

    var selected_operation_type_id
    function get_return_operation_type(opt_id){
        selected_operation_type_id = opt_id
    }


    class CreateReturnButton extends PosComponent {

        constructor() {
            super(...arguments);
            useListener("click", this.onClick);
        }

        async onClick() {
            const return_operation_type_ids = this.env.pos.config.operation_type_ids;
            const returnOperationTypes = await this.rpc({
                model: 'stock.picking.type',
                method: 'search_read',
                args: [[['id', 'in', return_operation_type_ids], ['is_return', '=', true ]]],
            })
            console.log(returnOperationTypes)
            const returnSelectionList = returnOperationTypes.map((operationType) => ({
                id: operationType.id,
                label: operationType.name,
                item: operationType,
            }));
            console.log(returnSelectionList)
            const { confirmed, payload: selectedOperationType } = await this.showPopup('SelectionPopup', {
                title: this.env._t('Select the Operation Type for this Return'),
                list: returnSelectionList,
            });

            if (!confirmed) return;
            this.trigger('discard');

            self = this;
            var order = self.env.pos.get_order();
            var data = order.export_as_JSON();
            var selectedOperationType_id = selectedOperationType.id ;
            get_return_operation_type(selectedOperationType_id)

            await this.showPopup('ReturnInputPopup', {
                title: this.env._t('Enter Your Note'),
                startingValue: '',
            });
      }
    }

    ProductScreen.addControlButton({
        component: CreateReturnButton,
        condition: function () {
            return true;
        },
    });

    CreateReturnButton.template = "CreateReturnButton";
    Registries.Component.add(CreateReturnButton);
    return CreateReturnButton;
  }
);
