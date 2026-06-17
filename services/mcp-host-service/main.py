import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import mcp_tools, search_local_papers, generate_paper_graphic

app = FastAPI(title="MCP Host Service - Local Llama Router")

# Initialize Local Llama as the primary model and router
try:
    llama_model = Ollama(model="llama3")
except Exception as e:
    print(f"Warning: Could not connect to local Llama. Is Ollama running? {e}")

class QueryRequest(BaseModel):
    question: str
    context_chunks: list[str] = []
    google_api_key: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "service": "mcp-host-service", "router": "Llama3 (Local)"}

@app.post("/route_query")
async def route_query(request: QueryRequest):
    if not llama_model:
        raise HTTPException(status_code=500, detail="Local Llama 3 model is not running.")

    # Routing Decision - use Llama to classify the intent
    router_prompt = f"""
    You are a routing assistant. Analyze the user's request.
    If the user explicitly asks for a chart, graphic, image, diagram, or visual plot, reply with exactly one word: VISUAL
    Otherwise, reply with exactly one word: TEXT
    
    User request: {request.question}
    Response:"""

    try:
        route_decision = llama_model.invoke(router_prompt).strip().upper()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local routing failed: {str(e)}")

    # Execute the Chosen Pipeline
    if "VISUAL" in route_decision:
        # Check if the optional Gemini key is available
        if not request.google_api_key:
            return {
                "answer": "The system determined this requires a graphic pipeline, but no Gemini API key was provided.",
                "pipeline_used": "None (Key Missing)",
                "routing_decision": "VISUAL",
                "image_url": None
            }

        try:
            os.environ["GOOGLE_API_KEY"] = request.google_api_key

            gemini_model = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                google_api_key=request.google_api_key
            )

            # Search the local library to get the actual data to the graphic
            context_data = search_local_papers.invoke(request.question)

            # Pass the retrieved data and the user's question to the graphic tool
            combined_prompt = f"Context Data: {context_data}\n\nUser Request: {request.question}"
            image_url_result = generate_paper_graphic.invoke(combined_prompt)

            # Use Gemini to write the final chat message
            response = gemini_model.invoke(
                f"You just generated a chart based on this data: '{context_data}'. Write a brief, professional one-sentence message telling the user their graphic is presented below."
            )

            raw_answer = response.content
            if isinstance(raw_answer, list):
                final_answer = raw_answer[0].get("text", "") if isinstance(raw_answer[0], dict) else str(raw_answer[0])
            else:
                final_answer = str(raw_answer)

            return {
                "answer": final_answer,
                "pipeline_used": "Gemini 3.5 Flash + QuickChart Engine",
                "routing_decision": "VISUAL",
                "image_url": image_url_result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini execution failed: {str(e)}")

    else:
        # Standard local text/RAG pipeline
        tool_result = search_local_papers.invoke(request.question)

        llama_prompt = f"""Context from library: {tool_result}
        
        Question: {request.question}
        Answer concisely using only the context provided:"""

        final_answer = llama_model.invoke(llama_prompt)
        used_model = "Llama 3 (Local Text Pipeline)"

    return {
        "answer": final_answer,
        "pipeline_used": used_model,
        "routing_decision": route_decision
    }