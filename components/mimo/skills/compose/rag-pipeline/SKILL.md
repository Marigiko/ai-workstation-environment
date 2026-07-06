---
name: compose-rag-pipeline
description: Compose workflow for building RAG (Retrieval-Augmented Generation) pipelines with vector search and LLM integration
---

# Compose Workflow: RAG Pipeline

You are orchestrating the creation of a RAG pipeline.

## Phase 1: Specification
Gather requirements:
- Document sources (PDF, web, database)
- Embedding model choice
- Vector database (Qdrant, Pinecone, etc.)
- LLM provider for generation
- Retrieval strategy (similarity, hybrid)

## Phase 2: Planning
Break down into tasks:
1. Document ingestion pipeline
2. Text chunking strategy
3. Embedding generation
4. Vector storage setup
5. Retrieval implementation
6. LLM integration
7. Response formatting
8. Evaluation metrics

## Phase 3: Execution
Execute tasks in order:
- Implement document loaders
- Build chunking logic
- Set up embedding pipeline
- Configure vector database
- Implement retrieval
- Integrate LLM
- Add response formatting

## Phase 4: Optimization
- Tune chunk size and overlap
- Optimize retrieval parameters
- Implement caching
- Add hybrid search (if needed)
- Benchmark performance

## Phase 5: Evaluation
- Test retrieval accuracy
- Measure response quality
- Check latency metrics
- Validate against test queries

## Phase 6: Documentation
- Architecture diagram
- Configuration guide
- Usage examples
- Performance benchmarks
- Troubleshooting guide

## Deliverables
- Working RAG pipeline
- Document ingestion system
- Vector search integration
- LLM response generation
- Evaluation metrics
- Complete documentation

Use `@perf-analyzer` for optimization, `@infra` for deployment setup.
