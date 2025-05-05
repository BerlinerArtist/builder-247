"""
Data Access Layer for Transaction Tracking

This module provides a comprehensive data access layer for managing transactions
with robust error handling and validation.
"""

from typing import Dict, List, Optional, Union
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import enum
import uuid

from .database import Base, SessionLocal, engine

class TransactionStatus(enum.Enum):
    """Enum representing possible transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(Base):
    """
    SQLAlchemy model representing a transaction.
    
    Attributes:
        id (str): Unique identifier for the transaction
        amount (float): Transaction amount
        status (TransactionStatus): Current status of the transaction
        created_at (datetime): Timestamp of transaction creation
        updated_at (datetime): Timestamp of last transaction update
        description (str, optional): Optional description of the transaction
    """
    __tablename__ = 'transactions'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(String, nullable=True)

class TransactionDAO:
    """
    Data Access Object for Transaction management.
    Provides methods for creating, reading, updating, and deleting transactions.
    """

    @staticmethod
    def create_transaction(amount: float, description: Optional[str] = None) -> Transaction:
        """
        Create a new transaction.

        Args:
            amount (float): Transaction amount
            description (Optional[str]): Optional transaction description

        Returns:
            Transaction: The created transaction object

        Raises:
            ValueError: If amount is not positive
            SQLAlchemyError: If database operation fails
        """
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")

        transaction = Transaction(
            amount=amount,
            description=description,
            status=TransactionStatus.PENDING
        )

        try:
            with SessionLocal() as session:
                session.add(transaction)
                session.commit()
                session.refresh(transaction)
                return transaction
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to create transaction: {str(e)}") from e

    @staticmethod
    def get_transaction(transaction_id: str) -> Optional[Transaction]:
        """
        Retrieve a transaction by its ID.

        Args:
            transaction_id (str): Unique identifier of the transaction

        Returns:
            Optional[Transaction]: Transaction if found, None otherwise

        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with SessionLocal() as session:
                return session.query(Transaction).filter(Transaction.id == transaction_id).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to retrieve transaction: {str(e)}") from e

    @staticmethod
    def update_transaction_status(transaction_id: str, status: TransactionStatus) -> Optional[Transaction]:
        """
        Update the status of a transaction.

        Args:
            transaction_id (str): Unique identifier of the transaction
            status (TransactionStatus): New status for the transaction

        Returns:
            Optional[Transaction]: Updated transaction, None if not found

        Raises:
            SQLAlchemyError: If database update fails
        """
        try:
            with SessionLocal() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if transaction:
                    transaction.status = status
                    session.commit()
                    session.refresh(transaction)
                    return transaction
                return None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to update transaction status: {str(e)}") from e

    @staticmethod
    def list_transactions(status: Optional[TransactionStatus] = None, limit: int = 100) -> List[Transaction]:
        """
        List transactions with optional filtering.

        Args:
            status (Optional[TransactionStatus]): Optional status filter
            limit (int): Maximum number of transactions to return

        Returns:
            List[Transaction]: List of transactions matching the criteria

        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with SessionLocal() as session:
                query = session.query(Transaction)
                if status:
                    query = query.filter(Transaction.status == status)
                return query.limit(limit).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to list transactions: {str(e)}") from e

    @staticmethod
    def delete_transaction(transaction_id: str) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id (str): Unique identifier of the transaction

        Returns:
            bool: True if transaction was deleted, False if not found

        Raises:
            SQLAlchemyError: If database deletion fails
        """
        try:
            with SessionLocal() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if transaction:
                    session.delete(transaction)
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to delete transaction: {str(e)}") from e

# Ensure tables are created
Base.metadata.create_all(bind=engine)