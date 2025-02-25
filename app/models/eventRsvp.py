from datetime import datetime
from app.models import*
from app.models.user import User
from app.models.event import Event

class EventRsvp(baseModel):
    user = ForeignKeyField(User)
    event = ForeignKeyField(Event, backref="rsvps")
    rsvpTime = DateTimeField(default=datetime.now)

    class Meta:
        indexes = ( (('user', 'event'), True), )
