from datetime import datetime, timedelta
from models.announcement import AnnouncementModel

def create_announcements(classes):
    """
    Create test announcements for the seeded classes
    """
    # Get current date for relative dates
    today = datetime.now()
    
    return [
        # Urgent announcement (2 days away) - SEB-11 class
        AnnouncementModel(
            title="Midterm Exam",
            content="Midterm exam will cover chapters 1-5. Please bring your calculator and student ID. The exam will be held in room CS-101.",
            event_date=today + timedelta(days=2, hours=10),
            class_=classes[0]  # SEB-11
        ),
        
        # Soon announcement (5 days away) - SEB-11 class
        AnnouncementModel(
            title="Assignment 3 Due",
            content="Don't forget to submit Assignment 3 on the LMS. Late submissions will receive a 10% penalty per day.",
            event_date=today + timedelta(days=5, hours=23, minutes=59),
            class_=classes[0]  # SEB-11
        ),
        
        # Normal announcement (10 days away) - AI Accelerator class
        AnnouncementModel(
            title="Guest Lecture: Machine Learning in Production",
            content="Join us for a special guest lecture by Dr. Sarah Johnson from Google AI. She will discuss deploying ML models at scale. Room: CS-201",
            event_date=today + timedelta(days=10, hours=14),
            class_=classes[1]  # AI Accelerator
        ),
        
        # Past announcement (2 days ago) - SEB-11 class
        AnnouncementModel(
            title="Lab Session Completed",
            content="Thank you all for attending the hands-on lab session. The lab materials are now available on the course website.",
            event_date=today - timedelta(days=2, hours=10),
            class_=classes[0]  # SEB-11
        ),
        
        # Past announcement (5 days ago) - AI Accelerator class
        AnnouncementModel(
            title="Quiz 1 Results Posted",
            content="Quiz 1 results have been posted. Please check your grades on the LMS. If you have any concerns, visit office hours this week.",
            event_date=today - timedelta(days=5, hours=9),
            class_=classes[1]  # AI Accelerator
        ),
        
        # Normal announcement (15 days away) - AI Accelerator class
        AnnouncementModel(
            title="Final Project Proposal Due",
            content="Your final project proposal is due in two weeks. Please include: project title, team members, problem statement, and proposed solution. Submit via LMS.",
            event_date=today + timedelta(days=15, hours=23, minutes=59),
            class_=classes[1]  # AI Accelerator
        ),
        
        # Urgent announcement (today!) - AI Accelerator class
        AnnouncementModel(
            title="Office Hours Today",
            content="Reminder: Office hours today from 2 PM to 4 PM in CS-210. Come with your questions about the upcoming project!",
            event_date=today + timedelta(hours=14),
            class_=classes[1]  # AI Accelerator
        ),
    ]