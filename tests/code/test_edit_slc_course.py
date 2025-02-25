import pytest
from flask import g
from werkzeug.datastructures import MultiDict

from app import app
from app.models import mainDB
from app.models.course import Course
from app.models.courseInstructor import CourseInstructor
from app.models.user import User
from app.models.courseStatus import CourseStatus
from app.logic.courseManagement import updateCourse

@pytest.mark.integration
def test_update_course():
    with mainDB.atomic() as transaction:
        testUser = User.create( username="testuser",
                                bnumber="B00000001",
                                email="test@test.edu",
                                phoneNumber="555-555-5555",
                                firstName="Test",
                                lastName="User",
                                isFaculty="1")
        testingCourse = Course.create(
                                        courseName = "Testing Course",
                                        courseAbbreviation = "TC",
                                        courseCredit = 2,
                                        courseOccurrence = "this event is ALL THE TIME",
                                        term = 3,
                                        status = CourseStatus.SUBMITTED,
                                        createdBy = testUser,
                                        isAllSectionsServiceLearning = 0,
                                        serviceLearningDesignatedSections = "None",
                                        isPermanentlyDesignated = 0)
        testingCourseInstructor = CourseInstructor.create( course=testingCourse, user="ramsayb2")

        courseDict = MultiDict({
                        "courseName": "Course Edited",
                        "courseID": testingCourse,
                        "courseAbbreviation": "EDIT",
                        "credit": 1.5,
                        "courseOccurrence": "NEVER",
                        "term": 2,
                        "slSectionsToggle": "on",
                        "slDesignation": "All",
                        "permanentDesignation": "on",
                        "1": "Question 1",
                        "2": "Question 2",
                        "3": "Question 3",
                        "4": "Question 4",
                        "5": "Question 5",
                        "6": "Question 6",
                        })
        courseDict.update(MultiDict([
                            ("instructor[]",testUser.username),
                            ("instructor[]",testingCourseInstructor.user.username)]))

        with app.test_request_context():
            g.current_user = "ramsayb2"
            updateCourse(courseDict)

        updatedCourse = Course.get_by_id(testingCourse.id)
        assert updatedCourse.courseName == "Course Edited"
        assert updatedCourse.courseAbbreviation == "EDIT"
        assert updatedCourse.courseCredit == 1.5
        assert updatedCourse.courseOccurrence == "NEVER"
        assert updatedCourse.status.id == CourseStatus.SUBMITTED
        assert updatedCourse.isAllSectionsServiceLearning
        assert updatedCourse.serviceLearningDesignatedSections == "All"
        assert updatedCourse.isPermanentlyDesignated

        instructorCount = CourseInstructor.select().where(CourseInstructor.course == updatedCourse.id).count()
        assert instructorCount == 2

        transaction.rollback()
