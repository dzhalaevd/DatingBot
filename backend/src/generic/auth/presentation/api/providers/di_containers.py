from dependency_injector import (
    containers,
    providers,
)

from src.application.services import (
    AuthService,
    CompositeNotifier,
    PhotoService,
    RoleService,
    S3Storage,
    UserService,
)
from src.application.services.profile import (
    ProfileService,
)
from src.infrastructure.database import (
    DBConnector,
    JTIRedisStorage,
    RedisConnector,
)
from src.infrastructure.database.repositories import (
    AuthRepository,
    PhotoRepository,
    ProfileRepository,
    RoleRepository,
    UserRepository,
)
from src.shared import (
    load_config,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.presentation.api.controllers.user",
            "src.presentation.api.controllers.auth",
            "src.presentation.api.controllers.healthcheck",
            "src.presentation.api.controllers.role",
            "src.presentation.api.controllers.profile",
            "src.presentation.api.controllers.photo"
        ]
    )

    config = providers.Singleton(load_config)()
    db = providers.Singleton(DBConnector, db_url=config.db.construct_sqlalchemy_url())
    session = db.provided.get_db_session
    redis = providers.Singleton(RedisConnector, url=config.db.construct_redis_dsn())
    s3 = providers.Singleton(
        S3Storage,
        service_name=config.s3.service_name,
        aws_access_key_id=config.s3.aws_access_key_id,
        aws_secret_access_key=config.s3.aws_secret_access_key,
        endpoint_url=config.s3.endpoint_url,
        region_name=config.s3.region_name,
        bucket_name=config.s3.bucket_name
    )

    blacklist_service = providers.Factory(
        JTIRedisStorage,
        redis_connector=redis,
    )
    user_repository = providers.Factory(
        UserRepository,
        session_factory=session,
    )
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    role_repository = providers.Factory(
        RoleRepository,
        session_factory=session,
    )
    role_service = providers.Factory(
        RoleService,
        role_repository=role_repository,
    )
    notifier = providers.Factory(
        CompositeNotifier,
    )
    auth_repository = providers.Factory(
        AuthRepository,
        session_factory=session,
    )
    auth_service = providers.Factory(
        AuthService,
        auth_repository=auth_repository,
        role_service=role_service,
        notifier=notifier
    )
    profile_repository = providers.Factory(
        ProfileRepository,
        session_factory=session
    )
    profile_service = providers.Factory(
        ProfileService,
        profile_repository=profile_repository,
    )
    photo_repository = providers.Factory(
        PhotoRepository,
        session_factory=session,
    )
    photo_service = providers.Factory(
        PhotoService,
        s3=s3,
        photo_repository=photo_repository
    )
