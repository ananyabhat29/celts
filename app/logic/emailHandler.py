from datetime import datetime
from peewee import DoesNotExist, JOIN
from flask_mail import Mail, Message
import os

from app import app
from app.models.programEvent import ProgramEvent
from app.models.interest import Interest
from app.models.user import User
from app.models.program import Program
from app.models.eventRsvp import EventRsvp
from app.models.emailTemplate import EmailTemplate
from app.models.emailLog import EmailLog
from app.models.event import Event
from app.models.eventParticipant import EventParticipant
from app.models.programBan import ProgramBan
from app.models.term import Term

class EmailHandler:
    def __init__(self, raw_form_data, url_domain, sender_object, attachment_file=None):

        self.mail = Mail(app)
        self.raw_form_data = raw_form_data
        self.url_domain = url_domain
        self.override_all_mail = app.config['MAIL_OVERRIDE_ALL']
        self.sender = sender_object
        self.template_identifier = None
        self.subject = None
        self.body = None
        self.reply_to = None
        self.event = None
        self.program_ids = None
        self.recipients = None
        self.sl_course_id = None
        self.attachment_path = app.config['files']['email_attachment_path']
        self.attachment_file = attachment_file

    def process_data(self):
        """ Processes raw data and stores it in class variables to be used by other methods """
        # Email Template Data
        self.template_identifier = self.raw_form_data['templateIdentifier']

        if 'subject' in self.raw_form_data:
            self.subject = self.raw_form_data['subject']

        if 'body' in self.raw_form_data:
            self.body = self.raw_form_data['body']

        if 'replyTo' in self.raw_form_data:
            self.reply_to = self.raw_form_data['replyTo']

        # Event
        if 'eventID' in self.raw_form_data:
            event = Event.get_by_id(self.raw_form_data['eventID'])
            self.event = event

        # Program
        if 'programID' in self.raw_form_data:
            self.program_ids = self.fetch_event_programs(self.raw_form_data['programID'])

        # Recipients
        if 'recipientsCategory' in self.raw_form_data:
            self.recipients_category = self.raw_form_data['recipientsCategory']
            self.recipients = self.retrieve_recipients(self.recipients_category)

        # Service-Learning Course
        if 'slCourseId' in self.raw_form_data:
            self.sl_course_id = self.raw_form_data['slCourseId']

    def fetch_event_programs(self, program_id):
        """ Fetches all the programs of a particular event """
        # Non-student-led programs have "Unknown" as their id
        if program_id == 'Unknown' or program_id is None:
            programEvents = ProgramEvent.select(ProgramEvent.program).where(ProgramEvent.event==self.event.id)
            return [program.program for program in programEvents.objects()]
        else:
            return [Program.get_by_id(program_id)]

    def update_sender_config(self):
        # We might need this.
        # This functionality should be moved somewhere else.
        # The function in another file would receive email_info[sender]
        # and update the config based on that and wherever we will end up saving emails and passwords
        #The sender information should be saved like so: {"name": [email, password], } or in the database
        pass

    def retrieve_recipients(self, recipients_category):
        """ Retrieves recipient based on which category is chosen in the 'To' section of the email modal """
        # Other potential recipients:
        # - course instructors
        # - course Participants
        # - outside participants'
        if recipients_category == "Interested":
            recipients = (User.select()
                .join(Interest)
                .join(Program, on=(Program.id==Interest.program))
                .where(Program.id.in_([p.id for p in self.program_ids])))
        if recipients_category == "RSVP'd":
            recipients = (User.select()
                .join(EventRsvp)
                .where(EventRsvp.event==self.event.id))

        if recipients_category == "Eligible Students":
            # all terms with the same accademic year as the current term,
            # the allVolunteer training term then needs to be in that query
            Term2 = Term.alias()

            sameYearTerms = Term.select().join(Term2, on=(Term.academicYear == Term2.academicYear)).where(Term2.isCurrentTerm == True)

            bannedUsers = ProgramBan.select(ProgramBan.user_id).where((ProgramBan.endDate > datetime.now()) | (ProgramBan.endDate is None), ProgramBan.program_id.in_([p.id for p in self.program_ids]))
            allVolunteer = Event.select().where(Event.isAllVolunteerTraining == True, Event.term.in_(sameYearTerms))
            recipients = User.select().join(EventParticipant).where(User.username.not_in(bannedUsers), EventParticipant.event.in_(allVolunteer))
        return [recipient for recipient in recipients]

    def replace_general_template_placeholders(self, email_body=None):
        """ Replaces all template placeholders except name """
        event_link = f"{self.url_domain}/eventsList/{self.event.id}/edit"

        new_body = email_body.format(event_name=self.event.name,
            location=self.event.location,
            start_date=(self.event.startDate).strftime('%m/%d/%Y'),
            end_date=(self.event.endDate).strftime('%m/%d/%Y'),
            start_time=(self.event.timeStart).strftime('%I:%M'),
            end_time=(self.event.timeEnd).strftime('%I:%M'),
            event_link=event_link,
            name="{name}")
        return new_body

    def replace_name_placeholder(self, name, body):
        """ Replaces name placeholder with recipient's full name """
        new_body = body.format(name=name)
        return new_body

    def retrieve_and_modify_email_template(self):
        """ Retrieves email template based on idenitifer and calls replace_general_template_placeholders"""

        email_template = EmailTemplate.get(EmailTemplate.purpose==self.template_identifier) # --Q: should we keep purpose as the identifier?
        template_id = email_template.id

        subject = self.subject if self.subject else email_template.subject

        body = self.body if self.body else email_template.body
        new_body = self.replace_general_template_placeholders(body)

        self.reply_to = email_template.replyToAddress
        return (template_id, subject, new_body)

    def getAttachmentFullPath(self, newfile=None):
        """
        This creates the directory/path for the object from the "Choose File" input in the emailModal.html file.
        :returns: directory path for attachment
        """
        attachmentFullPath = None
        try:
            # tries to create the full path of the files location and passes if
            # the directories already exist or there is no attachment
            attachmentFullPath = os.path.join(self.attachment_path, newfile.filename)
            if attachmentFullPath[:-1] == self.attachment_path:
                return None
            os.mkdir(self.attachment_path)

        except AttributeError:  # will pass if there is no attachment to save
            pass
        except FileExistsError: # will pass if the file already exists
            pass
        return attachmentFullPath

    def saveAttachment(self):
        """ Saves the attachment in the app/static/files/attachments/ directory """
        try:
            for file in self.attachment_file:
                attachmentFullPath = self.getAttachmentFullPath(newfile = file)
                if attachmentFullPath:
                    file.save(attachmentFullPath) # saves attachment in directory

        except AttributeError: # will pass if there is no attachment to save
            pass

    def store_sent_email(self, subject, template_id):
        """ Stores sent email in the email log """
        date_sent = datetime.now()

        attachmentNames = []
        for file in self.attachment_file:
            attachmentNames.append(file.filename)

        EmailLog.create(
            event = self.event.id,
            subject = subject,
            templateUsed = template_id,
            recipientsCategory = self.recipients_category,
            recipients = ", ".join(recipient.email for recipient in self.recipients),
            dateSent = date_sent,
            sender = self.sender,
            attachmentNames = attachmentNames)

    def build_email(self):
        # Most General Scenario
        self.saveAttachment()
        self.process_data()
        template_id, subject, body = self.retrieve_and_modify_email_template()
        return (template_id, subject, body)

    def send_email(self):
        defaultEmailInfo = {"senderName":"Sandesh", "replyTo":self.reply_to}
        template_id, subject, body = self.build_email()

        if len(self.program_ids) == 1:
            if self.program_ids[0].contactEmail:
                defaultEmailInfo["replyTo"] = self.program_ids[0].contactEmail
            if self.program_ids[0].contactName:
                defaultEmailInfo["senderName"] = self.program_ids[0].contactName

        try:
            with self.mail.connect() as conn:
                for recipient in self.recipients:
                    full_name = f'{recipient.firstName} {recipient.lastName}'
                    email_body = self.replace_name_placeholder(full_name, body)

                    conn.send(Message(
                        subject,
                        # [recipient.email],
                        [self.override_all_mail],
                        email_body,
                        file_attachment = self.getAttachmentFullPath(), #needs to be modified later
                        reply_to = defaultEmailInfo["replyTo"],
                        sender = (defaultEmailInfo["senderName"], defaultEmailInfo["replyTo"])
                    ))
            self.store_sent_email(subject, template_id)
            return True
        except Exception as e:
            print("Error on sending email: ", e)
            return False

    def update_email_template(self):
        try:
            self.process_data()
            (EmailTemplate.update({
                EmailTemplate.subject: self.subject,
                EmailTemplate.body: self.body,
                EmailTemplate.replyToAddress: self.reply_to
            }).where(EmailTemplate.purpose==self.template_identifier)).execute()
            return True
        except Exception as e:
            print("Error updating email template record: ", e)
            return False

    def retrieve_last_email(event_id):
        try:
            last_email = EmailLog.select().where(EmailLog.event==event_id).order_by(EmailLog.dateSent.desc()).get()
            return last_email
        except DoesNotExist:
            return None
