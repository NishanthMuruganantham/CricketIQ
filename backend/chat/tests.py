from django.test import TestCase
from chat.services import schema_service


class SchemaServiceTest(TestCase):
    def test_get_schema_structure(self):
        """Test that get_schema returns the correct structure."""
        # Reset cache so we test fresh
        schema_service._SCHEMA_CACHE = None

        schema = schema_service.get_schema()

        # Check top level keys
        self.assertIn("deliverywise", schema)
        self.assertIn("matchwise", schema)

        # Check deliverywise structure
        dw = schema["deliverywise"]
        self.assertIn("description", dw)
        self.assertIn("fields", dw)
        self.assertIsInstance(dw["fields"], list)
        self.assertIn("batter", dw["fields"])
        self.assertIn("bowler", dw["fields"])

        # Check matchwise structure
        mw = schema["matchwise"]
        self.assertIn("description", mw)
        self.assertIn("fields", mw)
        self.assertIsInstance(mw["fields"], list)
        self.assertIn("winner", mw["fields"])
        self.assertIn("match_id", mw["fields"])

    def test_schema_caching(self):
        """Test that schema is cached after first call."""
        # Reset cache for this test
        schema_service._SCHEMA_CACHE = None

        # First call
        schema1 = schema_service.get_schema()

        # Second call
        schema2 = schema_service.get_schema()

        # Should be the same cached object
        self.assertIs(schema1, schema2)
