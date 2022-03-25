from flask import request, render_template, g, abort, json, redirect, jsonify, flash
from app.models.courseInstructor import CourseInstructor
from app.models.courseQuestion import CourseQuestion
from app.models.courseStatus import CourseStatus
from app.models.course import Course
from app.models.term import Term


def pendingCourses(termId):
    '''
    Queries the database to get all the neccessary information for
    non approved and non completed courses.
    '''

    pendingCourses = (Course.select(Course, Term)
                    .join(CourseStatus)
                    .switch(Course)
                    .join(Term).where(Term.id == termId, Course.status.status != "Approved", Course.status.status != "Completed").distinct())

    return pendingCourses

def approvedCourses(termId):
    '''
    Queries the database to get all the neccessary information for
    approved courses.
    '''

    approvedCourses = (Course.select(Course, Term)
                        .join(CourseStatus)
                        .switch(Course)
                        .join(Term).where(Term.id == termId, Course.status.status == "Approved").distinct())

    return approvedCourses

def getinstructorData(courseIds):
    """
    Gets and instructor object for the course id's given.
    """
    instructorDict = {}
    instructor = CourseInstructor.select().where(CourseInstructor.course << courseIds)

    for i in instructor:
        instructorDict.setdefault(i.course.id, []).append(i.user.firstName + " " + i.user.lastName)

    return instructorDict

def createOrUpdate(id):
    """This function will return True or False based on wether a course exist or not"""
    coursecheck = Course.get_or_none(Course.id == id)

    if coursecheck != None:
        return False
    return True

def updateCourse(courseData, instructorsDict):
    """
        This function will take in courseData for the SLC proposal page and a dictionary
        of instuctors assigned to the course and update the information in the db.
    """
    print(instructorsDict)
    for toggler in ["regularOccurenceToggle", "slSectionsToggle", "permanentDesignation"]:
        courseData.setdefault(toggler, "off")
    status = CourseStatus.get(CourseStatus.status == "Pending")
    course = Course.update(
        courseName=courseData["courseName"],
        courseAbbreviation=courseData["courseAbbreviation"],
        courseCredit=courseData["credit"],
        isRegularlyOccuring=("on" in courseData["regularOccurenceToggle"]),
        term=courseData['term'],
        status=status,
        isAllSectionsServiceLearning=("on" in courseData["slSectionsToggle"]),
        serviceLearningDesignatedSections=courseData["slDesignation"],
        isPermanentlyDesignated=("on" in courseData["permanentDesignation"]),
    ).where(Course.id == courseData['courseID']).execute()
    for i in range(1, 7):
        (CourseQuestion.update(questionContent=courseData[f"{i}"])
                    .where((CourseQuestion.questionNumber == i) & (CourseQuestion.course==courseData["courseID"])).execute())
    removeInstructors = CourseInstructor.delete().where(CourseInstructor.course == courseData["courseID"]).execute()
    for instructor in instructorsDict["instructors"]:
        addInstructors = CourseInstructor.create(course=courseData["courseID"], user=instructor)
