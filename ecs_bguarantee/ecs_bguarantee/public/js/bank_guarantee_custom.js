
frappe.ui.form.on('Bank Guarantee', {
    bg_type: function(frm) {
        if (frm.doc.bg_type == "Receiving") {
            // Automatically set Reference Document Type to "Purchase Order" and Party Type to "Supplier"
            frm.set_value('reference_doctype', 'Purchase Order');
            frm.set_value('party_type', 'Supplier');

            // Clear customer-specific fields when the type is Supplier
            frm.set_value('customer', null);
            frm.set_value('customer_group', null);
            frm.set_value('customer_address', null);

        } else if (frm.doc.bg_type == "Providing") {
            // Automatically set Reference Document Type to "Sales Order" and Party Type to "Customer"
            frm.set_value('reference_doctype', 'Sales Order');
            frm.set_value('party_type', 'Customer');

            // Fetch customer-related fields (Customer Group, Customer Address)
            if (frm.doc.customer) {
                frappe.call({
                    method: "frappe.client.get",
                    args: {
                        doctype: "Customer",
                        name: frm.doc.customer
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.set_value('customer_group', r.message.customer_group);
                            frm.set_value('customer_address', r.message.address);
                        }
                    }
                });
            }
        }
    }
});
