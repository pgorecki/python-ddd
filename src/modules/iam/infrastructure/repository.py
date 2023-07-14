import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.schema import Column

from modules.iam.application.repository import UserRepository
from modules.iam.application.services import User
from seedwork.domain.value_objects import Email
from seedwork.infrastructure.database import Base
from seedwork.infrastructure.json_data_mapper import JSONDataMapper
from seedwork.infrastructure.repository import SqlAlchemyGenericRepository


class UserModel(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
    access_token = Column(String(255), unique=True, nullable=False)
    is_superuser = Column(Boolean(), nullable=False)


class UserDataMapper(JSONDataMapper):
    def model_to_entity(self, instance: UserModel) -> User:
        return User(
            id=instance.id,
            email=instance.email,
            password_hash=instance.password,
            access_token=instance.access_token,
            is_superuser=instance.is_superuser,
        )

    def entity_to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            password=entity.password_hash,
            access_token=entity.access_token,
            is_superuser=entity.is_superuser,
        )


class PostgresJsonUserRepository(SqlAlchemyGenericRepository, UserRepository):
    """Listing repository implementation"""

    mapper_class = UserDataMapper
    model_class = UserModel

    def get_by_access_token(self, access_token: str) -> User | None:
        try:
            instance = (
                self._session.query(UserModel)
                .filter_by(access_token=access_token)
                .one()
            )
            return self._get_entity(instance)
        except NoResultFound:
            return None

    def get_by_email(self, email: Email) -> User | None:
        try:
            instance = self._session.query(UserModel).filter_by(email=email).one()
            return self._get_entity(instance)
        except NoResultFound:
            return None
