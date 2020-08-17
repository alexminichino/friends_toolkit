import logging
import json
from fbchat import Client
from fbchat.models import *


class MessagesTool(object):
    
    def __init__(self,email="fakeemail@gmail.com", password ="fakePassword", logging_level=logging.DEBUG): #Fake credentials are needed in case of authentication by Session Cookie  
       self.authenticated = False
       self.email= email
       self.password= password       
        

    def send_message(self,user, message):
        try:
            message_id = self.client.send(Message(text=message), thread_id=user.uid, thread_type=ThreadType.USER)
            return message_id != None
        except FBchatUserError as exception: 
            return False 

    def send_image(self, user, image_path, caption):
        self.client.sendLocalImage(
            image_path,
            message=Message(text=caption),
            thread_id=user.uid,
            thread_type=ThreadType.USER,
        )

    def destroy_session(self):
        self.client.logout()

    def authenticate(self):
        try:
            self.client = MyClient(self.email,self.password, max_tries=2, user_agent= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
            self.authenticated = True
            return True
        except FBchatUserError as exception:
            self.authenticated = False
            return False  
    
    def fetch_users(self):
        if(self.authenticated):
            return self.client.fetchAllUsers()
        else:
            raise Exception("Authenticate first!")

    def getSessionClient(self, session):
        try:
            self.client = MyClient(self.email, self.password, session_cookies= session, max_tries=1, user_agent= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
            self.authenticated = self.client.isLoggedIn()
        except FBchatUserError as exception:            
            self.authenticated=False            
        return self.authenticated
        
class MyClient(Client):
    def on2FACode(self):
        """Called when a 2FA code is needed to progress."""
        return input("Please enter your 2FA code -->")

class SimplifiedUser():
    def __init__(self, uid, name, first_name, gender, photo, url, is_precontacted=False, is_excluded=False ):
        self.uid=uid
        self.name=name
        self.first_name = first_name
        self.gender = gender
        self.photo = photo
        self.url = url
        self.is_precontacted= is_precontacted
        self.is_excluded= is_excluded
    
def convert_to_dict(obj):
    """
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names.
    """
    
    #  Populate the dictionary with object meta data 
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }
    
    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)
    
    return obj_dict

def dict_to_obj(our_dict):
    """
    Function that takes in a dict and returns a custom object associated with the dict.
    This function makes use of the "__module__" and "__class__" metadata in the dictionary
    to know which object type to create.
    """
    if "__class__" in our_dict:
        # Pop ensures we remove metadata from the dict to leave only the instance arguments
        class_name = our_dict.pop("__class__")
        
        # Get the module name from the dict and import it
        module_name = our_dict.pop("__module__")
        
        # We use the built in __import__ function since the module name is not yet known at runtime
        module = __import__(module_name)
        
        # Get the class from the module
        class_ = getattr(module,class_name)
        
        # Use dictionary unpacking to initialize the object
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj