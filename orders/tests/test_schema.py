from django.test import TestCase
from drf_spectacular.generators import SchemaGenerator


class OrderSchemaTests(TestCase):
    def test_order_and_customer_lists_document_pagination_parameters(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)

        self._assert_pagination_parameters(
            schema["paths"]["/api/orders/list/"]["get"]["parameters"]
        )
        self._assert_pagination_parameters(
            schema["paths"]["/api/orders/customers/list/"]["get"]["parameters"]
        )

    def _assert_pagination_parameters(self, parameters):
        parameter_names = {parameter["name"] for parameter in parameters}

        self.assertIn("page", parameter_names)
        self.assertIn("page_size", parameter_names)

        page_size_parameter = next(
            parameter for parameter in parameters if parameter["name"] == "page_size"
        )

        self.assertEqual(page_size_parameter["schema"]["default"], 2)

    def test_order_types_endpoint_is_documented(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)

        operation = schema["paths"]["/api/orders/types/"]["get"]

        self.assertEqual(operation["summary"], "List order types")
        self.assertIn("Arabic labels", operation["description"])
        self.assertIn("application/json", operation["responses"]["200"]["content"])

        examples = operation["responses"]["200"]["content"]["application/json"][
            "examples"
        ]

        self.assertIn("DeliveryOrderType", examples)
        self.assertEqual(examples["DeliveryOrderType"]["value"][0]["value"], "delivery")
