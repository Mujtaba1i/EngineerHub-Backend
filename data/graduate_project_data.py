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
            poster="https://example.com/posters/car-accident-prevention.png",
            major="Electrical Engineering",
            graduation_year=2024,
            contact_email="Mujtaba@stu.uob.edu.bh",
            contact_phone="+97312345678",
            linkedin="https://linkedin.com/in/mujtaba",
            user=users[0],  # Mujtaba
        ),

        GraduateProjectModel(
            title="AI-Based Energy Consumption Optimization",
            summary=(
                "A machine learning system that analyzes building energy usage "
                "patterns and provides optimization recommendations to reduce "
                "power consumption and operational costs."
            ),
            poster=None,
            major="Chemical Engineering",
            graduation_year=2023,
            contact_email="Sajeda@stu.uob.edu.bh",
            contact_phone=None,
            linkedin="https://linkedin.com/in/sajeda-hussain",
            user=users[1],  # Sajeda
        ),
    ]
