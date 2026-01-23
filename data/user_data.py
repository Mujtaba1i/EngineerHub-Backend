from models.user import UserModel, UserRole

def create_test_users():
    # Student - Mujtaba
    user1 = UserModel(
        name="Mujtaba",
        email="Mujtaba@stu.uob.edu.bh",
        role=UserRole.STUDENT,
        major="Electrical Engineering",
        uni_id=202002179,
    )
    user1.set_password("Help!")

    # Graduate - Sajeda
    user2 = UserModel(
        name="Sajeda Hussain",
        email="Sajeda@stu.uob.edu.bh",
        role=UserRole.GRADUATE,
        major="Chimical Engineering",
        uni_id=202002020,
    )
    user2.set_password("Pengu")

    # Doctor
    user3 = UserModel(
        name="Dr. Omar",
        email="Omar@uob.edu.bh",
        role=UserRole.DOCTOR,
        department="Software Engineering",
        phone_num="+9999999",
        office_num="CS-210",
    )
    user3.set_password("one more thing")

    # Institution
    user4 = UserModel(
        name="I don't know",
        email="IDK@gmail.com",
        role=UserRole.INSTITUTION,
        license="https://image.something.com/image.img",
    )
    user4.set_password("Give me your money")

    return [user1, user2, user3, user4]


user_list = create_test_users()