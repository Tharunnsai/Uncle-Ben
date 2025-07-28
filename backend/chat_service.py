from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from backend.calendar_tools import calendar_tools
from backend.database import db
import config

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]
    user_id: str
    conversation_id: str

class ChatService:
    def __init__(self):
        from pydantic import SecretStr
        self.llm = ChatGroq(
            api_key=SecretStr(config.GROQ_API_KEY),
            model=config.GROQ_MODEL,
            temperature=0.7
        )
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(calendar_tools)
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create the LangGraph conversation flow"""
        workflow = StateGraph(ChatState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tool_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: ChatState):
        """Main agent node for processing messages"""
        messages = state["messages"]
        
        # Add system message with current date context
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        system_message = SystemMessage(content=f"""
        You are a helpful AI assistant with access to Google Calendar appointment management tools.
        
        IMPORTANT: Today is {current_date} and the current time is {current_time}.
        Use this information when interpreting relative dates like "tomorrow", "next week", "today", etc.
        
        You can help users with:
        - Booking new appointments  
        - Viewing existing appointments
        - Cancelling appointments
        - Checking availability
        - Rescheduling appointments
        
        When users want to book appointments, ask for necessary details like:
        - Title/purpose of the appointment
        - Date and time (start and end)
        - Description (optional)
        
        When booking appointments, always convert times to ISO format (YYYY-MM-DDTHH:MM:SS) for the tools.
        
        Always use the available tools to interact with Google Calendar.
        Be conversational and helpful in your responses.
        
        Current user ID: {state["user_id"]}
        """)
        
        full_messages = [system_message] + messages
        response = self.llm_with_tools.invoke(full_messages)
        
        return {"messages": [response]}
    
    def _tool_node(self, state: ChatState):
        """Execute tools called by the agent"""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_results = []
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                # Find the tool
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Add user_id to tool arguments
                tool_args["user_id"] = state["user_id"]
                
                # Execute the tool
                for tool in calendar_tools:
                    if tool.name == tool_name:
                        try:
                            result = tool.invoke(tool_args)
                            tool_results.append({
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": result
                            })
                        except Exception as e:
                            tool_results.append({
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": f"Error executing tool: {str(e)}"
                            })
                        break
        
        # Create tool message
        if tool_results:
            from langchain_core.messages import ToolMessage
            tool_messages = [
                ToolMessage(
                    content=result["content"],
                    tool_call_id=result["tool_call_id"]
                )
                for result in tool_results
            ]
            return {"messages": tool_messages}
        
        return {"messages": []}
    
    def _should_continue(self, state: ChatState):
        """Determine if we should continue to tools or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    async def process_message(self, user_id: str, conversation_id: str, message: str) -> str:
        """Process a user message and return the assistant's response"""
        try:
            # Get conversation history
            messages = await db.get_conversation_messages(conversation_id)
            
            # Convert to LangChain messages
            langchain_messages = []
            for msg in messages:
                if msg.role == "user":
                    langchain_messages.append(HumanMessage(content=msg.content))
                else:
                    langchain_messages.append(AIMessage(content=msg.content))
            
            # Add new user message
            langchain_messages.append(HumanMessage(content=message))
            
            # Save user message to database
            await db.save_message(user_id, conversation_id, message, "user")
            
            # Process with graph
            initial_state = ChatState(
                messages=langchain_messages,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            result = self.graph.invoke(initial_state)
            
            # Get the final response
            final_messages = result["messages"]
            response_content = ""
            
            for msg in final_messages:
                if isinstance(msg, AIMessage) and not hasattr(msg, 'tool_calls'):
                    response_content = msg.content
                    break
            
            if not response_content and final_messages:
                # If no direct AI message, use the last message content
                last_msg = final_messages[-1]
                if hasattr(last_msg, 'content'):
                    if isinstance(last_msg.content, str):
                        response_content = last_msg.content
                    else:
                        response_content = str(last_msg.content)
                else:
                    response_content = "I'm ready to help you!"
            
            # Ensure response_content is a string and clean
            if not isinstance(response_content, str):
                response_content = str(response_content)
            
            # Final cleanup - remove any remaining reasoning patterns
            if response_content:
                response_content = response_content.strip()
                if not response_content or len(response_content) < 10:
                    response_content = "I'm here to help with your calendar appointments!"
            
            # Save assistant response to database
            await db.save_message(user_id, conversation_id, response_content, "assistant")
            
            return response_content
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            await db.save_message(user_id, conversation_id, error_msg, "assistant")
            return error_msg

# Global chat service instance
chat_service = ChatService()
