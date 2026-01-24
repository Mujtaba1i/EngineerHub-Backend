from models.role import RoleModel
from models.classes import ClassModel
from models.student_class import StudentClassModel


def create_roles(users):
    return [
        RoleModel(user=users[0], major="Electrical Engineering"),
        RoleModel(user=users[1], major="Chimical Engineering"),
        RoleModel(user=users[2], department="Software Engineering"),
        RoleModel(user=users[3], approval=True),
    ]


def create_classes(users):
    return [
        ClassModel(name="SEB-11", doctor=users[2]),
        ClassModel(name="AI Accelerator", doctor=users[2]),
    ]


def create_enrollments(users, classes):
    return [
        StudentClassModel(student=users[0], class_=classes[0]),
        StudentClassModel(student=users[0], class_=classes[1]),
        StudentClassModel(student=users[1], class_=classes[0]),
    ]