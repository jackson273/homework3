import config
import datetime
import random, string

from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

USER_DB_DIR = config.USER_DB_DIR
DATABASE_URI = config.DATABASE_URI

client = MongoClient(DATABASE_URI)
db = client['Homework3']
users = db['Users']

def gen_session_token(length=24):
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])
    return token

class User:
    username = ''
    password = ''
    token = ''
    posts = []

    def __init__(self, _id):
        user = users.find_one({'_id': _id})
        self.cur = user
        self._id = _id
        self.username = user['username']
        self.password = user['password']
        self.token = user['token']
        self.imageURL = user['imageURL']
        self.posts = user['posts']
        

    def __str__(self):
        return self.username

    @classmethod
    def get_all_posts_of_user(cls, *args, **kwargs):
        query = []
        for user in users.find(kwargs):
            for id, post in enumerate(user['posts']):
                query.append(Post(id, user['username'], post['timestamp'], post['imageURL'], post['title'], post['text']))
        return query

    @classmethod
    def filter(cls, *args, **kwargs):
        query = []
        for user in users.find(kwargs):
            query.append(User(user['_id']))
        return query

    @classmethod
    def create(cls, username, password, token=None, imageURL='upload/user-default-img.jpg'):
        id = users.insert_one({
                'username': username, 
                'password': generate_password_hash(password),
                'token': token,
                'imageURL': imageURL,
                'posts':[]
            }).inserted_id
        user = cls(id)
        return user

    def create_post(self, title, text, imageURL='upload/post-default-img.jpg'):
        post = {
            'timestamp': datetime.datetime.now().strftime("%d %b %Y, %H:%M:%S"),
            'imageURL': imageURL,
            'title': title,
            'text': text,
        }
        self.posts.append(post)

    def is_existed(self):
        return User.filter(username=self.username) != []

    def delete(self):
        return users.delete_one({'_id': self._id})
    
    def save(self):
        users.update_one(
            {'_id':self._id}, 
            {
                '$set' : {
                    'username': self.username,
                    'password': self.password,
                    'token': self.token,
                    'imageURL': self.imageURL,
                    'posts': self.posts
                }
            },
            upsert=True
        )

    def authenticate(self, password):
        return check_password_hash(self.password, password)

    def edit_pwd(self, password):
        self.password = generate_password_hash(password)
        self.terminate_session()

    def init_session(self):
        self.token = gen_session_token()
        self.save()
        return self.token

    def terminate_session(self):
        self.token = None
        self.save()

class Post:
    id = ''
    author = ''
    timestamp = ''
    imageURL = ''
    title = ''
    text = ''

    def __init__(self, id, author, timestamp, imageURL, title, text):
        self.author = author
        self.timestamp = timestamp
        self.imageURL = imageURL
        self.title = title
        self.text = text