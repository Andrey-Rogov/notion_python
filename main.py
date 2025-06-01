from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import HumanMessage
from langchain_core.messages import ToolMessage
from langchain.chat_models import init_chat_model
from tools import get_current_time
import getpass
import os


def build_graph():
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Failed to read API key from environment.\n"
                                                       "Enter API key for Google Gemini: ")

    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    tools = [get_current_time]
    llm_with_tools = llm.bind_tools(tools)

    def call_agent(state: MessagesState) -> MessagesState:
        response = llm_with_tools.invoke(state["messages"])
        tool_messages = []
        for call in response.tool_calls:
            if call['name'] == 'get_current_time':
                tool_output = get_current_time.invoke("")
                tool_msg = ToolMessage(tool_call_id=call['id'], content=str(tool_output))
                tool_messages.append(tool_msg)

        final_response = state["messages"] + [response] + tool_messages
        return {"messages": final_response}

    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_node("model", call_agent)
    workflow.set_entry_point("model")
    workflow.add_edge("model", END)

    user_input = input('Enter your first message: ')
    message_history = []
    while user_input != 'Stop':
        message_history.append(HumanMessage(content=user_input))
        result = call_agent({"messages": message_history})
        response_msg = result["messages"][-1]
        message_history.append(response_msg)

        print("AI:", response_msg.content)
        user_input = input('You: ')


if __name__ == "__main__":
    with open('api_key.txt', 'r') as f:
        key = f.read()
        os.environ["GOOGLE_API_KEY"] = key
    if key:
        build_graph()
    else:
        print('Provide a GOOGLE_API_KEY in the api_key.txt file to start chatting')
