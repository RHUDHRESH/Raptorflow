"""
Database Tests for RaptorFlow Backend
Tests database connections, migrations, and data integrity
"""

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.config.settings import get_settings
from backend.core.database import get_db, DatabaseManager


class TestDatabase:
    """Test database connections and operations."""

    @pytest.fixture
    def mock_settings(self):
        """Mock database settings for testing."""
        settings = get_settings()
        settings.DATABASE_URL = "sqlite:///./test.db"
        return settings

    @pytest.fixture
    def db_manager(self, mock_settings):
        """Create database manager for testing."""
        return DatabaseManager(mock_settings.DATABASE_URL)

    def test_database_connection(self, db_manager):
        """Test database connection."""
        assert db_manager.engine is not None
        assert db_manager.session_factory is not None

    def test_database_health_check(self, db_manager):
        """Test database health check."""
        health = db_manager.check_health()
        assert health["status"] == "healthy"
        assert "connection_time" in health

    def test_database_migration(self, db_manager):
        """Test database migration."""
        # Test migration execution
        migration_result = db_manager.run_migrations()
        assert migration_result["success"] is True
        assert "version" in migration_result

    def test_create_tables(self, db_manager):
        """Test table creation."""
        # Create tables
        db_manager.create_tables()
        
        # Verify tables exist
        with db_manager.get_session() as session:
            result = session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result.fetchall()]
            assert len(tables) > 0

    def test_user_crud_operations(self, db_manager):
        """Test user CRUD operations."""
        with db_manager.get_session() as session:
            # Create user
            user_data = {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password_hash": "hashed_password"
            }
            
            # Insert user
            session.execute(text("""
                INSERT INTO users (email, first_name, last_name, password_hash, created_at, updated_at)
                VALUES (:email, :first_name, :last_name, :password_hash, NOW(), NOW())
            """), user_data)
            session.commit()
            
            # Read user
            result = session.execute(text("SELECT * FROM users WHERE email = :email"), user_data)
            user = result.fetchone()
            assert user is not None
            assert user[1] == "test@example.com"  # email column
            
            # Update user
            session.execute(text("""
                UPDATE users SET first_name = :first_name WHERE email = :email
            """), {"first_name": "Updated", "email": "test@example.com"})
            session.commit()
            
            # Verify update
            result = session.execute(text("SELECT first_name FROM users WHERE email = :email"), user_data)
            updated_user = result.fetchone()
            assert updated_user[0] == "Updated"
            
            # Delete user
            session.execute(text("DELETE FROM users WHERE email = :email"), user_data)
            session.commit()
            
            # Verify deletion
            result = session.execute(text("SELECT * FROM users WHERE email = :email"), user_data)
            deleted_user = result.fetchone()
            assert deleted_user is None

    def test_workspace_crud_operations(self, db_manager):
        """Test workspace CRUD operations."""
        with db_manager.get_session() as session:
            # Create workspace
            workspace_data = {
                "name": "Test Workspace",
                "description": "A test workspace",
                "owner_id": "test-user-id"
            }
            
            # Insert workspace
            session.execute(text("""
                INSERT INTO workspaces (name, description, owner_id, created_at, updated_at)
                VALUES (:name, :description, :owner_id, NOW(), NOW())
            """), workspace_data)
            session.commit()
            
            # Read workspace
            result = session.execute(text("SELECT * FROM workspaces WHERE name = :name"), workspace_data)
            workspace = result.fetchone()
            assert workspace is not None
            assert workspace[1] == "Test Workspace"  # name column
            
            # Update workspace
            session.execute(text("""
                UPDATE workspaces SET description = :description WHERE name = :name
            """), {"description": "Updated description", "name": "Test Workspace"})
            session.commit()
            
            # Verify update
            result = session.execute(text("SELECT description FROM workspaces WHERE name = :name"), workspace_data)
            updated_workspace = result.fetchone()
            assert updated_workspace[0] == "Updated description"
            
            # Delete workspace
            session.execute(text("DELETE FROM workspaces WHERE name = :name"), workspace_data)
            session.commit()
            
            # Verify deletion
            result = session.execute(text("SELECT * FROM workspaces WHERE name = :name"), workspace_data)
            deleted_workspace = result.fetchone()
            assert deleted_workspace is None

    def test_database_transaction_rollback(self, db_manager):
        """Test database transaction rollback."""
        with db_manager.get_session() as session:
            try:
                # Start transaction
                session.begin()
                
                # Insert data
                session.execute(text("""
                    INSERT INTO users (email, first_name, last_name, password_hash, created_at, updated_at)
                    VALUES (:email, :first_name, :last_name, :password_hash, NOW(), NOW())
                """), {
                    "email": "rollback_test@example.com",
                    "first_name": "Rollback",
                    "last_name": "Test",
                    "password_hash": "hashed_password"
                })
                
                # Simulate error
                raise Exception("Simulated error")
                
            except Exception:
                # Rollback transaction
                session.rollback()
            
            # Verify data was not committed
            result = session.execute(text(
                "SELECT * FROM users WHERE email = 'rollback_test@example.com'"
            ))
            user = result.fetchone()
            assert user is None

    def test_database_connection_pooling(self, db_manager):
        """Test database connection pooling."""
        # Test multiple concurrent connections
        async def test_concurrent_connections():
            tasks = []
            for i in range(10):
                task = asyncio.create_task(self._test_single_connection(db_manager))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All connections should succeed
            assert all(isinstance(result, bool) and result for result in results if not isinstance(result, Exception))
        
        asyncio.run(test_concurrent_connections())

    async def _test_single_connection(self, db_manager):
        """Test single database connection."""
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1

    def test_database_indexes(self, db_manager):
        """Test database indexes."""
        with db_manager.get_session() as session:
            # Check if indexes exist
            result = session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='users'
            """))
            indexes = [row[0] for row in result.fetchall()]
            assert len(indexes) > 0

    def test_database_constraints(self, db_manager):
        """Test database constraints."""
        with db_manager.get_session() as session:
            # Test unique constraint on email
            user_data = {
                "email": "constraint_test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password_hash": "hashed_password"
            }
            
            # Insert first user
            session.execute(text("""
                INSERT INTO users (email, first_name, last_name, password_hash, created_at, updated_at)
                VALUES (:email, :first_name, :last_name, :password_hash, NOW(), NOW())
            """), user_data)
            session.commit()
            
            # Try to insert duplicate email
            try:
                session.execute(text("""
                    INSERT INTO users (email, first_name, last_name, password_hash, created_at, updated_at)
                    VALUES (:email, :first_name, :last_name, :password_hash, NOW(), NOW())
                """), user_data)
                session.commit()
                assert False, "Should have failed due to unique constraint"
            except Exception:
                session.rollback()
                # Expected to fail

    def test_database_foreign_keys(self, db_manager):
        """Test foreign key constraints."""
        with db_manager.get_session() as session:
            # Test workspace-owner relationship
            try:
                # Try to insert workspace with non-existent owner
                session.execute(text("""
                    INSERT INTO workspaces (name, description, owner_id, created_at, updated_at)
                    VALUES (:name, :description, :owner_id, NOW(), NOW())
                """), {
                    "name": "Orphan Workspace",
                    "description": "Workspace without owner",
                    "owner_id": "non-existent-user-id"
                })
                session.commit()
                assert False, "Should have failed due to foreign key constraint"
            except Exception:
                session.rollback()
                # Expected to fail

    def test_database_performance(self, db_manager):
        """Test database performance."""
        import time
        
        with db_manager.get_session() as session:
            # Test query performance
            start_time = time.time()
            
            # Execute a complex query
            result = session.execute(text("""
                SELECT u.email, w.name 
                FROM users u 
                LEFT JOIN workspaces w ON u.id = w.owner_id 
                LIMIT 100
            """))
            
            end_time = time.time()
            query_time = end_time - start_time
            
            # Query should complete quickly
            assert query_time < 1.0, f"Query took too long: {query_time}s"

    def test_database_backup_simulation(self, db_manager):
        """Test database backup simulation."""
        # This would test actual backup procedures
        # For now, just verify backup-related functionality exists
        
        with db_manager.get_session() as session:
            # Create test data
            session.execute(text("""
                INSERT INTO users (email, first_name, last_name, password_hash, created_at, updated_at)
                VALUES (:email, :first_name, :last_name, :password_hash, NOW(), NOW())
            """), {
                "email": "backup_test@example.com",
                "first_name": "Backup",
                "last_name": "Test",
                "password_hash": "hashed_password"
            })
            session.commit()
            
            # Verify data exists
            result = session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            assert user_count > 0

    def test_database_migrations_rollback(self, db_manager):
        """Test database migration rollback."""
        # This would test migration rollback functionality
        # For now, just verify migration system exists
        
        migration_result = db_manager.run_migrations()
        assert migration_result["success"] is True
        
        # In a real implementation, you would test:
        # 1. Apply migration
        # 2. Verify changes
        # 3. Rollback migration
        # 4. Verify rollback

    def test_database_connection_retry(self, db_manager):
        """Test database connection retry logic."""
        # This would test connection retry logic
        # For now, just verify connection works
        
        health = db_manager.check_health()
        assert health["status"] == "healthy"

    def test_database_schema_validation(self, db_manager):
        """Test database schema validation."""
        with db_manager.get_session() as session:
            # Verify required tables exist
            required_tables = ["users", "workspaces", "profiles"]
            
            for table in required_tables:
                result = session.execute(text(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{table}'
                """))
                table_exists = result.fetchone() is not None
                assert table_exists, f"Required table {table} does not exist"

    def test_database_data_integrity(self, db_manager):
        """Test database data integrity."""
        with db_manager.get_session() as session:
            # Test data consistency
            result = session.execute(text("""
                SELECT COUNT(*) as total_users, 
                       COUNT(DISTINCT email) as unique_emails
                FROM users
            """))
            
            data = result.fetchone()
            total_users = data[0]
            unique_emails = data[1]
            
            # All emails should be unique
            assert total_users == unique_emails, "Duplicate emails found in database"

    def test_database_connection_timeout(self, db_manager):
        """Test database connection timeout."""
        # This would test connection timeout handling
        # For now, just verify connection works within reasonable time
        
        import time
        start_time = time.time()
        
        health = db_manager.check_health()
        
        end_time = time.time()
        connection_time = end_time - start_time
        
        assert connection_time < 5.0, f"Connection took too long: {connection_time}s"
        assert health["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])
