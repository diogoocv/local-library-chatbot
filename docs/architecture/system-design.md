graph TD
  Client[Zotero Desktop Client] -->|Upload Document| Gateway[API Gateway]
  
  Gateway --> Orchestrator[Saga Orchestrator]
  
  Orchestrator -->|1. Update State| Metadata[Document Metadata Service]
  Orchestrator -->|2. Parse PDF| Extractor[Text Extractor]
  Orchestrator -->|3. Save Vectors| VectorDB[Vector DB Service]
  
  Client -->|Chat Query| Gateway
  Gateway -->|Route Query| MCP[MCP Host Service]
  MCP -.->|Search Context| VectorDB
