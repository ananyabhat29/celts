from app.models.event import Event
from app.models.program import Program
from peewee import DoesNotExist
def getEvents(program_id=None):

    if program_id:
        Program.get_by_id(program_id) # raises an exception if program doesn't exist
        return Event.select(Event).where(Event.program == program_id)
    else:
        return Event.select()

def groupingEvents(termID):
    studentLedPrograms = (Event.select()
                               .join(Program)
                               .where(Program.isStudentLed))

    trainingEvents = (Event.select()
                           .where(Event.isTraining))

    bonnerScholarsPrograms = (Event.select()
                                   .join(Program)
                                   .where(Program.isBonnerScholars))

    oneTimeEvents = (Event.select()
                          .join(Program)
                          .where(Program.isStudentLed == False,
                                 Event.isTraining == False,
                                 Program.isBonnerScholars == False))

    return studentLedPrograms, trainingEvents, bonnerScholarsPrograms, oneTimeEvents
