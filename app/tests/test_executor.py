import pytest
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.sqlite_executor import SQLiteExecutor

@pytest.fixture
def temp_db():
    db_path = "test_temp.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE test (id INTEGER, val TEXT)")
    conn.execute("INSERT INTO test VALUES (1, 'hello')")
    conn.commit()
    conn.close()
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

def test_safe_execution(temp_db):
    executor = SQLiteExecutor(temp_db)
    result = executor.execute("SELECT * FROM test")
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["val"] == "hello"

def test_read_only_enforcement(temp_db):
    executor = SQLiteExecutor(temp_db)
    # This should fail due to the authorizer or URI mode
    result = executor.execute("INSERT INTO test VALUES (2, 'world')")
    assert result["success"] is False
    assert "not authorized" in result["error"].lower() or "read-only" in result["error"].lower()

def test_row_cap(temp_db):
    conn = sqlite3.connect(temp_db)
    for i in range(10):
        conn.execute("INSERT INTO test VALUES (?, ?)", (i, f"val{i}"))
    conn.commit()
    conn.close()
    
    executor = SQLiteExecutor(temp_db, row_cap=5)
    result = executor.execute("SELECT * FROM test")
    assert result["row_count"] == 5
    assert result["has_more"] is True
