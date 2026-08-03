from __future__ import annotations

import json
import re
from pathlib import Path

from ingest import build_knowledge_base, load_documents
from main import _select_embedder, demo_llm, select_llm
from src.agent import KnowledgeBaseAgent
from src.chunking import ChunkingStrategyComparator, RecursiveChunker


DATA_DIR = "data/k4_ecommerce"
TOP_K = 3
RESULTS_PATH = Path("benchmark_results_recursive_400.json")
REPORT_PATH = Path("personal_report_recursive_400.md")
SHORT_REPORT_PATH = Path("report_canhan.md")


class RecursiveHierarchicalChunker:
    """Split Markdown sections first, then recursively split long sections."""

    def __init__(self, chunk_size: int = 400) -> None:
        self.chunk_size = chunk_size
        self._recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        headings = list(re.finditer(r"(?m)^#{1,6}\s+.+$", text))
        if not headings:
            return self._recursive.chunk(text)

        chunks: list[str] = []
        if headings[0].start() > 0:
            chunks.extend(self._recursive.chunk(text[: headings[0].start()]))

        for index, heading_match in enumerate(headings):
            heading = heading_match.group(0).strip()
            section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            body = text[heading_match.end() : section_end].strip()
            if not body:
                chunks.append(heading)
                continue

            body_size = max(1, self.chunk_size - len(heading) - 1)
            section_chunks = RecursiveChunker(chunk_size=body_size).chunk(body)
            chunks.extend(f"{heading}\n{piece}" for piece in section_chunks)

        return [chunk.strip() for chunk in chunks if chunk.strip()]

QUERIES = [
    {
        "type": "Ngoại lệ",
        "q": "Tuyệt đối KHÔNG hỗ trợ trả hàng vì lý do đổi ý đối với các mặt hàng nào?",
        "filter": None,
        "gold_answer": (
            "Trả hàng COM không áp dụng cho sản phẩm thuộc Shopee Mart và một số "
            "người bán/sản phẩm khác theo từng thời điểm dựa trên đánh giá của Shopee."
        ),
        "expected_doc_id": "shopee_tra_hang_hoan_tien",
        "expected_chunk_note": "Mục 4.4 - Các trường hợp loại trừ Trả hàng COM.",
        "evidence_phrases": ["Các trường hợp loại trừ Trả hàng COM", "Shopee Mart", "người bán và sản phẩm khác"],
    },
    {
        "type": "Test Bộ Lọc (Filter)",
        "q": "Là người bán, tôi vi phạm quy định đăng bán sản phẩm thì bị xử lý như thế nào?",
        "filter": {"customer_role": "seller"},
        "gold_answer": (
            "Tùy mức độ vi phạm, Shopee có thể xóa/khóa/tạm ẩn sản phẩm, giới hạn hoặc "
            "khóa tài khoản, yêu cầu bồi thường, cấn trừ tiền, khóa rút tiền, cung cấp "
            "thông tin hoặc khởi kiện."
        ),
        "expected_doc_id": "shopee_quy_dinh_dang_ban",
        "expected_chunk_note": "Mục E - Xử lý vi phạm.",
        "evidence_phrases": ["Xử lý vi phạm", "Xóa, khóa hoặc tạm ẩn hiển thị sản phẩm", "Giới hạn hoặc khóa tài khoản"],
    },
    {
        "type": "Số liệu",
        "q": "Kích thước và cân nặng tối đa của một kiện hàng khi giao qua Shopee là bao nhiêu?",
        "filter": None,
        "gold_answer": (
            "Giới hạn phụ thuộc phương thức vận chuyển. Ví dụ Hỏa Tốc tối đa "
            "60 x 60 x 60 cm và 30 kg; Trong ngày, Hỏa Tốc - Ưu Tiên, Shopee Xử Lý "
            "và Hàng Cồng Kềnh có thể đạt 320 x 320 x 320 cm và 200 kg."
        ),
        "expected_doc_id": "shopee_chinh_sach_van_chuyen",
        "expected_chunk_note": "Mục 2.1 - Giới hạn kích thước và cân nặng.",
        "evidence_phrases": ["Giới hạn kích thước và cân nặng", "60 × 60 × 60", "30 kg"],
    },
    {
        "type": "Quy trình",
        "q": "Nếu người mua và người bán không tự thỏa thuận được, quy trình nhờ Shopee giải quyết tranh chấp gồm những bước nào?",
        "filter": None,
        "gold_answer": (
            "Quy trình gồm: gửi khiếu nại; Shopee tiếp nhận và hỗ trợ; thu thập thông tin "
            "và xử lý; nếu vượt thẩm quyền thì chuyển vụ việc đến cơ quan nhà nước có thẩm quyền."
        ),
        "expected_doc_id": "shopee_giai_quyet_tranh_chap",
        "expected_chunk_note": "Các mục Bước 1 đến Bước 4 của quy trình.",
        "evidence_phrases": ["Bước 1: Gửi khiếu nại", "Bước 2: Shopee tiếp nhận và hỗ trợ", "Bước 3: Thu thập thông tin và xử lý", "Bước 4: Chuyển vụ việc"],
    },
    {
        "type": "Điều kiện",
        "q": "Tôi có được bóc tem (seal) của hộp điện thoại ra để thử khi đồng kiểm không?",
        "filter": None,
        "gold_answer": (
            "Chính sách vận chuyển không cho phép kiểm tra hàng trước khi thanh toán và nhận hàng; "
            "ngoại lệ là đơn hàng được đồng kiểm. Khi đồng kiểm, cần tuân thủ quy định và tình trạng "
            "tem niêm phong có thể ảnh hưởng đến xử lý/bồi thường."
        ),
        "expected_doc_id": "shopee_chinh_sach_van_chuyen",
        "expected_chunk_note": "Mục E.1 - Kiểm tra hàng trước khi thanh toán; các bảng về tem niêm phong.",
        "evidence_phrases": ["không cho phép Người Mua kiểm tra hàng trước khi thanh toán", "Ngoại lệ: Đơn hàng được đồng kiểm", "Rách tem niêm phong"],
    },
]

