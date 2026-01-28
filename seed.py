from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.environment import db_URI
from data.role_data import create_classes, create_enrollments
from data.user_data import user_list
from data.announcement_data import create_announcements
from models.base import Base
from data.graduate_project_data import create_graduate_projects


engine = create_engine(db_URI)
SessionLocal = sessionmaker(bind=engine)

try:
    print("Recreating database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Seeding the database...")
    db = SessionLocal()

    # Seed users
    print("✓ Seeding users...")
    db.add_all(user_list)
    db.commit()

    # Seed graduate projects
    print("✓ Seeding graduate projects...")
    graduate_projects = create_graduate_projects(user_list)
    db.add_all(graduate_projects)
    db.commit()

    # Seed classes
    print("✓ Seeding classes...")
    classes_list = create_classes(user_list)
    db.add_all(classes_list)
    db.commit()

    # Seed enrollments
    print("✓ Seeding enrollments...")
    enrollments_list = create_enrollments(user_list, classes_list)
    db.add_all(enrollments_list)
    db.commit()

    # Seed announcements
    print("✓ Seeding announcements...")
    announcements_list = create_announcements(classes_list)
    db.add_all(announcements_list)
    db.commit()

    db.close()

    print("\n🎉 Database seeding complete!")
    print(f"   - {len(user_list)} users created")
    print(f"   - {len(classes_list)} classes created")
    print(f"   - {len(enrollments_list)} enrollments created")
    print(f"   - {len(announcements_list)} announcements created")
    print(f"   - {len(graduate_projects)} graduate projects created")

    print("\n👋 Happy testing!")
except Exception as e:
    print("❌ An error occurred during seeding:", e)
    import traceback
    traceback.print_exc()