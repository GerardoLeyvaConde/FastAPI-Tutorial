from typing import Optional, List, Set
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Form, UploadFile, BackgroundTasks, Depends
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from datetime import datetime, time, timedelta
from uuid import UUID

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str

#Model without flied

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    #tags: Set[str] = set()
    #image: Optional[List[Image]] = None
        class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }

class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]

#Model with flieds
"""
class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title= "The description of the item", max_length= 300
    )
    price: float = Field(..., gt= 0, description= "The price must be greater than 0")
    tax: Optional[float] = None
"""
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class User(BaseModel):
    username: str
    full_name: Optional[str]= None


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
###FIRST STEPS
@app.get("/")
def read_root():
    return{"Hello" : "World"}
###

###PATH PARAMETERS
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id} 

#parameters with type
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

#order matters
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
       
#models
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning :^)"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    
    return {"model_name": model_name, "message": "Have some residuals"}

#path
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
###

###QUERY PARAMETERS
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]
    
#optional parameters
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Optional[str]= None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

#Query parameter type conversion

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description :^)"}
        )
    return item

#Multiple path and query parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Optional[str] = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description :^)(2)"}
        )
    return item

#requiered query parameters
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str, skip: int= 0, limit: Optional[int]= None):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item
###

###REQUEST BODY
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

#request body and path parameters
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
###

#### QUERY PATAMETERS ANS STRING VALIDATIONS
@app.get("/items/")
async def read_item(
    q: Optional[str] = Query(None, min_length= 3, max_length= 50, regex= "^fixedquery$")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#default query
@app.get("/items/")
async def read_item(q: Optional[str] = Query("fixedquery", min_length= 3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#required query
@app.get("/items/")
async def read_item(q: str = Query(..., min_length= 3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#parameter list query
@app.get("/items/")
async def read_item(q: Optional[List[str]] = Query(None)):
    query_items = {"q": q}
    return query_items

#parameter list query with default values
@app.get("/items/")
async def read_item(q: List[str] = Query(["foo", "bar"])):
    query_items = {"q": q}
    return query_items
    
#Deprecatin parameters
@app.get("/items/")
async def read_item(
    q: Optional[str] = Query(
        None,
        alias= "item-query",
        title= "Query string",
        description= "Query for the item to search in the db",
        min_length= 3,
        max_length= 50,
        regex= "^fixedquery$",
        deprecated= True,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
###

###PATH PARAMETERS AND NUMERIC VALIDATIONS
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(..., title= "The ID of the item"),
    q: Optional[str] = Query(None, alias= "item-query"),):
    results= {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

#number validations greater,less or equal
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(..., title="The ID of the item", ge= 0, le= 1000),
    q: Optional[str]= None):
    results= {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
###

###BODY MULTIPLE PARAMETERS
@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int = Path(..., title="The ID of the item to get", ge=0, le=1000),
    q: Optional[str] = None,
    item: Optional[Item] = None):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

#multiple body parameters
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

#singular values in body
@app.put("/items/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: int = Body(...)):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

#multiple bodu params and query
@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item,
    user: User,
    importance: int = Body(..., gt=0),
    q: Optional[str] = None):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results

#embed a single parameter
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item = Body(..., embed=True)):
    results = {"item_id": item_id, "item": item}
    return results

###BODY FIELDS
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item = Body(..., embed=True)):
    results = {"item_id": item_id, "item": item}
    return results
###

### BODY NESTED MODELS
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

#offers
@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

#bodies of pure lists
@app.post("/images/multiple/")
async def create_multiple_images(images: List[Image]):
    return images

#bodies of arbitrary dicts
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights
###

###DECLARE REQUEST EXAMPLE DATA
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

#field additional arguments
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item = Body(
        ...,
        example={
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    ),):
    results = {"item_id": item_id, "item": item}
    return results

#multiples examples
@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item = Body(
        ...,
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
    ),):
    results = {"item_id": item_id, "item": item}
    return results
###

###EXTRA DATA TYPES
@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Optional[datetime] = Body(None),
    end_datetime: Optional[datetime] = Body(None),
    repeat_at: Optional[time] = Body(None),
    process_after: Optional[timedelta] = Body(None),):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }
###

###COOKIE PARAMETERS
@app.get("/items/")
async def read_items(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}
###

###HEADER PARAMETERS
@app.get("/items/")
async def read_items(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}

#automatic conversion
@app.get("/items/")
async def read_items(
    strange_header: Optional[str] = Header(None, convert_underscores=False)):
    return {"strange_header": strange_header}

#duplicate headers
@app.get("/items/")
async def read_items(x_token: Optional[List[str]] = Header(None)):
    return {"X-Token values": x_token}
###

###RESPONSE MODEL
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item

#return the unput data
@app.post("/user/", response_model=UserIn)
async def create_user(user: UserIn):
    return user

#return the output data
@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user

#response model parameters
@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include=["name", "description"])
async def read_item_name(item_id: str):
    return items[item_id]

@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]
###

###FORM
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
###

###REQUEST FORMS AND FILES
@app.post("/files/")
async def create_file(
    file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
###

###BACKGROUND TASKS
def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}

#deoendency injection
def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)

def get_query(background_tasks: BackgroundTasks, q: Optional[str] = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q

@app.post("/send-notification/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}
###