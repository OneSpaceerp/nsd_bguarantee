// Copyright (c) 2026, Nest Software Development and contributors
// For license information, please see license.txt

frappe.query_reports["Bank Guarantee Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "80"
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "80"
		},
		{
			fieldname: "bank_guarantee_purpose",
			label: __("Purpose"),
			fieldtype: "Select",
			options: "\nBank Guarantee\nCheque\nCash\nDeduction"
		},
		{
			fieldname: "bg_type",
			label: __("Type"),
			fieldtype: "Select",
			options: ["Receiving", "Providing"],
			default: "Providing"
		},
		{
			fieldname: "status_of_letter_of_guarantee",
			label: __("Category"),
			fieldtype: "Select",
			options: "\nInitial\nAdvanced Payment\nFinal"
		},
		{
			fieldname: "bank",
			label: __("Bank"),
			fieldtype: "Link",
			options: "Bank"
		}
	],

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		const today = frappe.datetime.nowdate();

		if (column.fieldname === "new_date" && data && data.new_date) {
			const diff = frappe.datetime.get_diff(data.new_date, today);
			if (diff <= 15 && diff >= 0) {
				value = `<span style="color:red;font-weight:bold;">${value}</span>`;
			}
		}

		if (column.fieldname === "end_date" && data && data.end_date) {
			const diff = frappe.datetime.get_diff(data.end_date, today);
			if (diff <= 15 && diff >= 0) {
				value = `<span style="color:red;font-weight:bold;">${value}</span>`;
			}
		}

		return value;
	}
};
