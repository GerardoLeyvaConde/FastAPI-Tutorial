from typing import Optional, List, Set, Dict
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Form, UploadFile, BackgroundTasks, Depends
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from datetime import datetime, time, timedelta
from uuid import UUID

app = FastAPI()


class Image(BaseModel):
    #validation of url
    url: HttpUrl
    name: str

#Model without flied
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    #Uncomment to the last part
    #tags: Set[str] = set()
    #image: Optional[List[Image]] = None

class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]

#Model used in the examples of MODEL-FIELD
#Field can declare validation and metadata inside of model
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

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

###FIRST STEPS
#Simple fuction to run the api
@app.get("/")
def read_root():
    return{"Hello" : "World"}
###

###PATH PARAMETERS
#Function to explain how to get the id of a Item(String)
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id} 

#parameters with type
#Function to explain how to get the id of a Item(Int)
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

#order matters
#Functions to explain the importance of the order of functions and not create ambiguities.
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

#models
#Function to explain the ways to uses the class Enum and get the values in two ways.
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning :^)"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    
    return {"model_name": model_name, "message": "Have some residuals"}

#path
#Function to explain to use the library file_path(Need to declare the path)
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
###

###QUERY PARAMETERS
#Function with default values to do the query
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]
    
#optional parameters
#Function where you can add an optional extra query
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Optional[str]= None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

#Query parameter type conversion
#Function with an optional extra query and a bool to specify if you want to see the long description of a Item
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
#Function to explain how to use the multiple values in a query
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
#Function to explain how to define parameters as required
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str, skip: int= 0, limit: Optional[int]= None):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item
###

###REQUEST BODY
#Function to explain how to crate an Item(Post)
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

#request body and path parameters
#Function to create an Item and taken from the request
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

#request body, path parameters and query
#Function to create an Item, taken from the request and a query parameter(optional)
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
###

#### QUERY PATAMETERS ANS STRING VALIDATIONS
#Function with validation query(min and max lenght)
@app.get("/items/")
async def read_item(q: Optional[str] = Query(None, min_length= 3, max_length= 50, regex= "^fixedquery$")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#default query
#Functions with default query(explicitly query parameter) and validation(min length)
@app.get("/items/")
async def read_item(q: Optional[str] = Query("fixedquery", min_length= 3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#required query
#Function with required query parameter
@app.get("/items/")
async def read_item(q: str = Query(..., min_length= 3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#parameter list query
#Function with a optional list of querys
@app.get("/items/")
async def read_item(q: Optional[List[str]] = Query(None)):
    query_items = {"q": q}
    return query_items

#parameter list query with default values
#Function with a default list of querys
@app.get("/items/")
async def read_item(q: List[str] = Query(["foo", "bar"])):
    query_items = {"q": q}
    return query_items

#more metadata
#Function to explain how add information about the parameters of the query
#(could be useful to show information to the user)
@app.get("/items/")
async def read_items(
    q: Optional[str] = Query(
        None,
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
    
#deprecating parameters
#Function to explain how use the "deprecated" variable to show just the more important variables
#OBSOLETE. The documentation recommends not use it.
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
#Functions ho explain how use the library "Path" like a query parameter.
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(..., title= "The ID of the item"),
    q: Optional[str] = Query(None, alias= "item-query"),):
    results= {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

#number validations greater,less or equal
#Function using path with validations
@app.get("/items/{item_id}")
async def read_items(item_id: int = Path(..., title="The ID of the item", ge= 0, le= 1000),
    q: Optional[str]= None):
    results= {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

#number validations(float)
#Function using path(optional) with validations
@app.get("/items/{item_id}")
async def read_items(
    *,
    item_id: int = Path(..., title="The ID of the item to get", ge=0, le=1000),
    q: str,
    size: float = Query(..., gt=0, lt=10.5)
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
###

###BODY MULTIPLE PARAMETERS
###IMPORTANT TO RUN. Have to comment the others "update_item" in this part to not overflow/overwrite and can run
#Function to update an item using the library "Path" and "Query"(both optionals) with validation
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
#Functions to update an item and add who user updated in the body of the json
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

#singular values in body
#Function to explain how add a new key in the body(json) but can't be treated like other body using "Body"
#(like in this example)
@app.put("/items/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: int = Body(...)):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

#multiple bodu params and query
#Function with additional query parameters and optional variables
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
#Funtion to explain the "embed" parameter. Add the key "Item" and inside the model contents
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item = Body(..., embed=True)):
    results = {"item_id": item_id, "item": item}
    return results

###BODY FIELDS
#Funtion to explain the library "Field"
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
#Example of List of models
@app.post("/images/multiple/")
async def create_multiple_images(images: List[Image]):
    return images

#bodies of arbitrary dicts
#Example to get Dict values
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights
###
