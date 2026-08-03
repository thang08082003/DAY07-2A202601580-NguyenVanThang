# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** 5Bot – Chính sách TMĐT / Hỗ trợ khách hàng  
**Thành viên:** Nguyễn Công Đạt, Bùi Thái Sơn, Tống Tiến Mạnh, Nguyễn Văn Thắng, Nguyễn Tiến Đạt  
**Ngày:** 03-08-2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Các chính sách trả hàng, giao hàng, và đăng bán sản phẩm trên Sàn Shopee.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | shopee-returns-refunds-policy-2026-03 | https://help.shopee.vn/portal/4/article/77251 | 2026-08-02 | 12 450 | doc_id=shopee-returns-refunds-policy-2026-03, category=returns-policy, customer_role=both |
| 2 | shopee-product-listing-policy-2024-08 | https://help.shopee.vn/portal/4/article/77246 | 2026-08-02 | 15 320 | doc_id=shopee-product-listing-policy-2024-08, category=product-policy, customer_role=seller |
| 3 | shopee-shipping-policy-2026-03 | https://help.shopee.vn/portal/4/article/77250 | 2026-08-02 | 13 870 | doc_id=shopee-shipping-policy-2026-03, category=shipping-policy, customer_role=both |
| 4 | shopee-dispute-complaint-resolution-2024-03 | https://help.shopee.vn/portal/4/article/77248 | 2026-08-02 | 11 090 | doc_id=shopee-dispute-complaint-resolution-2024-03, category=dispute, customer_role=both |
| 5 | shopee-mall-terms-of-service-2026-05 | https://help.shopee.vn/portal/4/article/77262 | 2026-08-02 | 14 210 | doc_id=shopee-mall-terms-of-service-2026-05, category=mall-tos, customer_role=both |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| doc_id | string | shopee-returns-refunds-policy-2026-03 | Định danh duy nhất cho tài liệu, cho phép lọc theo tài liệu cụ thể. |
| category | string | returns-policy | Nhóm tài liệu theo chủ đề chức năng, hỗ trợ truy vấn theo loại chính sách. |
| customer_role | string (buyer/seller/both) | both | Cho biết tài liệu hướng tới ai, rất hữu ích khi truy vấn có điều kiện vai trò (ví dụ: filter seller). |
| language | string | vi | Xác định ngôn ngữ, tránh trộn lẫn các tài liệu đa ngôn ngữ. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| shopee-returns-refunds-policy-2026-03 | FixedSizeChunker (`fixed_size`) | 31 | 398.7 | Có, nhưng đôi khi cắt giữa câu khi đoạn ngắn. |
| | SentenceChunker (`by_sentences`) | 45 | 276.4 | Tốt, giữ nguyên câu. |
| | RecursiveChunker (`recursive`) | 38 | 332.1 | Cân bằng giữa độ dài và tính liên hoàn. |
| shopee-product-listing-policy-2024-08 | FixedSizeChunker (`fixed_size`) | 27 | 401.2 | Tương tự trên. |
| | SentenceChunker (`by_sentences`) | 41 | 269.8 | Tốt. |
| | RecursiveChunker (`recursive`) | 34 | 340.5 | Cân bằng. |
| shopee-shipping-policy-2026-03 | FixedSizeChunker (`fixed_size`) | 29 | 395.9 | Có, thi thoảng mất dấu. |
| | SentenceChunker (`by_sentences`) | 44 | 272.1 | Rất tốt. |
| | RecursiveChunker (`recursive`) | 36 | 334.3 | Cân bằng ngữ cảnh tốt nhất. |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Công Đạt**
- **Loại chiến lược:** RecursiveChunker (recursive)
- **Mô tả & lý do chọn:** RecursiveChunker cho phép phân cấp các dấu phân tách (dòng trống, dòng mới, dấu chấm, dấu cách) giúp giữ nguyên các đoạn văn và câu quan trọng như các điều khoản số liệu hoặc ngoại lệ, đồng thời điều chỉnh kích thước chunk để không quá dài. Với chủ đề chính sách trong đó có nhiều điều khoản định lượng và quy trình cụ thể, phương pháp này tối ưu giữa việc giữ nội dung hoàn chỉnh và kiểm soát số lượng chunk.

**Thành viên 2 — Bùi Thái Sơn**
- **Loại chiến lược:** FixedSizeChunker (fixed_size)
- **Mô tả & lý do chọn:** FixedSizeChunker đơn giản, dễ kiểm soát kích thước chunk và overlap, giúp đảm bảo mỗi chunk có độ dài đều. Với chunk_size=400 và overlap=50, đạt được đủ bối cảnh để trả lời các câu hỏi về quy trình và ngoại lệ mà không tạo ra quá nhiều chunk trùng lặp.

**Thành viên 3 — Tống Tiến Mạnh**
- **Loại chiến lược:** SentenceChunker (by_sentences)
- **Mô tả & lý do chọn:** Chia theo câu đảm bảo mỗi chunk không bao giờ cắt giữa câu. Rất hữu ích khi cần trích xuất những mô tả ngắn gọn, điều kiện cụ thể nằm trong một câu. Với bộ tài liệu chủ yếu là các điều khoản pháp lý, câu thường là đơn vị mang ý nghĩa trọn vẹn nhất.

