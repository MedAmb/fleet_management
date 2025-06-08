from database.schema import engine, Base
import database.models  # noqa: F401  ensure model classes are registered


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
