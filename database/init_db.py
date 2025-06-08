import database.models  # noqa: F401  ensure model classes are registered
from database.schema import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
