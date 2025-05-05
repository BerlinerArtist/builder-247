"""
Unit tests for Transaction Data Access Layer
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction import Transaction, TransactionDAO, TransactionStatus, Base
from prometheus_swarm.database.database import SessionLocal

@pytest.fixture(scope='function')
def test_session():
    """
    Create a test database session for each test function
    """
    # Use an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    # Override the default session with our test session
    original_session = SessionLocal
    SessionLocal.configure(bind=engine)
    
    try:
        yield TestingSessionLocal()
    finally:
        # Restore the original session
        SessionLocal.configure(bind=original_session)
        Base.metadata.drop_all(engine)

def test_create_transaction(test_session):
    """Test creating a valid transaction"""
    transaction = TransactionDAO.create_transaction(100.50, "Test transaction")
    
    assert transaction is not None
    assert transaction.amount == 100.50
    assert transaction.description == "Test transaction"
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.id is not None

def test_create_transaction_invalid_amount():
    """Test creating a transaction with invalid amount"""
    with pytest.raises(ValueError, match="Transaction amount must be positive"):
        TransactionDAO.create_transaction(-50)
    
    with pytest.raises(ValueError, match="Transaction amount must be positive"):
        TransactionDAO.create_transaction(0)

def test_get_transaction(test_session):
    """Test retrieving an existing transaction"""
    transaction = TransactionDAO.create_transaction(200.75, "Retrieval test")
    
    retrieved_transaction = TransactionDAO.get_transaction(transaction.id)
    
    assert retrieved_transaction is not None
    assert retrieved_transaction.id == transaction.id
    assert retrieved_transaction.amount == 200.75

def test_get_nonexistent_transaction():
    """Test retrieving a non-existent transaction"""
    transaction = TransactionDAO.get_transaction("non-existent-id")
    
    assert transaction is None

def test_update_transaction_status(test_session):
    """Test updating transaction status"""
    transaction = TransactionDAO.create_transaction(150.25, "Status update test")
    
    updated_transaction = TransactionDAO.update_transaction_status(
        transaction.id, 
        TransactionStatus.COMPLETED
    )
    
    assert updated_transaction is not None
    assert updated_transaction.status == TransactionStatus.COMPLETED

def test_update_nonexistent_transaction_status():
    """Test updating status of a non-existent transaction"""
    updated_transaction = TransactionDAO.update_transaction_status(
        "non-existent-id", 
        TransactionStatus.COMPLETED
    )
    
    assert updated_transaction is None

def test_list_transactions(test_session):
    """Test listing transactions with optional filtering"""
    # Create multiple transactions
    TransactionDAO.create_transaction(50.00, "Transaction 1")
    TransactionDAO.create_transaction(75.50, "Transaction 2")
    
    # Update one transaction status
    first_transaction = TransactionDAO.get_transaction(
        TransactionDAO.create_transaction(100.00, "Transaction 3").id
    )
    TransactionDAO.update_transaction_status(first_transaction.id, TransactionStatus.COMPLETED)
    
    # List all transactions
    all_transactions = TransactionDAO.list_transactions()
    assert len(all_transactions) == 3
    
    # List completed transactions
    completed_transactions = TransactionDAO.list_transactions(status=TransactionStatus.COMPLETED)
    assert len(completed_transactions) == 1
    assert completed_transactions[0].status == TransactionStatus.COMPLETED

def test_delete_transaction(test_session):
    """Test deleting a transaction"""
    transaction = TransactionDAO.create_transaction(300.00, "Deletion test")
    
    # Delete the transaction
    delete_result = TransactionDAO.delete_transaction(transaction.id)
    
    assert delete_result is True
    
    # Verify transaction is deleted
    deleted_transaction = TransactionDAO.get_transaction(transaction.id)
    assert deleted_transaction is None

def test_delete_nonexistent_transaction():
    """Test deleting a non-existent transaction"""
    delete_result = TransactionDAO.delete_transaction("non-existent-id")
    
    assert delete_result is False