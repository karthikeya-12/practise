from mongoengine import connect, Document, StringField, IntField, ObjectIdField
from dotenv import load_dotenv
import os

load_dotenv()
connect(
    db=os.getenv("mongo_db"),
    host=os.getenv("mongo_host"),
    port=int(os.getenv("mongo_port")),
)


class User(Document):
    name = StringField()
    age = IntField()
    _id = ObjectIdField()

    meta = {"collection": "users"}


""" new_user = User(name="Ishu", age=20)
new_user.save()
 """
users = User.objects(name="Ishu")
for user in users:
    print(user.name, user.age, user._id)
