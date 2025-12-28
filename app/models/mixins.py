from typing import Optional, Any, Dict, List, Type, TypeVar
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

T = TypeVar('T', bound='CRUDMixin')


class TimestampMixin:
    """
    Mixin that adds automatic timestamp tracking to models.
    
    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


class CRUDMixin:
    """
    Mixin providing common CRUD (Create, Read, Update, Delete) operations for SQLAlchemy models.
    
    This mixin should be used alongside a SQLAlchemy declarative base class.
    All methods are designed to be called on the model class itself.
    
    Example:
        class User(Base, CRUDMixin, TimestampMixin):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            name = Column(String(100))
        
        # Usage
        user = User.create(session, name="John Doe")
        user = User.get_by_id(session, 1)
    """
    
    @classmethod
    def create(cls: Type[T], session: Session, commit: bool = True, **kwargs) -> T:
        """
        Create a new instance of the model and add it to the database.
        
        Args:
            session: SQLAlchemy database session
            commit: Whether to commit the transaction immediately (default: True)
            **kwargs: Field values for the new instance
            
        Returns:
            The newly created instance
            
        Raises:
            SQLAlchemyError: If database operation fails
            
        Example:
            user = User.create(session, name="Jane", email="jane@example.com")
        """
        instance = cls(**kwargs)
        session.add(instance)
        if commit:
            session.commit()
            session.refresh(instance)
        else:
            session.flush()
        return instance
    
    @classmethod
    def get_by_id(cls: Type[T], session: Session, id: Any) -> Optional[T]:
        """
        Retrieve a single record by its primary key.
        
        Args:
            session: SQLAlchemy database session
            id: Primary key value
            
        Returns:
            Model instance if found, None otherwise
            
        Example:
            user = User.get_by_id(session, 42)
        """
        return session.get(cls, id)
    
    @classmethod
    def get_or_404(cls: Type[T], session: Session, id: Any) -> T:
        """
        Retrieve a record by ID or raise an exception if not found.
        
        Args:
            session: SQLAlchemy database session
            id: Primary key value
            
        Returns:
            Model instance
            
        Raises:
            ValueError: If record not found
        """
        instance = cls.get_by_id(session, id)
        if instance is None:
            raise ValueError(f"{cls.__name__} with id {id} not found")
        return instance
    
    @classmethod
    def filter_by(cls: Type[T], session: Session, **kwargs) -> Optional[T]:
        """
        Find the first record matching the given filters.
        
        Args:
            session: SQLAlchemy database session
            **kwargs: Field names and values to filter by
            
        Returns:
            First matching model instance, or None if no match found
            
        Example:
            user = User.filter_by(session, email="user@example.com")
        """
        return session.query(cls).filter_by(**kwargs).first()
    
    @classmethod
    def filter_all(cls: Type[T], session: Session, **kwargs) -> List[T]:
        """
        Find all records matching the given filters.
        
        Args:
            session: SQLAlchemy database session
            **kwargs: Field names and values to filter by
            
        Returns:
            List of matching model instances
            
        Example:
            active_users = User.filter_all(session, is_active=True)
        """
        return session.query(cls).filter_by(**kwargs).all()
    
    
    @classmethod
    def update(cls: Type[T], session: Session, id: Any, updates: Dict[str, Any], 
               commit: bool = True) -> Optional[T]:
        """
        Update a record with the given ID.
        
        Args:
            session: SQLAlchemy database session
            id: Primary key value of the record to update
            updates: Dictionary of field names and new values
            commit: Whether to commit the transaction immediately (default: True)
            
        Returns:
            Updated model instance if found, None otherwise
            
        Example:
            user = User.update(session, 1, {"name": "John Smith", "age": 30})
        """
        instance = cls.get_by_id(session, id)
        if instance:
            for key, value in updates.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            if commit:
                session.commit()
                session.refresh(instance)
            else:
                session.flush()
        return instance
    
    def save(self, session: Session, commit: bool = True) -> 'CRUDMixin':
        """
        Save the current instance to the database.
        
        Args:
            session: SQLAlchemy database session
            commit: Whether to commit the transaction immediately (default: True)
            
        Returns:
            Self for method chaining
            
        Example:
            user.name = "New Name"
            user.save(session)
        """
        session.add(self)
        if commit:
            session.commit()
            session.refresh(self)
        else:
            session.flush()
        return self
    
    def delete(self, session: Session, commit: bool = True) -> None:
        """
        Delete this instance from the database.
        
        Args:
            session: SQLAlchemy database session
            commit: Whether to commit the transaction immediately (default: True)
            
        Example:
            user.delete(session)
        """
        session.delete(self)
        if commit:
            session.commit()