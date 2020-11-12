from oauth2client.service_account import ServiceAccountCredentials
from werkzeug.utils import redirect

from model.User import User
import firebase_admin
from firebase_admin import credentials, db, messaging

pathService_acount_json = 'covidtracing-749e0-firebase-adminsdk-2ub07-05c9957b06.json'
cred = credentials.Certificate(
    pathService_acount_json)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://covidtracing-749e0.firebaseio.com'
})
ref = db


def get_token():
    """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        pathService_acount_json)
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token

def addGeneralNotiToFB(contentNoti,title):
    print(ref.reference('notification').push().set({
        'title':title,
        'content':contentNoti
    }))

def getUsers(ref):
    objUsers = ref.reference('user').get()
    listUsers = []
    for userID in objUsers:
        phone = objUsers[userID]['phone']
        isExposed = objUsers[userID]['expose']
        key = objUsers[userID]['key']
        listUsers.append(User(userID, phone, key, isExposed))
    return listUsers

def deleteUser(ID):
    ref.reference('user').child(ID).delete()

def update(ID):
    ref.reference('user').child(ID).update(
        {
            'expose': 'F0'
        }
    )


def pushNotification( historyLocation, keyApp,title):
    # The topic name can be optionally prefixed with "/topics/".
    topic = 'covidtracing'
    if historyLocation == "":
        historyLocation = "Test"
    if keyApp == "":
        keyApp = "Test Key"
    if title=="":
        title = "test title"
    # See documentation on defining a message payload.
    messages = [
        # Gửi tin nhắn lịch trình đi lại tại đây, gửi kèm Key người bi F0
        messaging.Message(
            data={
                'title':title,
                'key': keyApp,
                'historyLocation': historyLocation,
            },
            topic=topic,
        ),
        # ...
        # Gửi thêm tin nhắn lịch trình đi lại tại đây luôn
        messaging.Message(
            notification=messaging.Notification('Thông báo ca nhiễm F0', historyLocation),
            topic=topic,
        ),
    ]
    # The topic name can be optionally prefixed with "/topics/".

    # See documentation on defining a message payload.
    # message = messaging.Message(
    #     data={
    #         'score': '850',
    #         'time': '2:45',
    #     },
    #     topic=topic,
    # )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send_all(messages)
    # Response is a message ID string.
    print('Successfully sent message:', response)

def pushGeneralNotification(contentNoti,title):
    topic = 'covidtracing'
    if contentNoti=="":
        contentNoti = "Content Test Noti"
    if title=="":
        title = "Test title"
    messages = [
        # Gửi tin nhắn lịch trình đi lại tại đây, gửi kèm Key người bi F0
        messaging.Message(
            data={
                'generalNotification': contentNoti,
                'title':title,
            },
            topic=topic,
        ),
        # ...
        # Gửi thêm tin nhắn lịch trình đi lại tại đây luôn
        messaging.Message(
            notification=messaging.Notification('Thông báo: '+title, contentNoti),
            topic=topic,
        ),
    ]
    response = messaging.send_all(messages)
    # Response is a message ID string.
    print('Successfully sent message:', response)


    
from flask import Flask, request, render_template, url_for
app = Flask(__name__)
@app.route('/generalnotification',methods=['POST'])
def handleNotification():
    notification = ""
    title = ""
    title = request.form['titleNoti']
    notification = request.form['historyLocation']
    pushGeneralNotification(notification,title)
    addGeneralNotiToFB(notification,title)
    print(notification)
    return redirect('/')

@app.route('/deleteuser',methods=['GET'])
def delete():
    IDUser = request.args.get('idremove')
    deleteUser(IDUser)
    return redirect('/')

@app.route('/handle', methods=['GET','POST'])
def handleRequest():
    IDUser = ""
    historyLocation = ""
    keyApp = ""
    title = ""
    historyLocation = request.form['historyLocation']
    title = request.form['titleNoti']
    print(historyLocation)

    IDUser = request.args.get('id')
    keyApp = request.args.get('key')
    print(keyApp)

    update(IDUser)
    # print(get_token())
    # do somthing
    pushNotification(historyLocation, keyApp,title)
    return redirect('/')


@app.route('/')
def homePage():
    return render_template('index.html', users=getUsers(ref))


if __name__ == '__main__':
    app.run()
