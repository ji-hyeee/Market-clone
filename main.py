from fastapi import FastAPI,UploadFile,Form,Response,Depends,jwt
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3

from pymongo import MongoClient

# # mongoDB 연결
# client = MongoClient("mongodb://localhost:27017/")

# # DB접근
# db = client["memo_db"]

# # 컬렉션접근
# collection = db["memo_col"]


con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

app = FastAPI()

SECRET = "super-secret"
manager = LoginManager(SECRET, "/login")

@manager.user_loader()
def query_user(data):
  WHERE_STATEMENTS = f"id='{data}'"
  if type(data) == dict:
    WHERE_STATEMENTS = f"""id='{data["id"]}'"""
    
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  user = cur.execute(f"""
                     SELECT * FROM users WHERE {WHERE_STATEMENTS}
                    """).fetchone()
  return user
  
# 로그인
@app.post("/login")
def login(id:Annotated[str,Form()],
          password:Annotated[str,Form()]):
  user = query_user(id)
  if not user:
    raise InvalidCredentialsException
  elif password != user["password"]:
    raise InvalidCredentialsException
  
  # 엑세스토큰 발급
  access_token = manager.create_access_token(data={
    "sub":{
      'id':user['id'],
      'name':user['name'],
      'email':user['email']
    }
  })
  
  return {"access_token":access_token}
  

# 회원가입
@app.post("/signup")
def signup(id:Annotated[str,Form()],
          password:Annotated[str,Form()],
          name:Annotated[str,Form()],
          email:Annotated[str,Form()]
          ):
  cur.execute(f"""
              INSERT INTO users(id,name,email,password)
              VALUES("{id}","{name}","{email}","{password}")
              """)
  con.commit()
  return "200"


@app.post("/items")
async def create_item(image:UploadFile,
                title:Annotated[str,Form()], 
                price:Annotated[int,Form()], 
                description:Annotated[str,Form()], 
                place:Annotated[str,Form()],
                insertAt:Annotated[int,Form()]
                ):
  
  image_bytes = await image.read()
  cur.execute(f"""
              INSERT INTO items(title, image, price, description, place,insertAt)
              VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
              """)
  con.commit()
  return '200'


@app.get("/items")
# 유저가 인증된 상태에서만 응답
async def get_items(user=Depends(manager)):
  # 컬럼명
  con.row_factory = sqlite3.Row
  
  cur = con.cursor()
  rows = cur.execute(f"""
                    SELECT * FROM items;
                    """).fetchall()
  return JSONResponse(jsonable_encoder(dict(row) for row in rows))


# 이미지 업데이트
@app.get("/images/{item_id}")
async def get_image(item_id):
  cur = con.cursor()
  
  # 16진법 이미지
  image_bytes=cur.execute(f"""
                          SELECt image FROM items WHERE id={item_id}
                          """).fetchone()[0]
  
  return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


