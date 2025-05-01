from typing import Dict

from fastapi import FastAPI, HTTPException

from agents import BookingAgent
from backend_service.schema import QueryRequest, ChatResponse

app = FastAPI(title="Booking Agent API")
booking_agent = BookingAgent()


@app.get("/", tags=['Health'])
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=['Chat'])
def query_langgraph(request: QueryRequest) -> ChatResponse:
    try:
        input_state = {
            "messages": [{"role": "user", "content": request.user_input}]
        }
        result = booking_agent.invoke(
            input_state, 
            config={"configurable": {"thread_id": request.thread_id}}
        )
        bot_response = result['messages'][-1]
        return ChatResponse(response=bot_response.content)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
