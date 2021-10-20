from app.models.eventParticipant import EventParticipant
from app.models.eventRsvp import EventRsvp
from app.models.user import User
from app.models.event import Event

from datetime import datetime


def getEventLengthInHours(startTime, endTime, eventDate):
    """
    Converts the event length hours into decimal
    parameters: startTime- start time event (type: time)
                endTime- end time event (type: time)
                eventDate- date of the event (type: datetime)
    """
    #can only subtract datetime objects, not time objects. So convert time into datetime
    eventLength = datetime.combine(eventDate, endTime) - datetime.combine(eventDate, startTime)
    eventLengthInHours = round(eventLength.seconds/3600, 2)
    return eventLengthInHours


def updateVolunteers(participantData):
    """
    Create new entry in event participant table if user does not exist. Otherwise, updates the record.

    param: participantData- a dictionary that contains data from every row of the page along with the associated username.
    """
    for user in range(1, len(participantData)):
        if f'username{user}' in participantData:
            username = participantData[f'username{user}']
            userObject = User.get_or_none(User.username==username)
            event = Event.get_or_none(Event.id==participantData['event'])
            eventParticipant = EventParticipant.get_or_none(user=userObject, event=participantData['event'])
            if userObject:
                try:
                    if participantData[f'checkbox_{username}']: #if the user is marked as present
                        hoursEarned = float(participantData['inputHours_'+ username])
                        if eventParticipant:
                            ((EventParticipant
                                .update({
                                    EventParticipant.hoursEarned: hoursEarned})
                                .where(
                                    EventParticipant.event==participantData['event'],
                                    EventParticipant.user==participantData[f'username{user}']))
                                .execute())
                        else:
                            (EventParticipant
                                .create(
                                    user=user,
                                    event=event,
                                    hoursEarned=hoursEarned))
                except (KeyError):   #if there is no checkbox for user then they are not present for the event.
                    if eventParticipant:
                        ((EventParticipant
                            .update({
                                EventParticipant.hoursEarned: 0})
                            .where(
                                EventParticipant.event==participantData['event'],
                                EventParticipant.user==participantData[f'username{user}']))
                            .execute())
                    else:
                        (EventParticipant
                            .create(
                                user=user,
                                event=event,
                                hoursEarned=0))
            else:
                return False
        else:
            break
    return True


def addVolunteerToEvent(user, volunteerEventID):
    '''
    Adds a volunteer to event rsvp table when a user rsvps and when they are
    added through the track volunteer page by an admin.

    param: user - a string containing username
           volunteerEventID - id of the event the volunteer is being registered for
    '''
    try:
        if not EventRsvp.get_or_none(user=user, event=volunteerEventID):
            EventRsvp.create(user=user, event=volunteerEventID)
        return True

    except Exception as e:
        return False
