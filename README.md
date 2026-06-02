# Local Library Assistant

## Description
**Local Library Assistant** is a distributed system that integrates with local reference managers like Zotero. It allows users to ask an AI chatbot questions about the papers and books in their local library. The system uses **Retrieval-Augmented Generation (RAG)** and the **Model Context Protocol (MCP)** to securely read local files and provide accurate, context-aware answers.

## System Architecture
The system is built as a set of isolated microservices. Document ingestion is managed via the **Saga Orchestration** pattern to ensure data consistency across the distributed nodes without relying on a two-phase commit.

## Repository Structure
* `client/zotero-plugin`: The user interface built with web technologies.
* `services/api-gateway`: The Java entry point that routes requests from the client.
* `services/saga-orchestrator`: The Python controller for the ingestion workflow.
* `services/document-metadata-service`: The Python service tracking document status.
* `services/text-extractor`: The Python service that parses and chunks PDF files.
* `services/vector-db-service`: The Python service running the local ChromaDB instance.
* `services/mcp-host-service`: The Python agent that queries the LLM and database.

## Getting Started
