import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.sql_validator import SQLValidator

@pytest.fixture
def validator():
    return SQLValidator(allowed_tables={"customers", "orders", "products"})

def test_valid_select(validator):
    sql = "SELECT name FROM customers LIMIT 10;"
    is_valid, error = validator.validate(sql)
    assert is_valid is True
    assert error is None

def test_forbidden_command(validator):
    sql = "DELETE FROM customers;"
    is_valid, error = validator.validate(sql)
    assert is_valid is False
    assert "Forbidden" in error

def test_multiple_statements(validator):
    sql = "SELECT * FROM orders; DROP TABLE customers;"
    is_valid, error = validator.validate(sql)
    assert is_valid is False
    assert "Only one" in error

def test_disallowed_table(validator):
    sql = "SELECT * FROM secret_table;"
    is_valid, error = validator.validate(sql)
    assert is_valid is False
    assert "not in the allowed schema" in error

def test_comments_disallowed(validator):
    sql = "SELECT * FROM orders; -- get everything"
    is_valid, error = validator.validate(sql)
    assert is_valid is False
    assert "Comments are not allowed" in error
