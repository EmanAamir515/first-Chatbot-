from fastapi import FastAPI ##endpoint file like tmrw 
from free_model import  ask_model_stream
from structure import mem
from DBservices import store_msg, get_convoHistory, delete_convo
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/get/{cid}")
async def get_hist(cid:str):
    return get_convoHistory(cid)

@app.post("/post_stream")
async def add_msg_stream(data:mem):
    ## store user msg with role/id after it got reply 
    store_msg(data.Cid, 'user', data.content)
    history = get_convoHistory(data.Cid) ##history of chat for context 
    
    def event_generator():
        full_response = ""

        for chunk in ask_model_stream(history):
            full_response += chunk
            yield f"data: {chunk}\n\n"
        
        store_msg(data.Cid, 'assistant', full_response)##saving full response at end
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.delete("/delete/{mid}")
def delete(cid:str):
    return delete_convo(cid)
# @app.post("/post")
# def add_msg(data:mem):
#     ## store user msg with role/id after it got reply 
#     store_msg(data.Cid, 'user', data.content)
    
#     history = get_convoHistory(data.Cid)
    
#     response = ask_model(history)
    
#     store_msg(data.Cid, 'assistant', response)

#     return { "response: " : response}



