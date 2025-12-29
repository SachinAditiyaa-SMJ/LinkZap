from typing import Optional, Any, Dict, List, Type, TypeVar
from sqlalchemy import Column, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

T = TypeVar("T", bound="CRUDMixin")


class TimestampMixin:
    """
    Mixin that adds automatic timestamp tracking to models.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at = Column(DateTime(timezone=True),
                        default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class CRUDMixin:
    """
    Async mixin providing common CRUD (Create, Read, Update, Delete) operations for SQLAlchemy models.

    This mixin should be used alongside a SQLAlchemy declarative base class.
    All methods are designed to be called on the model class itself and use async/await.

    Example:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        class User(Base, CRUDMixin, TimestampMixin):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            name = Column(String(100))

        # Usage
        async with async_session() as session:
            user = await User.create(session, name="John Doe")
            user = await User.get_by_id(session, 1)
    """

    @classmethod
    async def create(
        cls: Type[T], session: AsyncSession, commit: bool = True, **kwargs
    ) -> T:
        """
        Create a new instance of the model and add it to the database.

        Args:
            session: SQLAlchemy async database session
            commit: Whether to commit the transaction immediately (default: True)
            **kwargs: Field values for the new instance

        Returns:
            The newly created instance

        Raises:
            SQLAlchemyError: If database operation fails

        Example:
            async with async_session() as session:
                user = await User.create(session, name="Jane", email="jane@example.com")
        """
        instance = cls(**kwargs)
        session.add(instance)
        if commit:
            await session.commit()
            await session.refresh(instance)
        else:
            await session.flush()
        return instance

    @classmethod
    async def get_by_id(cls: Type[T], session: AsyncSession, id: Any) -> Optional[T]:
        """
        Retrieve a single record by its primary key.

        Args:
            session: SQLAlchemy async database session
            id: Primary key value

        Returns:
            Model instance if found, None otherwise

        Example:
            async with async_session() as session:
                user = await User.get_by_id(session, 42)
        """
        return await session.get(cls, id)

    @classmethod
    async def get_or_404(cls: Type[T], session: AsyncSession, id: Any) -> T:
        """
        Retrieve a record by ID or raise an exception if not found.

        Args:
            session: SQLAlchemy async database session
            id: Primary key value

        Returns:
            Model instance

        Raises:
            ValueError: If record not found

        Example:
            async with async_session() as session:
                user = await User.get_or_404(session, 42)
        """
        instance = await cls.get_by_id(session, id)
        if instance is None:
            raise ValueError(f"{cls.__name__} with id {id} not found")
        return instance

    @classmethod
    async def filter_by(cls: Type[T], session: AsyncSession, **kwargs) -> Optional[T]:
        """
        Find the first record matching the given filters.

        Args:
            session: SQLAlchemy async database session
            **kwargs: Field names and values to filter by

        Returns:
            First matching model instance, or None if no match found

        Example:
            async with async_session() as session:
                user = await User.filter_by(session, email="user@example.com")
        """
        stmt = select(cls).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def filter_all(cls: Type[T], session: AsyncSession, **kwargs) -> List[T]:
        """
        Find all records matching the given filters.

        Args:
            session: SQLAlchemy async database session
            **kwargs: Field names and values to filter by

        Returns:
            List of matching model instances

        Example:
            async with async_session() as session:
                active_users = await User.filter_all(session, is_active=True)
        """
        stmt = select(cls).filter_by(**kwargs)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_all(
        cls: Type[T], session: AsyncSession, limit: Optional[int] = None
    ) -> List[T]:
        """
        Retrieve all records of this model.

        Args:
            session: SQLAlchemy async database session
            limit: Maximum number of records to return (optional)

        Returns:
            List of all model instances

        Example:
            async with async_session() as session:
                all_users = await User.get_all(session, limit=100)
        """
        stmt = select(cls)
        if limit:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def update(
        cls: Type[T],
        session: AsyncSession,
        id: Any,
        updates: Dict[str, Any],
        commit: bool = True,
    ) -> Optional[T]:
        """
        Update a record with the given ID.

        Args:
            session: SQLAlchemy async database session
            id: Primary key value of the record to update
            updates: Dictionary of field names and new values
            commit: Whether to commit the transaction immediately (default: True)

        Returns:
            Updated model instance if found, None otherwise

        Example:
            async with async_session() as session:
                user = await User.update(session, 1, {"name": "John Smith", "age": 30})
        """
        instance = await cls.get_by_id(session, id)
        if instance:
            for key, value in updates.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            if commit:
                await session.commit()
                await session.refresh(instance)
            else:
                await session.flush()
        return instance

    async def save(self, session: AsyncSession, commit: bool = True) -> "CRUDMixin":
        """
        Save the current instance to the database.

        Args:
            session: SQLAlchemy async database session
            commit: Whether to commit the transaction immediately (default: True)

        Returns:
            Self for method chaining

        Example:
            async with async_session() as session:
                user.name = "New Name"
                await user.save(session)
        """
        session.add(self)
        if commit:
            await session.commit()
            await session.refresh(self)
        else:
            await session.flush()
        return self

    async def delete(self, session: AsyncSession, commit: bool = True) -> None:
        """
        Delete this instance from the database.

        Args:
            session: SQLAlchemy async database session
            commit: Whether to commit the transaction immediately (default: True)

        Example:
            async with async_session() as session:
                await user.delete(session)
        """
        await session.delete(self)
        if commit:
            await session.commit()

    @classmethod
    async def bulk_create(
        cls: Type[T],
        session: AsyncSession,
        items: List[Dict[str, Any]],
        commit: bool = True,
    ) -> List[T]:
        """
        Create multiple records efficiently.

        Args:
            session: SQLAlchemy async database session
            items: List of dictionaries containing field values
            commit: Whether to commit the transaction immediately (default: True)

        Returns:
            List of created instances

        Example:
            async with async_session() as session:
                users = await User.bulk_create(session, [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"}
                ])
        """
        instances = [cls(**item) for item in items]
        session.add_all(instances)
        if commit:
            await session.commit()
            for instance in instances:
                await session.refresh(instance)
        else:
            await session.flush()
        return instances

    @classmethod
    async def count(cls: Type[T], session: AsyncSession, **kwargs) -> int:
        """
        Count records matching the given filters.

        Args:
            session: SQLAlchemy async database session
            **kwargs: Field names and values to filter by

        Returns:
            Number of matching records

        Example:
            async with async_session() as session:
                count = await User.count(session, is_active=True)
        """
        from sqlalchemy import func as sql_func

        stmt = select(sql_func.count()).select_from(cls).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def exists(cls: Type[T], session: AsyncSession, **kwargs) -> bool:
        """
        Check if any records exist matching the given filters.

        Args:
            session: SQLAlchemy async database session
            **kwargs: Field names and values to filter by

        Returns:
            True if at least one matching record exists, False otherwise

        Example:
            async with async_session() as session:
                exists = await User.exists(session, email="user@example.com")
        """
        from sqlalchemy import exists as sql_exists

        stmt = select(
            sql_exists().where(
                *[getattr(cls, k) == v for k, v in kwargs.items()])
        )
        result = await session.execute(stmt)
        return result.scalar()

    @classmethod
    async def delete_by_id(
        cls: Type[T], session: AsyncSession, id: Any, commit: bool = True
    ) -> bool:
        """
        Delete a record by its ID.

        Args:
            session: SQLAlchemy async database session
            id: Primary key value of the record to delete
            commit: Whether to commit the transaction immediately (default: True)

        Returns:
            True if record was deleted, False if not found

        Example:
            async with async_session() as session:
                deleted = await User.delete_by_id(session, 42)
        """
        instance = await cls.get_by_id(session, id)
        if instance:
            await instance.delete(session, commit=commit)
            return True
        return False
