**DOCUMENTAÇÃO** **TÉCNICA**

**Local** **Library** **Assistant**

**1.** **Identificação** **do** **Projeto**

**Nome** **do** **Projeto:** Local Library Assistant

**Disciplina:** Sistemas Distribuídos

**Tipo** **de** **Projeto:** Sistema Distribuído baseado em
Microsserviços

**Objetivo:** Desenvolver um assistente inteligente integrado ao Zotero
capaz de armazenar, processar e consultar artigos científicos através de
técnicas de Recuperação Aumentada por Geração (RAG), utilizando modelos
de Inteligência Artificial e banco de dados vetorial.

**2.** **Visão** **Geral** **do** **Sistema**

O Local Library Assistant é um sistema distribuído que permite ao
usuário importar artigos científicos em formato PDF para uma base
vetorial local e posteriormente realizar consultas utilizando linguagem
natural.

O sistema utiliza uma arquitetura baseada em microsserviços, onde cada
componente possui uma responsabilidade específica. A comunicação entre
os serviços ocorre através de requisições HTTP utilizando a framework
FastAPI.

Além das consultas textuais, o sistema também é capaz de gerar gráficos
e visualizações a partir dos dados encontrados nos documentos
armazenados.

**3.** **Arquitetura** **do** **Sistema**

O sistema segue o padrão de arquitetura distribuída baseada em
microsserviços.

**Componentes** **Principais**

**Cliente**

Plugin desenvolvido para o Zotero responsável pela interação com o
usuário.

**API** **Gateway**

Porta: 8000

Funções:

> • Receber requisições do cliente.
>
> • Encaminhar consultas para os serviços adequados.
>
> • Centralizar o acesso aos microsserviços.

**Saga** **Orchestrator**

Porta: 8005

Funções:

> • Coordenar o processo de ingestão de documentos.
>
> • Garantir consistência dos dados.
>
> • Executar rollback em caso de falhas.

**Metadata** **Service**

Porta: 8001

Funções:

> • Gerenciar metadados dos documentos.
>
> • Controlar estados da transação distribuída.

**Text** **Extractor** **Service**

Porta: 8002

Funções:

> • Extrair texto de arquivos PDF.
>
> • Dividir o conteúdo em fragmentos (chunks).

**Vector** **DB** **Service**

Porta: 8003

Funções:

> • Gerar embeddings vetoriais.
>
> • Armazenar vetores no ChromaDB.
>
> • Realizar buscas semânticas.

**MCP** **Host** **Service**

Porta: 8004

Funções:

> • Atuar como roteador inteligente.
>
> • Classificar intenções do usuário.
>
> • Direcionar consultas para os modelos adequados.

**RAG** **Service**

Funções:

> • Recuperar informações relevantes da base vetorial.
>
> • Construir contexto para geração de respostas.

**4.** **Tecnologias** **Utilizadas**

**Backend**

> • Python 3.12
>
> • FastAPI
>
> • Requests
>
> • Pydantic

**Inteligência** **Artificial**

> • LangChain
>
> • Ollama
>
> • Llama 3
>
> • Gemini 3.5 Flash

**Banco** **de** **Dados**

> • ChromaDB (Banco Vetorial)

**Processamento** **de** **Texto**

> • PyPDF
>
> • Sentence Transformers

**Frontend**

> • Plugin Zotero
>
> • TypeScript
>
> • Node.js

**Containers**

> • Docker
>
> • Docker Compose

**5.** **Estrutura** **do** **Projeto**

**Diretório** **Principal**

local-library-chatbot-main/

│

├── client/

├── data/

├── docs/

├── services/

├── docker-compose.yml

├── setup.sh

├── start-library.sh

└── README.md

