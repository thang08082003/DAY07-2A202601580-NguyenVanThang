# Báo cáo cá nhân — Recursive Hierarchical Chunking (chunk_size=800)

- Corpus: `data/k4_ecommerce`
- Strategy: `RecursiveHierarchicalChunker(chunk_size=800)` — heading trước, recursive split section dài
- Embedder: `mock embeddings fallback`
- Giới hạn embedder: nếu dùng MockEmbedder, vector xác định nhưng gần như ngẫu nhiên theo toàn chuỗi, không phản ánh tốt ngữ nghĩa tiếng Việt.
- Tổng số chunk: **324**
- top_k: **3**

## Bảng chấm điểm

| Query | Loại | Điểm | Có bằng chứng top-3 | Agent đúng | Ghi chú |
|---:|---|---:|---|---|---|
| 1 | Ngoại lệ | 0/2 | none | Không | Không có chunk top-3 chứa cụm bằng chứng yêu cầu. |
| 2 | Test Bộ Lọc (Filter) | 0/2 | none | Không | Không có chunk top-3 chứa cụm bằng chứng yêu cầu. |
| 3 | Số liệu | 0/2 | none | Không | Không có chunk top-3 chứa cụm bằng chứng yêu cầu. |
| 4 | Quy trình | 0/2 | none | Không | Không có chunk top-3 chứa cụm bằng chứng yêu cầu. |
| 5 | Điều kiện | 0/2 | none | Không | Không có chunk top-3 chứa cụm bằng chứng yêu cầu. |

**Tổng điểm: 0/10**

## Phân tích

- **Retrieval precision:** đánh giá dựa trên việc top-3 có chứa các cụm bằng chứng cụ thể, không chỉ dựa vào `doc_id`.
- **Chunk coherence:** một số chunk giữ được heading và nội dung liền kề, nhưng các bảng/số liệu có thể bị tách khỏi câu hỏi hoặc phần giải thích.
- **Metadata utility:** filter `customer_role=seller` giới hạn đúng corpus seller trước khi rank, giúp loại tài liệu buyer/both khỏi kết quả.
- **Grounding:** agent demo hiện chỉ trả preview prompt, nên không được xem là câu trả lời grounded đầy đủ; các điểm 2 cần một LLM trả lời và trích dẫn đúng bằng chứng.

## Top-3 chi tiết

### Query 1 — Ngoại lệ

**Question:** Tuyệt đối KHÔNG hỗ trợ trả hàng vì lý do đổi ý đối với các mặt hàng nào?

**Gold answer:** Trả hàng COM không áp dụng cho sản phẩm thuộc Shopee Mart và một số người bán/sản phẩm khác theo từng thời điểm dựa trên đánh giá của Shopee.

**Expected document:** `shopee_tra_hang_hoan_tien` — Mục 4.4 - Các trường hợp loại trừ Trả hàng COM.

**Agent answer:** There is not enough information to answer the question regarding which items are not supported for return due to change of mind. The provided context does not specify any particular items or categories that are excluded from return for this reason.

- Rank 1, score `0.3788`, doc `shopee_chinh_sach_van_chuyen`, chunk `80`: # Gợi ý chunking cho RAG `shipping_claim_deadline`            Thời hạn khiếu nại      Mất hàng hoàn trả phải                                                                khiếu nại trong bao                                                           
- Rank 2, score `0.3447`, doc `shopee_dieu_khoan_mall`, chunk `30`: ## 11.2. Bưu kiện bị hư hại Nếu bưu kiện:  - Có dấu hiệu đã bị mở; - Bị ướt; - Bị rách; - Bị móp méo; - Bị hư hại;  Người Bán phải:  1. Từ chối nhận hàng. 2. Thông báo ngay cho Shopee trong vòng **24 giờ kể từ thời điểm nhận hàng**.  ---
- Rank 3, score `0.3334`, doc `shopee_tra_hang_hoan_tien`, chunk `27`: ## 7. Trách nhiệm về chi phí vận chuyển hoàn trả của Người Bán

### Query 2 — Test Bộ Lọc (Filter)

**Question:** Là người bán, tôi vi phạm quy định đăng bán sản phẩm thì bị xử lý như thế nào?

**Gold answer:** Tùy mức độ vi phạm, Shopee có thể xóa/khóa/tạm ẩn sản phẩm, giới hạn hoặc khóa tài khoản, yêu cầu bồi thường, cấn trừ tiền, khóa rút tiền, cung cấp thông tin hoặc khởi kiện.

**Expected document:** `shopee_quy_dinh_dang_ban` — Mục E - Xử lý vi phạm.

**Agent answer:** Không có đủ thông tin trong ngữ cảnh để trả lời câu hỏi về cách xử lý vi phạm quy định đăng bán sản phẩm. Các quy định chỉ nêu rõ các hành vi không được thực hiện mà không đề cập đến hình thức xử lý vi phạm [1].

