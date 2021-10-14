from app.models.courseInstructor import CourseInstructor
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
                    .join(Term)).where(Term.id == termId, Course.status.status != "Approved", Course.status.status != "Completed").distinct()

    courseIds = []
    for course in pendingCourses:
        courseIds.append(course.id)

    pendingCourseInstructor = getinstructorData(courseIds)


    return pendingCourses, pendingCourseInstructor


def approvedCourses(termId):
    '''
    Queries the database to get all the neccessary information for
    approved courses.
    '''

    approvedCourses = (Course.select(Course, Term)
                    .join(CourseStatus)
                    .switch(Course)
                    .join(Term)).where(Term.id == termId, Course.status.status == "Approved").distinct()

    courseIds = []
    for course in approvedCourses:
        courseIds.append(course.id)

    approvedCourseInstructor = getinstructorData(courseIds)
    return approvedCourses, approvedCourseInstructor

def getinstructorData(courseIds):
    """
    Gets and instructor object for the course id's given.
    """
    instructorDict = {}
    instructor = CourseInstructor.select().where(CourseInstructor.course << courseIds)

    for i in instructor:
        instructorDict.setdefault(i.course.id, []).append(i.user.firstName + " " + i.user.lastName)

    return instructorDict
