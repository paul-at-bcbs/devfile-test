from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class Item(BaseModel):
    name: str
    msg: str = None
    time: str

@app.post("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    print ({"item_id": item_id, "item": item})
    return {"item_id": item_id, "item": item}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