- Rank 1, score `0.3283`, doc `shopee_quy_dinh_dang_ban`, chunk `13`: ## 3. Các hành vi không được thực hiện 5. So sánh trực tiếp về giá cả, chất lượng, hiệu quả sử dụng sản phẩm, hàng hóa, dịch vụ của mình với sản phẩm, hàng hóa, dịch vụ cùng loại của tổ chức, cá nhân khác.  6. Có nội dung cạnh tranh không lành mạnh t
- Rank 2, score `0.2633`, doc `shopee_quy_dinh_dang_ban`, chunk `29`: # 3. Quy định riêng với một số ngành hàng
- Rank 3, score `0.2532`, doc `shopee_quy_dinh_dang_ban`, chunk `61`: ## 4.4. Thông tin liên hệ Thông tin sản phẩm không bao gồm:  - Số điện thoại; - Thông tin liên lạc nhằm mục đích quảng cáo; - Thông tin dẫn người dùng tới website khác.

### Query 3 — Số liệu

**Question:** Kích thước và cân nặng tối đa của một kiện hàng khi giao qua Shopee là bao nhiêu?

**Gold answer:** Giới hạn phụ thuộc phương thức vận chuyển. Ví dụ Hỏa Tốc tối đa 60 x 60 x 60 cm và 30 kg; Trong ngày, Hỏa Tốc - Ưu Tiên, Shopee Xử Lý và Hàng Cồng Kềnh có thể đạt 320 x 320 x 320 cm và 200 kg.

**Expected document:** `shopee_chinh_sach_van_chuyen` — Mục 2.1 - Giới hạn kích thước và cân nặng.

**Agent answer:** There is not enough information provided in the context to answer the question about the maximum size and weight of a package when shipping through Shopee.

- Rank 1, score `0.3148`, doc `shopee_quy_dinh_dang_ban`, chunk `8`: ### 1.3. Chứng từ cung cấp cho Shopee Tất cả chứng từ mà Người Bán được yêu cầu cung cấp phải:  - Được scan từ chứng từ gốc; - Không được làm giả; - Không được chỉnh sửa; - Không được tẩy xóa.  Người Bán phải đảm bảo và cam kết về tính xác thực của c
- Rank 2, score `0.3003`, doc `shopee_chinh_sach_van_chuyen`, chunk `47`: ## 4. Bồi thường Shopee sẽ thông báo trực tiếp kết quả xử lý khiếu nại cho Người Mua/Người Bán, kèm thông tin về mức bồi thường nếu có.
- Rank 3, score `0.2938`, doc `shopee_quy_dinh_dang_ban`, chunk `91`: ### 3.2. Quà tặng không đăng công khai Khi quà tặng kèm không được đăng công khai trên thông tin sản phẩm chính, Shopee sẽ không can thiệp xử lý khiếu nại về hạn sử dụng của quà tặng kèm.  Tuy nhiên, hành vi cố ý tặng kèm sản phẩm hết hạn sử dụng có 

### Query 4 — Quy trình

**Question:** Nếu người mua và người bán không tự thỏa thuận được, quy trình nhờ Shopee giải quyết tranh chấp gồm những bước nào?

**Gold answer:** Quy trình gồm: gửi khiếu nại; Shopee tiếp nhận và hỗ trợ; thu thập thông tin và xử lý; nếu vượt thẩm quyền thì chuyển vụ việc đến cơ quan nhà nước có thẩm quyền.

**Expected document:** `shopee_giai_quyet_tranh_chap` — Các mục Bước 1 đến Bước 4 của quy trình.

**Agent answer:** Không có đủ thông tin trong bối cảnh để trả lời câu hỏi về quy trình nhờ Shopee giải quyết tranh chấp.

- Rank 1, score `0.2859`, doc `shopee_quy_dinh_dang_ban`, chunk `11`: ## 2. Các nội dung không được phép đăng bán 12. Sản phẩm vi phạm quyền sở hữu trí tuệ và/hoặc bất kỳ nhãn hiệu hàng hóa nào của bất kỳ bên thứ ba nào.  13. Các sản phẩm nằm trong **Danh sách sản phẩm bị cấm/hạn chế của Shopee**.  ---
- Rank 2, score `0.2761`, doc `shopee_quy_dinh_dang_ban`, chunk `90`: ### 3.1. Quà tặng được đăng công khai Khi quà tặng kèm được đăng công khai trên thông tin sản phẩm chính, quy định về hạn sử dụng sẽ được áp dụng **tương tự sản phẩm chính**.
- Rank 3, score `0.2664`, doc `shopee_quy_dinh_dang_ban`, chunk `36`: ## 3.5. Nhà cửa & Đời sống Đăng sản phẩm theo đúng định dạng được Shopee quy định.  ---

