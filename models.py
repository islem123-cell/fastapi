from mongoengine import Document,IntField,ListField,StringField



class Employee(Document):
    emp_id = IntField()
    name= StringField()
    age = IntField()
    roles = ListField()

class User(Document):
    first_name= StringField()
    last_name = StringField()
    email=StringField()
    username= StringField()
    password=StringField()