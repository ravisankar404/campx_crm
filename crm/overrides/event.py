from frappe.desk.doctype.event.event import Event


class CustomEvent(Event):
	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Subject",
				"type": "Data",
				"key": "subject",
				"width": "18rem",
			},
			{
				"label": "Type",
				"type": "Data",
				"key": "event_type",
				"width": "8rem",
			},
			{
				"label": "Status",
				"type": "Select",
				"key": "status",
				"width": "10rem",
			},
			{
				"label": "Starts On",
				"type": "Datetime",
				"key": "starts_on",
				"width": "12rem",
			},
		]
		rows = [
			"name",
			"subject",
			"status",
			"starts_on",
			"ends_on",
			"event_type",
			"reference_doctype",
			"reference_docname",
		]
		return {"columns": columns, "rows": rows}
