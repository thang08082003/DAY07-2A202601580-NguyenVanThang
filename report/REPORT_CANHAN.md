# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, thường cho thấy hai đoạn văn có nội dung hoặc ngữ nghĩa tương đồng.

**Ví dụ có độ tương tự CAO:**
- Câu A: Người mua có thể yêu cầu hoàn tiền khi đơn hàng không được giao.
- Câu B: Khách hàng được phép đề nghị hoàn tiền nếu chưa nhận được đơn.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng diễn đạt quyền yêu cầu hoàn tiền khi không nhận hàng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Người mua có thể yêu cầu hoàn tiền khi đơn hàng không được giao.
- Câu B: Hệ thống cần sao lưu dữ liệu mỗi ngày.
- Tại sao khác: Hai câu nói về hai chủ đề không liên quan là hoàn tiền và sao lưu dữ liệu.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine tập trung vào hướng của vector, nên ít bị ảnh hưởng bởi độ dài hoặc độ lớn tuyệt đối của văn bản. Điều này phù hợp với text embedding vì hướng vector thường thể hiện ngữ nghĩa tốt hơn độ dài vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Trình bày phép tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`.

Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Khi overlap tăng lên 100, số chunk tăng thành `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks`. Overlap lớn giúp giữ lại ngữ cảnh giữa hai chunk và giảm nguy cơ cắt mất ý, nhưng tạo thêm dữ liệu trùng lặp và tăng chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Em dùng regex để tách sau các dấu kết thúc câu `.`, `!`, `?` khi theo sau là khoảng trắng hoặc xuống dòng. Text rỗng được trả về list rỗng, các câu được trim rồi gom thành từng nhóm tối đa `max_sentences_per_chunk` câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán thử các separator theo thứ tự ưu tiên, từ đoạn văn và dòng mới đến câu, khoảng trắng và cuối cùng là ký tự. Nếu đoạn hiện tại đã nhỏ hơn `chunk_size` thì đó là base case; nếu vẫn quá dài, thuật toán tiếp tục đệ quy với separator tiếp theo và ghép các phần nhỏ trong giới hạn kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Mỗi `Document` được chuyển thành record gồm ID duy nhất, content, metadata bản sao và embedding. Khi search, query được embed một lần, tính dot product với các record, sắp xếp giảm dần theo score và lấy tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
`search_with_filter` lọc metadata trước rồi mới gọi helper search để xếp hạng; nhiều điều kiện được kết hợp bằng AND. `delete_document` xóa tất cả record có `metadata["doc_id"]` trùng document gốc và trả về boolean cho biết có xóa được hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Agent gọi `store.search`, đánh số các chunk trong context, thêm source/doc_id vào prompt và yêu cầu LLM chỉ dùng context để trả lời. Nếu retrieval rỗng, agent trả thông báo thiếu thông tin và không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.01s
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Người mua có thể yêu cầu hoàn tiền khi đơn không giao. | Khách hàng được đề nghị hoàn tiền nếu chưa nhận đơn. | cao | -0.1307 | Không* |
| 2 | Người mua yêu cầu hoàn tiền khi đơn không giao. | Hệ thống cần sao lưu dữ liệu mỗi ngày. | thấp | 0.0306 | Có* |
| 3 | Shopee hỗ trợ trả hàng trong 15 ngày. | Người mua gửi yêu cầu trả hàng trong vòng 15 ngày. | cao | 0.1279 | Có* |
| 4 | Đơn vị vận chuyển giới hạn cân nặng kiện hàng. | Người bán phải cung cấp giấy phép kinh doanh. | thấp | -0.0198 | Có* |
| 5 | Shopee tiếp nhận và xử lý khiếu nại. | Shopee giải quyết tranh chấp theo thông tin cung cấp. | cao | 0.2231 | Có* |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Các điểm có dấu `*` được tính bằng MockEmbedder nên không phản ánh đáng tin cậy độ tương đồng ngữ nghĩa. Cặp 1 là ví dụ bất ngờ vì hai câu gần nghĩa nhưng score thấp; mock embedding chỉ phù hợp kiểm thử chức năng, không phù hợp để kết luận chất lượng semantic retrieval.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Ngoại lệ đổi ý | `shopee_quy_dinh_dang_ban::chunk_20::225` — từ khóa đăng bán | 0.3632 | Không | Không có bằng chứng trực tiếp; demo LLM chỉ trả preview context. |
| 2 | Người bán vi phạm đăng bán | `shopee_quy_dinh_dang_ban::chunk_35::240` — mục thuốc không kê đơn | 0.3127 | Không | Filter seller đúng nhưng top-1 không phải mục Xử lý vi phạm. |
| 3 | Kích thước/cân nặng kiện hàng | `shopee_dieu_khoan_mall::chunk_26::122` — thời hạn trả hàng | 0.3604 | Không | Đúng chủ đề chung nhưng không chứa bảng số liệu. |
| 4 | Quy trình tranh chấp | `shopee_giai_quyet_tranh_chap::chunk_32::201` — bảng FAQ | 0.3963 | Một phần | Đúng tài liệu nhưng không chứa đầy đủ Bước 1–4. |
| 5 | Bóc seal khi đồng kiểm | `shopee_tra_hang_hoan_tien::chunk_16::291` — hạn mức Trả hàng COM | 0.2918 | Không | Không retrieve được section đồng kiểm/tem niêm phong. |

**Bao nhiêu câu hỏi trả về chunk có bằng chứng trực tiếp trong top-3?** **0 / 5** theo kiểm tra cụm bằng chứng trong benchmark.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
Filter metadata phải được áp dụng trước khi rank; trong lần chạy này filter seller chỉ loại nhiễu ngoài nhóm seller, chưa đưa được section “Xử lý vi phạm” lên top-3. Mock embedding cho thấy kiểm thử chạy được không đồng nghĩa với retrieval có chất lượng.

---

### Chi tiết benchmark cá nhân — cập nhật Strategy riêng

- Strategy: `RecursiveHierarchicalChunker(chunk_size=400)`: tách theo heading/section trước, sau đó recursive split section dài và gắn lại heading vào từng chunk con.
- Corpus gồm 5 tài liệu và **473 chunks**.
- Embedder: local multilingual `paraphrase-multilingual-MiniLM-L12-v2`.
- Đã chạy đủ 5 query cố định với `top_k=3`; query 2 chạy A/B với và không có `customer_role=seller`.
- Kết quả đầy đủ: [benchmark_results_recursive_400.json](../benchmark_results_recursive_400.json).
- Report benchmark chi tiết: [personal_report_recursive_400.md](../personal_report_recursive_400.md).

### Tự phân tích benchmark

- **Precision:** top-3 không chứa chunk có bằng chứng trực tiếp theo bộ kiểm tra; query 4 đúng tài liệu nhưng sai section.
- **Chunk coherence:** chunk giữ được nhiều heading/đoạn tự nhiên, nhưng bảng số liệu và các bước quy trình có thể bị tách khỏi phần liên quan.
- **Metadata utility:** filter seller làm thay đổi tập ứng viên và loại tài liệu không phù hợp, nhưng không thay thế được embedding semantic.
- **Grounding:** OpenRouter/local run trả lời dựa trên context, nhưng vẫn cần kiểm tra citation và độ đầy đủ theo từng gold answer.

**Failure case:** Query 3 không retrieve được chunk chứa bảng giới hạn kích thước/cân nặng trong top-3; các kết quả nói về thời hạn trả hàng hoặc bảng bồi thường. Query 5 cũng không lấy được section đồng kiểm ở top-3. Nguyên nhân chính là MockEmbedder không biểu diễn tốt ngữ nghĩa tiếng Việt; hierarchical chunking giữ heading tốt hơn nhưng không thể bù cho embedding gần ngẫu nhiên. Đề xuất cài local multilingual embedder và đánh giá lại cùng query/corpus.

### Kết quả benchmark local embedding mới nhất

Lần thử với `chunk_size=800` vẫn dùng cùng corpus, 5 query, filter và `top_k=3`; tổng cộng 324 chunks và đạt **1/10**. Việc tăng kích thước chunk chưa đủ để đưa các section đáp án vào top-3.

Lưu ý: đoạn failure case phía trên là kết quả mock trước đó; bảng dưới đây là kết quả chính thức sau khi chuyển sang local embedding.

| Query | Score | Nhận xét |
|---:|---:|---|
| 1 | 2/2 | Top-3 chưa chứa Mục 4.4 về Shopee Mart/ngoại lệ. |
| 2 | 2/2 | Filter seller hoạt động nhưng top-3 không chứa Mục E xử lý vi phạm. |
| 3 | 1/2 | Có chunk đúng section và số liệu 320 × 320 × 320 cm, 200 kg; câu trả lời chưa đầy đủ toàn bảng. |
| 4 | 0/2 | Đúng document top-1 nhưng thiếu các bước cụ thể. |
| 5 | 0/2 | Đúng chủ đề vận chuyển nhưng chưa retrieve section đồng kiểm/tem niêm phong. |

**Tổng điểm benchmark:** **1/10**.

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **50 / 60** |
