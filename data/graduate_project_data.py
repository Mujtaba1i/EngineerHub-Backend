from models.graduate_project import GraduateProjectModel

def create_graduate_projects(users):
    return [
        GraduateProjectModel(
            title="Smart Car Accident Prevention System",
            summary=(
                "An ESP32-S3 based system that detects potential car accidents using "
                "sensors and computer vision. The system provides real-time warnings "
                "and automatically sends emergency notifications with GPS location "
                "after an accident occurs."
            ),
            poster="https://i.imgur.com/XdLrjzV.jpeg",
            major="Electrical Engineering",
            graduation_year=2025,
            contact_email="Mujtaba@stu.uob.edu.bh",
            contact_phone="+973 39232337",
            linkedin="https://linkedin.com/in/mujtaba1i",
            user=users[0],  # Mujtaba
        ),

        GraduateProjectModel(
            title="AI-Based Energy Consumption Optimization",
            summary=(
                "A machine learning system that analyzes building energy usage "
                "patterns and provides optimization recommendations to reduce "
                "power consumption and operational costs."
            ),
            poster='https://i.imgur.com/guH9fRv.jpeg',
            major="Chemical Engineering",
            graduation_year=2025,
            contact_email="Sajeda@stu.uob.edu.bh",
            contact_phone='+973 12345678',
            linkedin="https://linkedin.com/in/sajedataqi",
            user=users[1],  # Sajeda
        ),
    ]
