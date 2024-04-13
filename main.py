import json
from fastapi import FastAPI
from models import Employee, User
from mongoengine import connect

app=FastAPI()
connect(db="hrms",host ="localhost", port=27017 )

# @app.get("/")
# def home():
#     return{"message": "helo islem!"}





@app.get("/get_all_employees")
def get_all_employees():
    employees = json.loads(Employee.objects().to_json())

    return {"employees": employees}

@app.get("/get_employee/{emp_id}")
def get_employee(emp_id:int):
    employee = Employee.objects.get(emp_id=emp_id)
    employee_dict ={
              "emp_id": employee.emp_id,
              "name": employee.name,
              "age" :employee.age,
              "roles" : employee.roles
              }
    return employee_dict
from fastapi import Query
from mongoengine.queryset.visitor import Q
@app.get("/search_employees")
def search_employees(name:str,age:int =Query(None,gt=18)):
    employees =json.loads(Employee.objects.filter(Q(name__icontains=name) | Q(age=age)).to_json())
    return{"employees": employees}

from pydantic import BaseModel


class NewEmployee(BaseModel):
    emp_id: int
    name:str
    age:int
    roles:list


@app.post("/add_emplyee")
def add_employee(employee: NewEmployee):
    new_employee= Employee(emp_id = employee.emp_id,
                           name=employee.name,
                           age=employee.age,
                           roles=employee.roles)
    new_employee.save()
    return {"message":"Employee added succefully"}

@app.delete("/employees/{employee_id}")
def delete_employee(emp_id: str):
    employee = Employee.objects.filter(id=emp_id).first()

    if employee:
        employee.delete()
        return {"message": f"Employee {emp_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Employee not found")
    
class UpdateEmployee(BaseModel):
    name: str
    age: int

@app.put("/employees/{emp_id}")
def update_employee(emp_id: str, employee_data: UpdateEmployee):
    employee = Employee.objects.filter(id=emp_id).first()

    if employee:
        employee.update(name=employee_data.name, age=employee_data.age)
        return {"message": f"Employee {emp_id} updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Employee not found")


class NewUser(BaseModel):
    first_name: str
    last_name : str
    email: str
    username: str
    password:str





from passlib.context import CryptContext
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)



@app.post("/sign_up")
def sign_up(new_user:NewUser):
    user=User(username=new_user.username,
              password=get_password_hash(new_user.password))
    user.save()
    return {"message":"new user created"}


from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username,password):
   
    user=json.loads(User.objects.get(username=username).to_json())
    
    if user :
        password_check=pwd_context.verify(password,user['password'])
        return password_check
    else:
        return False




from datetime import datetime, timedelta
from jose import jwt
import secrets


SECRET_KEY=secrets.token_hex(32)
ALGORITHM= "HS256"

def create_access_token(data:dict,expires_delta:timedelta):
    to_encode = data.copy()

    expire = datetime.utcnow()+ expires_delta # token expirer apres 30 min
    to_encode.update({"exp":expire})
    #print(to_encode)
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.post("/token")
def login(form_data:OAuth2PasswordRequestForm=Depends()):
    username=form_data.username
    password = form_data.password

   
    if authenticate_user(username,password):
         access_token= create_access_token(
                               data={"sub":username},expires_delta=timedelta(minutes=30) )
         return {"access_token":access_token,"token_type":"bearer"}

    else:
        raise HTTPException(status_code=400, detail="Incorrect username or passxord")



@app.get("/")
def home(token:str=Depends(oauth2_scheme)):
    return{"token": token}
