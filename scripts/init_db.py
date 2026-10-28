from shared.database import Base, engine
from shared import models

Base.metadata.create_all(bind=engine)

print("Database tables created.")
