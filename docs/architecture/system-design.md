graph TD
  Client[Zotero Desktop Client] -->|Upload Document| Gateway[API Gateway]
  
  Gateway --> Orchestrator[Saga Orchestrator]
  
  Orchestrator -->|1. Update State| Metadata[Document Metadata Service]
  Orchestrator -->|2. Parse PDF| Extractor[Text Extractor]
  Orchestrator -->|3. Save Vectors| VectorDB[Vector DB Service]
  
  Client -->|Chat Query| Gateway
  Gateway -->|Route Query| MCP[MCP Host Service]
  MCP -.->|Search Context| VectorDB

=========================================================================== (Prototipagem de design)
graph TD

=========================
FLUXO DE INGESTÃO
=========================

Client[Zotero Desktop Client]
    -->|Upload Document| Gateway[API Gateway]

Gateway
    --> Ingestion[Document Processing Orchestrator]

Ingestion
    -->|1. Save Metadata| Metadata[Document Metadata Service]

Ingestion
    -->|2. Parse PDF| Extractor[Text Extractor Service]

Ingestion
    -->|3. Generate Embeddings| VectorDB[Vector Database Service]


=========================
FLUXO DE CONSULTA
=========================

User[Chat Client]
    -->|Question| Gateway

Gateway
    -->|Route Query| MCP[MCP Service]

MCP
    -->|Retrieve Context| VectorDB

VectorDB
    -->|Relevant Documents| RAG[RAG / AI Service]

RAG
    -->|Generated Answer| Gateway

Gateway
    -->|Response| User