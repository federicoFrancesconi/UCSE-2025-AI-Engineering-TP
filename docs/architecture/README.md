# Architecture Documentation

Visual documentation of the system's evolution and design.

## Architecture Files

### Evolution

**`initial_high_level_architecture.puml`**  
Original simple design: User → LLM → SQL Tool → Database

**`high_level_architecture.puml`**  
Current high-level view with:
- Query classification (SQL/RAG/HYBRID)
- Multi-provider support (Ollama/Groq)
- RAG integration with ChromaDB
- Three query paths

### Implementation Details

**`initial_langgraph_architecture.puml`**  
Original LangGraph workflow:
- 5 basic nodes
- Single model provider
- SQL-only queries

**`langgraph_architecture.puml`**  
Current LangGraph implementation:
- Query classifier node
- Retrieve documents node (RAG)
- Multi-provider LLM support
- HYBRID query handling
- Error handling

**`rag_integrated_architecture.puml`**  
RAG integration design showing:
- ChromaDB vector store
- PDF summaries loading
- Semantic search flow
- HYBRID query merging

## Key Features Shown

✅ **Query Classification** - Routes to SQL, RAG, or both  
✅ **Multi-Provider** - Ollama (local) or Groq (cloud)  
✅ **RAG Integration** - Vector search in PDF summaries  
✅ **Hybrid Queries** - Combines database + documents  
✅ **Error Handling** - Graceful degradation

## Viewing Diagrams

### VS Code
1. Install "PlantUML" extension by jebbs
2. Open `.puml` file
3. Press `Alt + D` to preview

### Online
Visit: http://www.plantuml.com/plantuml/uml/

### Export
```bash
# Install PlantUML
sudo apt install plantuml

# Generate PNG
plantuml high_level_architecture.puml
```

## Architecture Evolution

```
v1: Simple SQL Agent
    User → LLM → Database
    
v2: LangGraph Workflow
    Multi-node pipeline with validation
    
v3: Multi-Provider
    Added Groq cloud support
    
v4: RAG Integration
    Added document retrieval from PDFs
    
v5: Hybrid Queries (Current)
    Combined SQL + RAG results
```

## Comparison: Initial vs Current

| Feature | Initial | Current |
|---------|---------|---------|
| Nodes | 1 (LLM) | 6 (Classify, SQL, Execute, RAG, Format, Error) |
| Providers | Ollama only | Ollama + Groq |
| Query Types | SQL only | SQL + RAG + HYBRID |
| Data Sources | Database | Database + Vector Store (PDFs) |
| Classification | None | LLM or Embedding-based |

---

*For implementation details, see [../README.md](../README.md)*
