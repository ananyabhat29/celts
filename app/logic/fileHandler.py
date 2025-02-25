import os
from flask import redirect, url_for
from app import app
from app.models.eventFile import EventFile

class FileHandler:
    def __init__(self,files=None):
        self.files=files
        self.path= app.config['files']['event_attachment_path']

    def getFileFullPath(self, eventId=None, newfile = None):
        """
        This creates the directory/path for the object from the "Choose File" input in the create event and edit event.
        :returns: directory path for attachment
        """
        try:
            # tries to create the full path of the files location and passes if
            # the directories already exist or there is no attachment
            if eventId:
                filePath=(os.path.join(self.path, str(eventId), newfile.filename))
                os.makedirs(self.path +"/"+ str(eventId))

            else:
                filePath=(os.path.join(self.path, newfile.filename))
                os.makedirs(self.path+"/"+ str(eventId))
        except AttributeError:  # will pass if there is no attachment to save
            pass
        except FileExistsError:
            pass
        return filePath

    def saveFilesForEvent(self, eventId):
        """ Saves the attachment in the app/static/files/eventattachments/ directory """
        try:
            for file in self.files:
                isFileInEvent = EventFile.select().where(EventFile.event == eventId, EventFile.fileName == file.filename).exists()
                if not isFileInEvent:
                    EventFile.create(event = eventId, fileName = file.filename)
                    file.save(self.getFileFullPath(eventId = eventId, newfile = file)) # saves attachment in directory
        except AttributeError: # will pass if there is no attachment to save
            return False
            pass

    def retrievePath(self,files, eventId = None):
        pathDict={}
        for file in files:
            pathDict[file.fileName] = ((self.path+"/"+ str(eventId) +"/"+ file.fileName)[3:], file)
        return pathDict

    def deleteEventFile(self, fileId, eventId):
        """
        Deletes attachmant from the app/static/files/eventattachments/ directory
        """
        try:
            file = EventFile.get_by_id(fileId)
            path = os.path.join(self.path,str(eventId), file.fileName)
            os.remove(path)
            file.delete_instance()
        except AttributeError: #passes if no attachment is selected.
            pass