**client/**

Contém o plugin responsável pela integração com o Zotero.

**data/**

Armazena os dados persistidos do ChromaDB.

**docs/**

Documentação da arquitetura.

**services/**

Contém todos os microsserviços do sistema.

**6.** **Fluxo** **de** **Ingestão** **de** **Documentos**

O processo de ingestão segue os seguintes passos:

> 1\. Usuário seleciona um PDF no Zotero.
>
> 2\. Plugin envia o arquivo ao API Gateway.
>
> 3\. Gateway encaminha para o Saga Orchestrator.
>
> 4\. Metadata Service registra os metadados.
>
> 5\. Text Extractor extrai o texto do PDF.
>
> 6\. O texto é dividido em chunks.
>
> 7\. Vector DB Service gera embeddings.
>
> 8\. Embeddings são armazenados no ChromaDB.
>
> 9\. Metadata Service atualiza o status para AVAILABLE.

Caso ocorra qualquer erro durante o processo, o Saga Orchestrator
executa rollback da transação.

**7.** **Fluxo** **de** **Consulta**

Quando o usuário realiza uma pergunta:

> 1\. Plugin envia a pergunta ao API Gateway.
>
> 2\. Gateway encaminha a requisição para o MCP Host Service.
>
> 3\. O Llama 3 classifica a intenção da consulta.

**Consulta** **Textual**

> • Busca documentos relacionados.
>
> • Recupera contexto do ChromaDB.
>
> • Gera resposta utilizando o modelo local.

**Consulta** **Visual**

> • Recupera dados relevantes.
>
> • Envia informações ao Gemini.
>
> • Gera gráficos através do QuickChart.

**8.** **Padrões** **de** **Sistemas** **Distribuídos** **Utilizados**

**API** **Gateway** **Pattern**

Centraliza todas as requisições externas em um único ponto de entrada.

Benefícios:

> • Redução do acoplamento.
>
> • Facilidade de manutenção.
>
> • Segurança centralizada.

**Saga** **Pattern**

Utilizado para garantir consistência em transações distribuídas.

Benefícios:

> • Tratamento de falhas.
>
> • Execução de rollback.
>
> • Consistência eventual.

**Microservices** **Architecture**

Cada funcionalidade é implementada em um serviço independente.

Benefícios:

> • Escalabilidade.
>
> • Modularidade.
>
> • Facilidade de manutenção.

**9.** **Banco** **de** **Dados** **Vetorial**

O sistema utiliza o ChromaDB como banco de dados vetorial.

Características:

> • Armazenamento de embeddings.
>
> • Busca semântica.
>
> • Recuperação eficiente de contexto.

Os embeddings são gerados utilizando o modelo:

all-MiniLM-L6-v2

da biblioteca Sentence Transformers.

**10.** **Comunicação** **Entre** **Serviços**

A comunicação ocorre através do protocolo HTTP utilizando APIs REST.

Exemplos de endpoints:

**API** **Gateway**

POST /query

POST /upload

**Metadata** **Service**

POST /metadata

PUT /metadata/{id}/complete

DELETE /metadata/{id}

**Vector** **DB** **Service**

POST /documents

POST /search

**Text** **Extractor** **Service**

POST /extract

**11.** **Requisitos** **para** **Execução**

**Software**

> • Python 3.12+
>
> • Node.js
>
> • npm
>
> • Docker

**Instalação**

chmod +x setup.sh

./setup.sh

**Inicialização**

chmod +x start-library.sh

./start-library.sh

**12.** **Resultados** **Esperados**

O sistema permite:

> • Armazenamento local de artigos científicos.
>
> • Consultas inteligentes utilizando linguagem natural.
>
> • Recuperação semântica de informações.
>
> • Geração automática de visualizações.
>
> • Preservação da privacidade dos dados dos usuários.

**13.** **Conclusão**

O Local Library Assistant demonstra a aplicação prática dos conceitos de
Sistemas Distribuídos através de uma arquitetura baseada em
microsserviços, API Gateway e Saga Pattern. A solução integra técnicas
modernas de Inteligência Artificial, bancos de dados vetoriais e
recuperação semântica de informações, oferecendo uma plataforma robusta
para apoio à pesquisa acadêmica.

A arquitetura adotada proporciona escalabilidade, modularidade e
tolerância a falhas, características fundamentais em sistemas
distribuídos modernos.
