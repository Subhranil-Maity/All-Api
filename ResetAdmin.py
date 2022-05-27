import pickle
import os
import sys

OriginalToken = {
    "test": {
        "name": "test",
        "access": {
            "read": True,
            "write": True,
            "delete": True
        },
        "pass": "testllb"
    }
}


def TokenReset():
    with open('Token.pickle', 'wb') as handle:
        pickle.dump(OriginalToken, handle, protocol=pickle.HIGHEST_PROTOCOL)


def AdminRead():
    with open('Admin.pickle', 'rb') as handle:
        globalAdmin = pickle.load(handle)
    return globalAdmin['pass']


def AdminReset(passd: str = "changeme"):
    OriginalAdmin = {
        "pass": passd
    }
    with open('Admin.pickle', 'wb') as handle:
        pickle.dump(OriginalAdmin, handle, protocol=pickle.HIGHEST_PROTOCOL)


def Reset():
    print("Warning this will not only reset the admin password but also reset all the tokens saved")
    con = str(input("Do You Want To continue ('Y' for yes/ 'N' for no) "))
    if con == 'y' or con == 'Y':
        TokenReset()
        AdminReset()
        print("Resetting Admin info and Tokens")
        print("Successfully set password is \'changeme\'")
    elif con == 'n' or con == 'N':
        print("Exiting")
        sys.exit()
    else:
        print("Unknown value entered")
        sys.exit()


def ChangePass():
    opass = str(input("Enter the old password ->"))
    if str(AdminRead()) == opass:
        npass = str(input("Enter the new password ->"))
        AdminReset(passd=npass)
    else:
        print("Entered Wrong Old Password")
        sys.exit()


def CreateNew():
    print("No Admin info found \n Created new")
    AdminReset()
    print("Default password is \'changeme\'")


if os.path.isfile(os.getcwd() + "\\Admin.pickle"):
    print("An Admin file found")
    print("Choose Action to be performed:")
    print("\t1. Reset Admin File")
    print("\t2. Change Admin Password")
    toBeDone = str(input("Enter What Should Be Done ->"))
    if toBeDone == '1':
        Reset()
    elif toBeDone == '2':
        ChangePass()
    else:
        print(toBeDone + " Out Of Range")
else:
    CreateNew()
