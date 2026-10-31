import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv('E:/HopeAI_Learning/python_learning/Python_New/MCP/sqlite_mcp_langchain_gemini/.venv.env')
print ("Environment variables loaded from .env file")

# Initialize model and server parameters
model = ChatGoogleGenerativeAI(model="gemini-3.6-flash", api_key= os.environ["GOOGLE_API_KEY"])
server_params = StdioServerParameters(
    command="uv",
    args=[
        "--directory", 
        "E:/HopeAI_Learning/python_learning/Python_New/MCP/servers/servers-archived/src/sqlite",
        "run", 
        "mcp-server-sqlite",
        "--db-path",
        "E:/HopeAI_Learning/python_learning/Python_New/MCP/sqlite_mcp_langchain_gemini/database.db",
    ],
)

async def process_query(agent, query):
    response = await agent.ainvoke({"messages": query})
    return response["messages"][-1].content

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_agent(model, tools)
            
            print("SQLite Database Assistant (type 'exit' to quit)")
            
            while True:
                query = input("\nEnter your query: ").strip()
                if query.lower() == 'exit':
                    break
                if not query:
                    continue
                    
                print("\nProcessing...\n")
                response = await process_query(agent, query)
                if response and isinstance(response, list) and 'text' in response[0]:
                    answer_text = response[0]['text']
                else:
                    answer_text = str(response)
                print(f"\nAnswer: {answer_text}")

if __name__ == "__main__":
    asyncio.run(main())