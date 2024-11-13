''' This code is based on the example code from https://github.com/aldebaran/libqi-python/blob/master/examples/authentication_with_application.py'''

import qi
import sys 

class Authenticator:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # This method is expected by libqi and must return a dictionary containing
    # login information with the keys 'user' and 'token'.
    def initialAuthData(self):
        return {'user': self.username, 'token': self.password}

class AuthenticatorFactory:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # This method is expected by libqi and must return an object with at least
    # the `initialAuthData` method.
    def newAuthenticator(self):
        return Authenticator(self.username, self.password)

def getConnection() :
    app = qi.Application(sys.argv, url="tcp://IP_ADDRESS:PORT")
    logins = ("nao", "OMITTED")
    factory = AuthenticatorFactory(*logins)
    app.session.setClientAuthenticatorFactory(factory)
    app.start()
    print("Connection success")
    return app