def print_baseline(documents) -> None:
    comparator = ChunkingStrategyComparator()
    print("=== BASELINE CHUNKING (front matter excluded) ===")
    for document in documents[:3]:
        comparison = comparator.compare(document.content, chunk_size=400)
        print(f"\nDocument: {document.metadata.get('doc_id')} | {document.metadata.get('title', document.id)}")
        print("Strategy         Count    Avg length")
        for name in ("fixed_size", "by_sentences", "recursive"):
            stats = comparison[name]
            print(f"{name:<16} {stats['count']:<8} {stats['avg_length']:.1f}")
            previews = [chunk.replace("\n", " ")[:120] for chunk in stats["chunks"][:2]]
            for preview in previews:
                print(f"  - {preview}")


def retrieve(store, item):
    if item["filter"] is None:
        return store.search(item["q"], top_k=TOP_K)
    return store.search_with_filter(item["q"], top_k=TOP_K, metadata_filter=item["filter"])


def evidence_check(item: dict, results: list[dict]) -> tuple[str, str]:
    terms = item["evidence_phrases"]
    for result in results:
        content = result.get("content", "")
        matched = [term for term in terms if term.lower() in content.lower()]
        if len(matched) == len(terms):
            rank = results.index(result) + 1
            return ("full" if rank == 1 else "partial"), f"chunk {result.get('id')} chứa đủ: {', '.join(matched)}"
        if matched:
            return "partial", f"chunk {result.get('id')} chỉ chứa một phần: {', '.join(matched)}"
    return "none", "Không có chunk top-3 chứa cụm bằng chứng yêu cầu."


def answer_is_grounded(answer: str, evidence_note: str) -> bool:
    if answer.startswith("[DEMO LLM]"):
        return False
    return bool(evidence_note and "chứa:" in evidence_note)


def prompt_from_results(question: str, results: list[dict]) -> str:
    blocks = []
    for index, result in enumerate(results, start=1):
        metadata = result.get("metadata") or {}
        source = metadata.get("doc_id") or metadata.get("source") or result.get("id") or "unknown"
        blocks.append(
            f"[{index}] Source: {source}\n"
            f"Content: {result.get('content', '').strip()}"
        )
    context = "\n\n".join(blocks)
    return (
        "Instruction:\n"
        "Use only the provided context to answer the question. If the context is insufficient, "
        "clearly state that there is not enough information. Cite relevant chunks using [1], [2], "
        "and so on.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )


def print_query(index: int, item: dict, results: list[dict], store_size: int, answer: str) -> dict:
    print("\n" + "=" * 60)
    print(f"QUERY {index} — {item['type']}")
    print(f"Question: {item['q']}")
    print(f"Filter: {item['filter']}")
    print("Strategy: RecursiveHierarchicalChunker")
    print("Parameters: chunk_size=400")
    print(f"Store size: {store_size} chunks")
    print(f"Gold answer: {item['gold_answer']}")
    print(f"Expected document: {item['expected_doc_id']}")
    print(f"Expected chunk note: {item['expected_chunk_note']}")
    print("\nTOP 3 RETRIEVAL")

    serialized_results = []
    for rank, result in enumerate(results, start=1):
        metadata = result.get("metadata") or {}
        content = result.get("content", "")
        print(f"\n[{rank}]")
        print(f"Score: {result.get('score', 0.0):.4f}")
        print(f"Chunk ID: {result.get('id', 'unknown')}")
        print(f"doc_id: {metadata.get('doc_id', 'unknown')}")
        print(f"chunk_index: {metadata.get('chunk_index', 'unknown')}")
        print(f"title: {metadata.get('title', 'unknown')}")
        print(f"source_url: {metadata.get('source_url', 'unknown')}")
        print(f"Preview: {content.replace(chr(10), ' ')[:250]}")
        serialized_results.append({
            "rank": rank,
            "score": result.get("score", 0.0),
            "id": result.get("id"),
            "doc_id": metadata.get("doc_id"),
            "chunk_index": metadata.get("chunk_index"),
            "preview": content.replace("\n", " ")[:250],
        })

    print("\nAGENT ANSWER")
    print(answer)
    return serialized_results


def main() -> None:
    documents = load_documents(DATA_DIR)
    print_baseline(documents)

    embedding_fn = _select_embedder()
    chunker = RecursiveHierarchicalChunker(chunk_size=400)
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedding_fn, chunker=chunker)
    llm_fn = select_llm()
    agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)

    print("\n=== PERSONAL STRATEGY BENCHMARK ===")
    print("Strategy: RecursiveHierarchicalChunker")
    print("Parameters: chunk_size=400")
    print(f"Corpus: {DATA_DIR}")
    print(f"Total chunks loaded: {store.get_collection_size()}")

    output = []
    report_rows = []
    ab_result = None
    for index, item in enumerate(QUERIES, start=1):
        results = retrieve(store, item)
        if item["filter"] is None:
            answer = agent.answer(item["q"], top_k=TOP_K)
        else:
            answer = llm_fn(prompt_from_results(item["q"], results))
        serialized_results = print_query(index, item, results, store.get_collection_size(), answer)
        evidence_level, evidence_note = evidence_check(item, results)
        has_evidence = evidence_level != "none"
        agent_correct = answer_is_grounded(answer, evidence_note)
        score = 2 if evidence_level == "full" and agent_correct else 1 if has_evidence else 0
        report_rows.append({
            "index": index,
            "type": item["type"],
            "score": score,
            "evidence": evidence_level,
            "agent_correct": agent_correct,
            "note": evidence_note,
        })
        output.append({
            "query_index": index,
            "type": item["type"],
            "question": item["q"],
            "filter": item["filter"],
            "strategy": "RecursiveHierarchicalChunker",
            "strategy_params": {"chunk_size": 400},
            "store_size": store.get_collection_size(),
            "gold_answer": item["gold_answer"],
            "expected_doc_id": item["expected_doc_id"],
            "expected_chunk_note": item["expected_chunk_note"],
            "results": serialized_results,
            "agent_answer": answer,
            "evidence_found": has_evidence,
            "evidence_note": evidence_note,
            "agent_correct": agent_correct,
            "rubric_score": score,
            "evidence_level": evidence_level,
        })

        if index == 2:
            unfiltered = store.search(item["q"], top_k=TOP_K)
            filtered_ids = [result.get("id") for result in results]
            unfiltered_ids = [result.get("id") for result in unfiltered]
            filtered_evidence, filtered_note = evidence_check(item, results)
            unfiltered_evidence, unfiltered_note = evidence_check(item, unfiltered)
            ab_result = {
                "filtered_ids": filtered_ids,
                "unfiltered_ids": unfiltered_ids,
                "filtered_evidence": filtered_evidence,
                "filtered_note": filtered_note,
                "unfiltered_evidence": unfiltered_evidence,
                "unfiltered_note": unfiltered_note,
                "filtered_answer": answer,
                "unfiltered_answer": llm_fn(prompt_from_results(item["q"], unfiltered)),
            }

    RESULTS_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    total_score = sum(row["score"] for row in report_rows)
    report_lines = [
        "# Báo cáo cá nhân — Recursive Hierarchical Chunking (chunk_size=400)",
        "",
        f"- Corpus: `{DATA_DIR}`",
        "- Strategy: `RecursiveHierarchicalChunker(chunk_size=400)` — heading trước, recursive split section dài",
        f"- Embedder: `{getattr(embedding_fn, '_backend_name', embedding_fn.__class__.__name__)}`",
        "- Giới hạn embedder: nếu dùng MockEmbedder, vector xác định nhưng gần như ngẫu nhiên theo toàn chuỗi, không phản ánh tốt ngữ nghĩa tiếng Việt.",
        f"- Tổng số chunk: **{store.get_collection_size()}**",
        "- top_k: **3**",
        "",
        "## Bảng chấm điểm",
        "",
        "| Query | Loại | Điểm | Có bằng chứng top-3 | Agent đúng | Ghi chú |",
        "|---:|---|---:|---|---|---|",
    ]
    for row in report_rows:
        report_lines.append(f"| {row['index']} | {row['type']} | {row['score']}/2 | {row['evidence']} | {'Có' if row['agent_correct'] else 'Không'} | {row['note']} |")
    report_lines += ["", f"**Tổng điểm: {total_score}/10**", "", "## Phân tích", "", "- **Retrieval precision:** đánh giá dựa trên việc top-3 có chứa các cụm bằng chứng cụ thể, không chỉ dựa vào `doc_id`.", "- **Chunk coherence:** một số chunk giữ được heading và nội dung liền kề, nhưng các bảng/số liệu có thể bị tách khỏi câu hỏi hoặc phần giải thích.", "- **Metadata utility:** filter `customer_role=seller` giới hạn đúng corpus seller trước khi rank, giúp loại tài liệu buyer/both khỏi kết quả.", "- **Grounding:** agent demo hiện chỉ trả preview prompt, nên không được xem là câu trả lời grounded đầy đủ; các điểm 2 cần một LLM trả lời và trích dẫn đúng bằng chứng.", "", "## Top-3 chi tiết", ""]
    for index, item in enumerate(QUERIES, start=1):
        row = output[index - 1]
        report_lines += [f"### Query {index} — {item['type']}", "", f"**Question:** {item['q']}", "", f"**Gold answer:** {item['gold_answer']}", "", f"**Expected document:** `{item['expected_doc_id']}` — {item['expected_chunk_note']}", "", f"**Agent answer:** {row['agent_answer']}", ""]
        for result in row["results"]:
            report_lines.append(f"- Rank {result['rank']}, score `{result['score']:.4f}`, doc `{result['doc_id']}`, chunk `{result['chunk_index']}`: {result['preview']}")
        report_lines.append("")
    report_lines += ["## A/B filter — Query 2", "", f"- Filtered IDs: `{ab_result['filtered_ids']}`", f"- Unfiltered IDs: `{ab_result['unfiltered_ids']}`", f"- Filtered evidence: **{ab_result['filtered_evidence']}** ({ab_result['filtered_note']})", f"- Unfiltered evidence: **{ab_result['unfiltered_evidence']}** ({ab_result['unfiltered_note']})", f"- Filtered agent answer: {ab_result['filtered_answer']}", f"- Unfiltered agent answer: {ab_result['unfiltered_answer']}", "- Nhận xét: filter được áp dụng trước rank và giới hạn kết quả trong tài liệu seller. Trong lần chạy này cả hai top-3 đều không chứa đủ bằng chứng về mục xử lý vi phạm; filter giảm phạm vi ứng viên nhưng không khắc phục giới hạn của mock embedding.", "", "## Failure case", "", "Query 5 là failure case chính: top-3 không chứa chunk của `shopee_chinh_sach_van_chuyen`, nơi có quy định về đồng kiểm và tem niêm phong. Các chunk được trả về thuộc tài liệu trả hàng, tranh chấp và đăng bán; chúng gần chủ đề thương mại điện tử nhưng không chứa bằng chứng trực tiếp. Nguyên nhân có thể là mock embedding xếp hạng theo vector gần như ngẫu nhiên và RecursiveChunker không bảo đảm bảng/section đồng kiểm nằm cùng chunk. Đề xuất: chạy lại bằng local multilingual embedder và thử chunk theo heading/section để giữ câu hỏi, ngoại lệ và bảng bằng chứng cùng nhau.", "", "## Kết luận", "", f"Strategy đã nạp {store.get_collection_size()} chunk và chạy đủ 5 query cố định, đạt **{total_score}/10** theo kiểm tra bằng chứng hiện tại. Đây là kết quả của một strategy riêng, chưa đủ cơ sở tuyên bố tốt nhất trước khi so sánh với các thành viên khác."]
    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    SHORT_REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nSaved benchmark results to {RESULTS_PATH}")
    print(f"Saved personal report to {REPORT_PATH}")
    print(f"Saved short personal report to {SHORT_REPORT_PATH}")
    print(f"Total rubric score: {total_score}/10")


if __name__ == "__main__":
    main()
