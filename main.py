import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('./env/musicstreamingrank-firebase-adminsdk-umd95-da99b91f04.json')
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://musicstreamingrank-default-rtdb.firebaseio.com/'
})

dir = db.reference()
dir.update({'자동차':'기아'})

print('데이터가 성공적으로 추가되었습니다.')