### Query 5 — Điều kiện

**Question:** Tôi có được bóc tem (seal) của hộp điện thoại ra để thử khi đồng kiểm không?

**Gold answer:** Chính sách vận chuyển không cho phép kiểm tra hàng trước khi thanh toán và nhận hàng; ngoại lệ là đơn hàng được đồng kiểm. Khi đồng kiểm, cần tuân thủ quy định và tình trạng tem niêm phong có thể ảnh hưởng đến xử lý/bồi thường.

**Expected document:** `shopee_chinh_sach_van_chuyen` — Mục E.1 - Kiểm tra hàng trước khi thanh toán; các bảng về tem niêm phong.

**Agent answer:** Không có đủ thông tin trong ngữ cảnh để trả lời câu hỏi về việc có được bóc tem (seal) của hộp điện thoại ra để thử khi đồng kiểm hay không.

- Rank 1, score `0.4654`, doc `shopee_chinh_sach_van_chuyen`, chunk `40`: ## 2. Thời gian xử lý khiếu nại Shopee xử lý khiếu nại tối đa **10 ngày làm việc** kể từ khi nhận đủ bằng chứng hợp lệ từ các bên liên quan.  Đối với vụ việc có nhiều tình tiết phức tạp cần xác minh thêm:  -   Thời gian xử lý có thể kéo dài hơn. -   
- Rank 2, score `0.3834`, doc `shopee_chinh_sach_van_chuyen`, chunk `73`: ## Khối lượng tính cước ``` text Khối lượng tính cước = MAX(     Khối lượng thực tế sau đóng gói,     Khối lượng quy đổi ) ```
- Rank 3, score `0.3184`, doc `shopee_chinh_sach_van_chuyen`, chunk `68`: ## 9. Quyết định cuối cùng về tranh chấp vận chuyển Mọi tranh chấp liên quan đến vận chuyển được giải quyết theo:  **Chính sách Vận Chuyển Shopee.**  Quyền quyết định cuối cùng thuộc về:  **Shopee.**

## A/B filter — Query 2

- Filtered IDs: `['shopee_quy_dinh_dang_ban::chunk_13::188', 'shopee_quy_dinh_dang_ban::chunk_29::204', 'shopee_quy_dinh_dang_ban::chunk_61::236']`
- Unfiltered IDs: `['shopee_quy_dinh_dang_ban::chunk_13::188', 'shopee_quy_dinh_dang_ban::chunk_29::204', 'shopee_quy_dinh_dang_ban::chunk_61::236']`
- Filtered evidence: **none** (Không có chunk top-3 chứa cụm bằng chứng yêu cầu.)
- Unfiltered evidence: **none** (Không có chunk top-3 chứa cụm bằng chứng yêu cầu.)
- Filtered agent answer: Không có đủ thông tin trong ngữ cảnh để trả lời câu hỏi về cách xử lý vi phạm quy định đăng bán sản phẩm. Các quy định chỉ nêu rõ các hành vi không được thực hiện mà không đề cập đến hình thức xử lý vi phạm [1].
- Unfiltered agent answer: Không có đủ thông tin trong ngữ cảnh để trả lời câu hỏi về cách xử lý vi phạm quy định đăng bán sản phẩm. Các quy định chỉ đề cập đến các hành vi không được thực hiện mà không nêu rõ hình thức xử lý vi phạm [1].
- Nhận xét: filter được áp dụng trước rank và giới hạn kết quả trong tài liệu seller. Trong lần chạy này cả hai top-3 đều không chứa đủ bằng chứng về mục xử lý vi phạm; filter giảm phạm vi ứng viên nhưng không khắc phục giới hạn của mock embedding.

## Failure case

Query 5 là failure case chính: top-3 không chứa chunk của `shopee_chinh_sach_van_chuyen`, nơi có quy định về đồng kiểm và tem niêm phong. Các chunk được trả về thuộc tài liệu trả hàng, tranh chấp và đăng bán; chúng gần chủ đề thương mại điện tử nhưng không chứa bằng chứng trực tiếp. Nguyên nhân có thể là mock embedding xếp hạng theo vector gần như ngẫu nhiên và RecursiveChunker không bảo đảm bảng/section đồng kiểm nằm cùng chunk. Đề xuất: chạy lại bằng local multilingual embedder và thử chunk theo heading/section để giữ câu hỏi, ngoại lệ và bảng bằng chứng cùng nhau.

## Kết luận

Strategy đã nạp 324 chunk và chạy đủ 5 query cố định, đạt **0/10** theo kiểm tra bằng chứng hiện tại. Đây là kết quả của một strategy riêng, chưa đủ cơ sở tuyên bố tốt nhất trước khi so sánh với các thành viên khác.
