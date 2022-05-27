from flask import *
import os
import pickle

app = Flask(__name__)

seperator = "@@@"

# %3A = :
# %5C = \
# %5E = ^


with open('Token.pickle', 'rb') as handle:
    globalToken = pickle.load(handle)
with open('Admin.pickle', 'rb') as handle:
    globalAdmin = pickle.load(handle)
    AdminPass = globalAdmin['pass']


def haveAccess(token, tpass):
    try:
        raw = globalToken[token]
        if raw['pass'] == tpass:
            return True, raw['access']
    except:
        return False, {
            "read": False,
            "write": False,
            "delete": False,
            "shell": False
        }


def parseDir(loc: str):
    if not loc.endswith("\\"): loc += "\\"
    items = []
    for item in os.listdir(loc):
        if os.path.isfile(loc + item):
            types = "file"
        elif os.path.isdir(loc + item):
            types = "folder"
        else:
            types = "unknown"
        items.append({
            item: {
                "type": types,
                "size": "" if not os.path.isfile(loc + item) else os.path.getsize(loc + item)
            }
        })
    return items


def deleteAccess(token, tpass, apass):
    if apass == AdminPass:
        try:
            gpass = globalToken[token]['pass']
            if tpass == gpass:
                globalToken.pop(token)
                with open('Token.pickle', 'wb') as handle:
                    pickle.dump(globalToken, handle, protocol=pickle.HIGHEST_PROTOCOL)
                return True, {
                    "error": ""
                }
        except Exception as e:
            if e == '\'token\'':
                result = {
                    "error": "token does not exists"
                }
                return False, result

            return False, {}
    else:
        return False, {}


@app.route('/')
def root():
    return {
        "Name": os.environ['COMPUTERNAME']
    }


@app.route('/dir/<string:token>/<string:loc>', methods=['GET'])
def getdir(token: str, loc):
    try:
        tokenh = token.split(seperator)
        if len(tokenh) != 2:
            return {
                "error": "token not properly encoded"
            }
        if not os.path.isdir(loc): return {"error": "folder does not exists"}
        have, whatHave = haveAccess(token=tokenh[0], tpass=tokenh[1])
        if not have:
            return {
                "error": "Token Value Not Accepted"
            }
        if not whatHave['read']:
            return {
                "error": "Do not have read access"
            }
        return {
            "path": loc,
            "content": parseDir(loc),
            "error": ""
        }
    except:
        return {
            "error": "token not properly encoded",
        }


@app.route('/mkdir/<string:token>/<string:loc>/<string:name>', methods=['GET'])
def mkdir(token, loc, name):
    try:
        tokenh = token.split(seperator)
        if len(tokenh) == 2:
            have, whatHave = haveAccess(token=tokenh[0], tpass=tokenh[1])
            if have:
                if whatHave['write']:
                    error = ""
                    try:
                        os.system("mkdir " + loc + "\\" + name)
                    except Exception as e:
                        error = str(e)
                    result = {
                        "path": loc,
                        "error": error
                    }
                else:
                    result = {
                        "error": "Not Have Access To Write"
                    }
            else:
                result = {
                    "error": "Token Value Not Accepted"
                }
        else:
            result = {
                "error": "token not properly encoded"
            }
    except:
        result = {
            "error": "token not properly encoded"
        }
    return result


@app.route('/touch/<string:token>/<string:loc>/<string:name>', methods=['GET'])
def touch(token, loc, name):
    try:
        tokenh = token.split(seperator)
        if len(tokenh) == 2:
            have, whatHave = haveAccess(token=tokenh[0], tpass=tokenh[1])
            if have:
                if whatHave['read']:
                    error = ""
                    try:
                        os.system("type nul >>" + loc + "\\" + name)
                    except Exception as e:
                        error = str(e)
                    result = {
                        "path": loc,
                        "error": error
                    }
                else:
                    result = {
                        "error": "Not Have Access To Read"
                    }
            else:
                result = {
                    "error": "Token Value Not Accepted"
                }
        else:
            result = {
                "error": "token not properly encoded"
            }
    except:
        result = {
            "error": "token not properly encoded"
        }
    return result


@app.route('/deleteaccess/<string:apass>/<string:token>/<string:tpass>', methods=['GET'])
def adelete(apass, token, tpass):
    boolstatus, result = deleteAccess(tpass=tpass, apass=apass, token=token)
    return result


@app.route('/delete/<string:token>/<string:path>', methods=['GET'])
def delete(token, path: str):
    # result = {}
    try:
        tokenh = token.split(seperator)
        if len(tokenh) == 2:
            have, whatHave = haveAccess(token=tokenh[0], tpass=tokenh[1])
            if have:
                if whatHave['delete']:
                    print(path)
                    if os.path.isdir(path):
                        result = {
                            "error": os.system("rmdir /q /s " + path)
                        }
                    elif os.path.isfile(path):
                        result = {
                            "error": os.system("del /f " + path)
                        }
                    else:
                        result = {
                            "error": "File or Folder Does not Exists"
                        }
                else:
                    result = {
                        "error": "Not Have Access To Delete"
                    }
            else:
                result = {
                    "error": "Token Value Not Accepted"
                }
        else:
            result = {
                "error": "token not properly encoded"
            }
    except:
        result = {
            "error": "token not properly encoded"
        }
    return result


@app.route('/type/<string:token>/<string:path>', methods=['GET'])
def getType(token, path):
    try:
        tokenh = token.split(seperator)
        if len(tokenh) != 2:
            return {
                "error": "token not properly encoded"
            }
        have, whatHave = haveAccess(token=tokenh[0], tpass=tokenh[1])
        if not have:
            return {
                "error": "Token Value Not Accepted"
            }
        if not whatHave['read']:
            return {
                "error": "Do not have read access"
            }
        with open(path, 'r') as handle:
            data = handle.read()
        return {
            "content": data,
            "error": ""
        }
    except:
        return {
            "error": "token not properly encoded",
        }


# Admin Page
@app.route('/admin/<string:passt>/getusers', methods=['GET'])
def AdmingetUsers(passt):
    if not passt == AdminPass:
        return {
            "error": "Wrong Admin Pass"
        }
    return globalToken


@app.route('/admin/<string:passt>/changeadminpass/<string:newpass>')
def resetAdminPass(passt: str, newpass):
    if not passt == globalAdmin['pass']:
        return {
            "error": "Wrong Admin Pass"
        }
    globalAdmin['pass'] = newpass
    AdminPass = newpass
    OriginalAdmin = {
        "pass": newpass
    }
    with open('Admin.pickle', 'wb') as handle:
        pickle.dump(OriginalAdmin, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return {
        "content": "Successfully changed the pass",
        "error": ""
    }


@app.route("/admin/<string:passt>/adduser/<string:name>/<string:tpass>/<string:read>/<string:write>/<string:delf"
           ">/<string:shell>")
def addUser(passt, name, tpass, read, write, delf, shell):
    if not passt == globalAdmin['pass']:
        return {
            "error": "Wrong Admin Pass"
        }
    globalToken[name] = {
        "name": "test",
        "access": {
            "read": True if read == "yes" else False,
            "write": True if write == "yes" else False,
            "delete": True if delf == "yes" else False,
            "shell": True if shell == "yes" else False
        },
        "pass": tpass
    }
    return ""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