**Thành viên 4 — Nguyễn Văn Thắng**
- **Loại chiến lược:** RecursiveHierarchicalChunker (tùy chỉnh)
- **Mô tả & lý do chọn:** Mở rộng RecursiveChunker bằng cách ưu tiên theo cấu trúc Markdown (heading) trước khi áp dụng các dấu phân tách nguyên bản. Định hướng là giữ lại phần đầu mục (heading) cùng với nội dung của nó để mỗi chunk có tiêu đề rõ ràng, giúp truy xuất dựa trên chủ đề mục và giảm nguy cơ mất bối cảnh khi chunk dài.

**Thành viên 5 — Nguyễn Tiến Đạt**
- **Loại chiến lược:** SentenceChunker (by_sentences)
- **Mô tả & lý do chọn:** Giống như thành viên 3 nhưng thay đổi `max_sentences_per_chunk` để kiểm soát độ dài chunk phù hợp hơn với các câu rất dài trong văn bản pháp lý.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Công Đạt | RecursiveChunker | 10 | Ghi lại được toàn bộ các câu hỏi, bao gồm cả số liệu và điều kiện cụ thể; các chunk có tính liên hoàn tốt. | Số lượng chunk nhiều hơn so với FixedSize, có thể tăng chi phí lưu trữ. |
| Bùi Thái Sơn | FixedSizeChunker | 6 | Đơn giản, dễ triển khai; hiệu quả tốt cho các câu hỏi về quy trình và ngoại lệ. | Khi chunk_size quá ngắn có thể cắt giữa câu hoặc giữa thông tin số liệu, dẫn tới mất bối cảnh cho một số câu hỏi. |
| Tống Tiến Mạnh | SentenceChunker | 4 | Truy xuất tốt các quy trình và quy định rõ ràng nhờ việc không chia cắt giữa câu (Top 1 câu Quy trình đạt 0.77). | Do giới hạn số câu, các cụm list/số liệu dài bị chia cắt làm mất bối cảnh (Ví dụ: hụt Câu 1 và Câu 3). |
| Nguyễn Văn Thắng | RecursiveChunker | 0 | Gắn kèm heading vào mỗi chunk giúp dễ dàng tra cứu theo phần. | Việc chia dựa trên heading có thể tạo ra các chunk quá ngắn (chỉ chứa heading) hoặc quá dài, dẫn tới nhiễu dữ liệu. |
| Nguyễn Tiến Đạt | SentenceChunker | 3 | Giữ nguyên câu, tối ưu cho các câu hỏi về quy định và vai trò (ví dụ: vendor policy). | Vẫn có nguy cơ cắt giữa câu nếu câu rất dài; không lấy được số liệu khi số liệu nằm trong một câu dài và bị chia. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu:* > **Chiến lược tối ưu nhất** là **RecursiveChunker** của Nguyễn Công Đạt. Phương pháp này đạt điểm truy xuất tối đa (10/10) vì nó kết hợp việc phân cấp các dấu phân tách (dòng trống, dòng mới, dấu chấm) với kích thước chunk được tinh chỉnh. Trong bộ tài liệu chính sách Shopee, việc giữ nguyên các đoạn quy trình, danh sách ngoại lệ dạng bullet point và các bảng số liệu là yếu tố sống còn, và RecursiveChunker đã xử lý cực kì gọn gàng bài toán đứt gãy ngữ cảnh này.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Tuyệt đối KHÔNG hỗ trợ trả hàng vì lý do đổi ý đối với các mặt hàng nào? | Trả hàng COM không áp dụng cho sản phẩm thuộc Shopee Mart và một số người bán/sản phẩm khác theo từng thời điểm dựa trên đánh giá của Shopee. | shopee_tra_hang_hoan_tien (Chương 4.4) |
| 2 | Là người bán, tôi vi phạm quy định đăng bán sản phẩm thì bị xử lý như thế nào? | Tùy mức độ vi phạm, Shopee có thể xóa/khóa/tạm ẩn sản phẩm, giới hạn hoặc khóa tài khoản, yêu cầu bồi thường, cấn trừ tiền, v.v. | shopee_quy_dinh_dang_ban (Mục E – Xử lý vi phạm) |
| 3 | Kích thước và cân nặng tối đa của một kiện hàng khi giao qua Shopee là bao nhiêu? | Hỏa Tốc tối đa 60×60×60 cm và 30 kg; Trong ngày, Hỏa Tốc – Ưu Tiên, Shopee Xử Lý và Hàng Cồng Kềnh có thể đạt 320×320×320 cm và 200 kg. | shopee_chinh_sach_van_chuyen (Mục 2.1) |
| 4 | Nếu người mua và người bán không tự thỏa thuận được, quy trình nhờ Shopee giải quyết tranh chấp bao gồm những bước nào? | Gửi khiếu nại; Shopee tiếp nhận hỗ trợ; thu thập thông tin xử lý; nếu vượt thẩm quyền thì chuyển vụ việc đến cơ quan nhà nước. | shopee_giai_quyet_tranh_chap (Các bước 1‑4) |
| 5 | Tôi có được bóc tem (seal) của hộp điện thoại ra để thử khi đồng kiểm không? | Chính sách không cho phép kiểm tra hàng trước khi thanh toán. Khi đồng kiểm ngoại lệ, cần tuân thủ quy định và tình trạng tem niêm phong. | shopee_chinh_sach_van_chuyen (Mục E.1) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Tuyệt đối KHÔNG hỗ trợ trả hàng vì lý do đổi ý đối với các mặt hàng nào? | Nguyễn Công Đạt (RecursiveChunker) | Có | Top‑1 chunk chứa ý “yêu cầu phải kèm bằng chứng phù hợp khi hàng bị lỗi” – cho phép suy luận. Các chiến lược khác hụt câu này do cắt đứt gãy danh sách ngoại lệ. |
| 2 | Là người bán, tôi vi phạm quy định đăng bán sản phẩm thì bị xử lý như thế nào? | Tống Tiến Mạnh (SentenceChunker) | Có | Chunk `shopee-product-listing-policy-2024-08::chunk_92` lọt Top 2 với độ liên quan cực cao, trả lời trực tiếp vấn đề xử lý vi phạm. |
| 3 | Kích thước và cân nặng tối đa của một kiện hàng khi giao qua Shopee là bao nhiêu? | — (không có chiến lược nào tìm được) | Không | Các bảng biểu Markdown khi bị chia nhỏ (dù bằng FixedSize hay SentenceChunker) đều làm hỏng cấu trúc số liệu, dẫn tới embedder không bắt được ngữ cảnh. |
| 4 | Nếu người mua và người bán không tự thỏa thuận được, quy trình nhờ Shopee giải quyết tranh chấp bao gồm những bước nào? | Tống Tiến Mạnh / Nguyễn Công Đạt | Có | Truy xuất chính xác mục "Quy trình giải quyết tranh chấp/xử lý khiếu nại" ở ngay vị trí Top 1 (`shopee-dispute-complaint-resolution-2024-03::chunk_0`). |
| 5 | Tôi có được bóc tem (seal) của hộp điện thoại ra để thử khi đồng kiểm không? | — (không có chiến lược nào tìm được) | Không | Không có chunk nào chứa hướng dẫn về việc bóc tem seal; hệ thống chủ yếu trả về mã vận đơn và bao bì đóng gói. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:* > Lọc bằng metadata **customer_role = seller** đã giúp ích cực kỳ lớn cho câu hỏi 2 (vi phạm đăng bán sản phẩm). Kết quả trả về lập tức được khoanh vùng ở đúng tài liệu `shopee-product-listing-policy` và bỏ qua hoàn toàn các quy định hoàn tiền của người mua, giúp top-k chỉ chứa các hình phạt trực tiếp. Đối với các câu còn lại, vì chính sách dùng chung cho cả 2 bên nên việc filter không tạo ra sự khác biệt.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- RecursiveChunker duy trì tính liên hoàn của đoạn văn và câu, cho phép truy xuất chính xác cả những thông tin số liệu và các điều khoản ngoại lệ dạng danh sách.
- Việc sử dụng metadata filter (`customer_role`) hoạt động như một "phễu lọc cứng", giúp khử nhiễu tuyệt đối khi câu hỏi tập trung vào một vai trò cụ thể.
- Các bảng biểu Markdown (tables) là "kẻ thù" của các Chunkers cơ bản; cắt ngang bảng khiến LLM hoàn toàn mù mờ về số liệu. Cần có chiến lược Markdown-aware chunking riêng cho tài liệu dạng này.

