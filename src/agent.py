from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "The knowledge base does not contain enough information to answer this question."

        context_blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            source = (
                metadata.get("doc_id")
                or metadata.get("source")
                or metadata.get("source_url")
                or result.get("id")
                or "unknown"
            )
            content = result.get("content", "").strip()
            context_blocks.append(
                f"[{index}] Source: {source}\n"
                f"Content: {content}"
            )

        context = "\n\n".join(context_blocks)
        prompt = (
            "Instruction:\n"
            "Use only the provided context to answer the question. "
            "If the context is insufficient, clearly state that there is not enough information. "
            "Cite relevant chunks using [1], [2], and so on.\n\n"
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{question}\n\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
