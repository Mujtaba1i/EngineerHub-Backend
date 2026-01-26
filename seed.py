from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.environment import db_URI
from data.role_data import create_classes, create_enrollments
from data.user_data import user_list
from models.base import Base

engine = create_engine(db_URI)
SessionLocal = sessionmaker(bind=engine)

try:
    print("Recreating database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Seeding the database...")
    db = SessionLocal()

    db.add_all(user_list)
    db.commit()

    classes_list = create_classes(user_list)
    db.add_all(classes_list)
    db.commit()

    enrollments_list = create_enrollments(user_list, classes_list)
    db.add_all(enrollments_list)
    db.commit()

    db.close()

    print("Database seeding complete! 👋")
except Exception as e:
    print("An error occurred during seeding:", e)
