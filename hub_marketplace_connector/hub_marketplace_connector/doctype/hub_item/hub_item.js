// Copyright (c) 2024, pwctech technologies private limited and contributors
// For license information, please see license.txt

function set_sub_category_field() {
	cur_frm.set_value('sub_category', null).then(() => {
		const sub_category_field = cur_frm.get_field("sub_category")
		const hub_categories_data = frappe.boot.hub_categories_response
		const selected_category = hub_categories_data.find(cat => cat.name === cur_frm.doc.category);
		if (selected_category.sub_category && selected_category.sub_category.length > 0) {
			const sub_categories = selected_category.sub_category.map(subcat => subcat.name).sort((a, b) => a.localeCompare(b));
			cur_frm.set_df_property('sub_category', 'hidden', 0)
			cur_frm.set_df_property('sub_category', 'reqd', 1)
			sub_category_field.set_data(sub_categories)
		}
		else {
			cur_frm.set_df_property('sub_category', 'hidden', 1)
			cur_frm.set_df_property('sub_category', 'reqd', 0)
		}
	})
}
frappe.ui.form.on('Hub Item', {
	refresh: function(frm) {
		if (frm.is_new() || !frm.doc.mapped_warehouse.length) {
			frm.events.set_warehouse(frm);
		};
		if (frm.doc.sub_category){
			frm.set_df_property('sub_category', 'hidden', 0),
			frm.events.set_additional_attributes_and_variant_df(frm)
		};
		frm.events.set_hub_categories(frm);
	},
	category: function (frm) {
		set_sub_category_field()
	},
	sub_category: function (frm) {
		if (frm.doc.sub_category) {
			frm.events.set_additional_attributes_and_variant_df(frm);
			return frm.call({
				doc: frm.doc,
				method: "set_variant_details"
			});
		}
	},
	enable_variants: function (frm) {
		frm.events.set_additional_attributes_and_variant_df(frm);
	},
	copy_from_hub_item_attributes: (frm) => {
		return frm.call({
			doc: frm.doc,
			method: "copy_hub_item_attributes"
		});
	},
	set_hub_categories: (frm) => {
		const category_field = frm.get_field("category")
		category_field.set_data(frappe.boot.hub_categories)
	},
	set_warehouse: (frm) => {
		return frm.call({
			doc: frm.doc,
			method: "set_warehouse"
		});
	},
	set_additional_attributes_and_variant_df: (frm) => {
		frm.call({
			doc: frm.doc,
			method: 'get_sub_category',
			callback: (r) => {
				if (r.message && r.message.additional_attributes.length) {
					frm.set_df_property('additional_specifications', 'hidden', 0)
					if (frm.doc.variant_of && frm.doc.enable_variants){
						frm.set_df_property('item_variants', 'hidden', 0)
					}
					else {
						frm.set_df_property('item_variants', 'hidden', 1)
					}
				}
				else {
					frm.set_df_property('additional_specifications', 'hidden', 1)
					frm.set_df_property('item_variants', 'hidden', 1)
				}
			}
		})
	}
});
