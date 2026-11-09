from app.database import Base, engine
from app import models  # noqa: F401

Base.metadata.create_all(bind=engine)
print("Tablas creadas:", ", ".join(Base.metadata.tables.keys()))