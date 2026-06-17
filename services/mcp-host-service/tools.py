from langchain_core.tools import tool
import requests
import urllib.parse
from langchain_google_genai import ChatGoogleGenerativeAI

VECTOR_DB_URL = "http://localhost:8003"
IMAGE_GEN_URL = "http://localhost:8006/generate"

@tool
def search_local_papers(query: str) -> str:
    """
    Search the local vector database for text chunks from the user's PDFs.
    Use this tool when the user asks a question about the text content, methods, or conclusions of their papers.
    """
    try:
        # Ask the vector database for the top 3 most relevant chunks
        response = requests.post(
            f"{VECTOR_DB_URL}/search",
            json={"query": query, "limit": 3},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                return "No relevant information found in the local library. The database might be empty."

            # Format the mathematical matches into a readable context block for Llama
            context = "Here are the relevant excerpts from the user's library:\n\n"
            for doc in results:
                title = doc.get("title", "Unknown Document")
                content = doc.get("content", "")
                context += f"--- Source: {title} ---\n{content}\n\n"

            return context

        else:
            return f"Database Error: Received status code {response.status_code}"

    except Exception as e:
        return f"Error connecting to the local vector database: {str(e)}"

@tool
def generate_paper_graphic(combined_prompt: str) -> str:
    """
    Generate a visual graphic, diagram, or chart based on data extracted from the papers.
    Use this tool ONLY when the user explicitly asks for a graphic, chart, image, or visual representation.
    """
    try:
        # Initialize Gemini
        gemini_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

        # Instruct Gemini to act as a data visualization engineer
        chart_prompt = f"""
        You are a data visualization expert. Read the following context and user request.
        Extract the relevant numbers/data and create a valid JSON configuration for Chart.js.
        
        {combined_prompt}
        
        RULES:
        1. Output ONLY the raw JSON object. 
        2. Do NOT use markdown formatting like ```json or ```.
        3. Make the chart visually appealing (use colors like 'rgba(54, 162, 235, 0.5)').
        """

        # Get the response from Gemini
        response = gemini_model.invoke(chart_prompt)
        raw_content = response.content

        # Extract text whether LangChain returns a string or a list of blocks
        if isinstance(raw_content, list):
            # Extract the 'text' key from the first block in the list
            chart_json = raw_content[0].get("text", "") if isinstance(raw_content[0], dict) else str(raw_content[0])
        else:
            chart_json = str(raw_content)

        chart_json = chart_json.strip()

        # Failsafe: Strip markdown if Gemini disobeys rule 2
        if chart_json.startswith("```json"):
            chart_json = chart_json[7:-3]
        elif chart_json.startswith("```"):
            chart_json = chart_json[3:-3]

        # URL encode the JSON and append to the QuickChart open API
        encoded_json = urllib.parse.quote(chart_json.strip())
        real_image_url = f"https://quickchart.io/chart?c={encoded_json}"

        return real_image_url

    except Exception as e:
        return f"Error generating chart: {str(e)}"

mcp_tools = [search_local_papers, generate_paper_graphic]