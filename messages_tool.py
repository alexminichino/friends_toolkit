from fbchat import Client
from fbchat.models import *

class MessagesTool(object):
    
    def __init__(self,email="fakeemail@gmail.com", password ="fakePassword"): #Fake credentials are needed in case of authentication by Session Cookie  
       self.authenticated = False
       self.email= email
       self.password= password       
        

    def send_message(self,user, message):
        self.client.send(Message(text=message), thread_id=user.uid, thread_type=ThreadType.USER)

    def send_image_to_user(self, user, image_path, caption):
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
            self.client = MyClient(self.email,self.password, max_tries=2)
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
            self.client = MyClient(self.email, self.password, session_cookies= session, max_tries=1)
            self.authenticated = self.client.isLoggedIn()
        except FBchatUserError as exception:            
            self.authenticated=False            
        return self.authenticated
        
class MyClient(Client):
    def on2FACode(self):
        """Called when a 2FA code is needed to progress."""
        return input("Please enter your 2FA code -->")
    


