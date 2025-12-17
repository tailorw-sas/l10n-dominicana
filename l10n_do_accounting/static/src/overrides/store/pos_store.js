import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // NCF is now embedded in order.name by the server
    // No complex RPC needed since name is automatically synced
    async postSyncAllOrders(orders) {
        await super.postSyncAllOrders(orders);

        // Log for debugging
        if (this.company.country_id?.code === "DO" && orders) {
            for (const order of orders) {
                console.log("L10N_DO: Order synced with name:", order.name);
            }
        }
    },
});
