from app.models.eventTemplate import EventTemplate
# from app.models.backgroundCheck import BackgroundCheck
from app.models.term import Term
from app.models.courseStatus import CourseStatus
from app.models.backgroundCheckType import BackgroundCheckType

terms = [
    {
        "id": 7,
        "description": "Summer 2022",
        "year": 2022,
        "academicYear": "2021-2022",
        "isSummer": True,
        "isCurrentTerm": False
    },
    {
        "id": 8,
        "description": "Fall 2022",
        "year": 2022,
        "academicYear": "2022-2023",
        "isSummer": False,
        "isCurrentTerm": False
    },
    {
        "id": 9,
        "description": "Spring 2023",
        "year": 2023,
        "academicYear": "2022-2023",
        "isSummer": False,
        "isCurrentTerm": False
    },
]
Term.insert_many(terms).on_conflict_replace().execute()

print("Inserting base data needed in all environments.")
templates = [
    {
        "id": 1,
        "name": "Single Program",
        "tag": "single-program",
        "templateJSON": "{}",
        "templateFile": "createEvent.html",
        "isVisible": False
    },
    {
        "id": 2,
        "name": "All Volunteer Training",
        "tag": "all-volunteer",
        "templateJSON": '{"name": "All Volunteer Training","description": "Training for all CELTS programs", "isTraining": true, "isService": false, "isRequired": true, "isAllVolunteerTraining": true}',
        "templateFile": "createEvent.html",
        "isVisible": True
    },
    {
        "id": 3,
        "name": "CELTS-Sponsored Event",
        "tag": "no-program",
        "templateJSON": "{}",
        "templateFile": "createEvent.html",
        "isVisible": True
    },

]
EventTemplate.insert_many(templates).on_conflict_replace().execute()

backgroundTypes = [
    {
    "id": "CAN",
    "description": "Child Abuse and Neglect Background Check",
    },
    {
    "id": "SHS",
    "description": "Safe Hiring Solutions",
    },
    {
    "id": "FBI",
    "description": "Federal Criminal Background Check",
    },
    {
    "id": "BSL",
    "description": "Berea Student Life Background Check",
    },

]
BackgroundCheckType.insert_many(backgroundTypes).on_conflict_replace().execute()

coursestatus = [
    {
        "id": 1,
        "status": "Incomplete"
    },
    {
        "id": 2,
        "status": "Submitted"
    },
    {
        "id": 3,
        "status": "Approved"
    }
]
CourseStatus.insert_many(coursestatus).on_conflict_replace().execute()
