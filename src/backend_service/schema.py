from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_input: str = Field(
        description="User input to the agent at the current turn.",
        examples=["What is the weather in Tokyo?"],
    )
    thread_id: str = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )


class ChatResponse(BaseModel):
    response: str = Field(
        description="Response of the agent for the user query.",
        examples=["Hello, world!"],
    )
