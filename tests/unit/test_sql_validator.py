import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sqlify.validation.sql_validator import validate_sql

class TestSQLValidator(unittest.TestCase):
    def test_valid_select(self):
        result = validate_sql("SELECT * FROM users;")
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['cleaned_sql'], "SELECT * FROM users;")

    def test_valid_with(self):
        result = validate_sql("WITH temp AS (SELECT 1) SELECT * FROM temp;")
        self.assertTrue(result['is_valid'])

    def test_blocked_keyword(self):
        result = validate_sql("DROP TABLE users;")
        self.assertFalse(result['is_valid'])
        self.assertIn("Blocked keyword", result['error_message'])

    def test_multiple_statements(self):
        result = validate_sql("SELECT * FROM users; DROP TABLE users;")
        self.assertFalse(result['is_valid'])
        self.assertIn("Multiple SQL statements", result['error_message'])

    def test_comments_blocked(self):
        result = validate_sql("SELECT * FROM users -- comment")
        self.assertFalse(result['is_valid'])
        self.assertIn("Comments are not allowed", result['error_message'])

if __name__ == '__main__':
    unittest.main()
