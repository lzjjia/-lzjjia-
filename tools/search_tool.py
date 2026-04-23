import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

def get_search_tool(max_results: int = 3):
    return TavilySearch(
        max_results=max_results,
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
    )