import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    is_dominican_country() {
        return this.company.country_id?.code === "DO";
    },
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        if (this.is_dominican_country()) {
            // NCF is now embedded in this.name by the server (format: "Order Name - NCF: B0100000123")
            // This approach follows the same pattern as Colombia module (l10n_co_pos)

            // Extract NCF from name if present
            let ncf = false;
            if (this.name && this.name.includes(" - NCF: ")) {
                const parts = this.name.split(" - NCF: ");
                ncf = parts[1] || false;
            }

            result.l10n_do_fiscal_number = ncf;
            result.l10n_do_ncf_expiration_date = false; // Available in full invoice PDF
            result.l10n_do_document_type = ncf ? "FACTURA DE CRÉDITO FISCAL" : false;

            // Add client/partner information for the receipt
            const partner = this.get_partner();
            if (partner) {
                result.client = {
                    name: partner.name || "",
                    vat: partner.vat || "",
                    phone: partner.phone || "",
                    mobile: partner.mobile || "",
                    street: partner.street || "",
                    city: partner.city || "",
                    email: partner.email || "",
                };
            } else {
                result.client = null;
            }

            console.log("L10N_DO: Order name:", this.name);
            console.log("L10N_DO: Extracted NCF:", ncf);
            console.log("L10N_DO: Client:", result.client);
        }
        return result;
    },
    wait_for_push_order() {
        var result = super.wait_for_push_order(...arguments);
        // For Dominican orders with invoice, wait for server response to get NCF
        result = Boolean(result || (this.is_dominican_country() && this.to_invoice));
        return result;
    },
});