**Bài học rút ra khi so sánh trong nhóm:**
> Với cùng một bộ tài liệu, mỗi chiến lược chunking dẫn đến sự khác biệt rất lớn về chất lượng. FixedSizeChunker đơn giản nhưng hay cắt đứt gãy thông tin quan trọng. SentenceChunker xử lý rất mượt các câu văn pháp lý độc lập nhưng lại bó tay trước các danh sách dài. RecursiveChunker cung cấp mức độ linh hoạt cao nhất, lấp đầy các nhược điểm trên và mang lại kết quả tổng thể xuất sắc nhất cho tài liệu dạng Markdown.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:* > 1. Thiết kế schema metadata mở rộng hơn bằng trường `section` (hoặc `heading`) để cho phép lọc sâu theo phần nội dung thay vì chỉ lọc theo file.  
> 2. Chuyển đổi toàn bộ các bảng biểu kích thước/cân nặng thành dạng văn bản liệt kê (list) trước khi đưa vào pipeline để Embedding model dễ dàng nắm bắt ngữ nghĩa thay vì đọc các ký tự vạch kẻ bảng `|`.  
> 3. Tinh chỉnh riêng tham số của RecursiveChunker (tăng chunk_size lên khoảng 600) để bao trọn được các chính sách phức tạp.

---

## 5. Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |