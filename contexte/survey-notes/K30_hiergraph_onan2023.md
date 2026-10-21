# [K30] Hierarchical graph-based text classification framework with contextual node embedding and BERT-based dynamic fusion

> **Vai trò:** R3 – Đại diện **nhánh đồ thị (G)**; ví dụ phản biện về baseline và tính so sánh được · Chương 4, 8 · Liên quan ★★★
> **Ghi chú file:** `30.pdf` và `31.pdf` có nội dung giống hệt nhau. Phiếu này áp dụng cho cả hai.

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | A. Onan, "Hierarchical graph-based text classification framework with contextual node embedding and BERT-based dynamic fusion," *J. King Saud Univ. – Comput. Inf. Sci.*, vol. 35, no. 7, Art. no. 101610, 2023, doi: 10.1016/j.jksuci.2023.101610. *(Số tập con cần xác minh.)* |
| Đơn vị | İzmir Katip Çelebi Univ., Thổ Nhĩ Kỳ |
| File | `sources/papers/Paper_KDD_Data/30.pdf` (= `31.pdf`) |

## 2. Bài toán và động lực
- Các mô hình GNN cho văn bản (TextGCN, TextING, HyperGAT…) và các PLM mỗi bên chỉ nắm một phần: quan hệ cấu trúc hoặc ngữ cảnh.
- **Đề xuất:** kết hợp đặc trưng ngôn ngữ, đồ thị phân cấp có tri thức miền, và BERT.

## 3. Phương pháp (7 giai đoạn)
1. Trích đặc trưng ngôn ngữ (LFE): POS, dependency, NER, coreference.
2. Dựng nút phân cấp (tài liệu → đoạn → câu → từ; cửa sổ 512/64) và hợp nhất với đồ thị tri thức miền.
3. Embedding nút theo ngữ cảnh (BERT, lr 2e-5).
4. Học đồ thị đa mức (GCN 3 mức, hidden 256).
5. Tương tác đặc trưng tuần tự động bằng **DTW**.
6. Học đồ thị dựa trên attention.
7. Hợp nhất động với BERT, rồi tầng FC.

Thiết lập theo Wang et al. 2023: GloVe 300 chiều đóng băng; 10% train làm tập validation; Adam; dropout 0,5; bỏ ngẫu nhiên cạnh với xác suất 0,3.

## 4. Dữ liệu và kết quả
- **8 dataset:** 20NG (20.000 bài, 20 lớp), R8 (7.674 bài, 8 lớp), R52 (9.100 bài, 52 lớp), Ohsumed (7.400 bài, 23 lớp), MR, Airline Twitter, App (752.937 bài), Sarcasm.
- **17 baseline** và 9 biến thể ablation.

| Mô hình | 20NG | R8 | R52 | Ohsumed | MR |
|---|---|---|---|---|---|
| TextGCN *(theo K30)* | 79,52 | 86,07 | 84,01 | 67,12 | 80,18 |
| BERT *(theo K30)* | 82,35 | 91,06 | 87,33 | 70,59 | 83,70 |
| Text-FCG + BERT | 85,67 | 95,43 | 91,63 | 74,08 | 87,19 |
| **Đề xuất** | **93,71** | **98,75** | **94,11** | **74,87** | **89,30** |

- Ablation: bỏ bất kỳ mô-đun nào cũng làm giảm kết quả. Chỉ dùng POS (biến thể 1) vẫn rất cao (R8 95,88).

## 5. Hạn chế và phản biện (mạnh)
1. **Baseline không khớp với công bố gốc, lệch theo cả hai chiều.** Chính các survey trong kho tài liệu đã ghi TextGCN đạt **20NG 86,34; Ohsumed 68,36; MR 76,74** ([K06] Bảng 2; [K05] Bảng 4). K30 báo 79,52 / 67,12 / **80,18**. TextGCN gốc (Yao et al., AAAI 2019) còn báo R8 97,07, trong khi K30 báo 86,07. BERT trên R8 trong K30 chỉ 91,06, thấp hơn nhiều so với mức thường được báo (khoảng 97–98). Như vậy **"vượt trội trên mọi dataset" chủ yếu đến từ baseline yếu hoặc không nhất quán**.
2. Không báo độ lệch chuẩn. Số liệu ghi 4 chữ số thập phân tạo cảm giác chính xác giả.
3. Pipeline 7 giai đoạn, nhiều siêu tham số, **không công bố mã nguồn**, không báo chi phí. Hệ thống gần như không tái lập được.
4. Phụ thuộc vào POS, dependency, NER, coref và đồ thị tri thức miền. Với ngôn ngữ ít tài nguyên như tiếng Việt, đây là nguồn **lan truyền lỗi** ([K21]: NER F1 0,58).
5. "Tri thức miền" được mô tả chung chung, không rõ nguồn cho từng dataset.

## 6. Liên hệ với đề tài / Trans2Vec
- **Nhánh G trong taxonomy:** đồ thị đồng xuất hiện từ–tài liệu (TextGCN) là "người họ hàng" của Trans2Vec. Cả hai đều khai thác **đồng xuất hiện** giữa từ: TextGCN qua cạnh PMI (bậc hai), Trans2Vec qua FI (bậc cao, không cần liền kề). Cả hai bản gốc đều **transductive** (TextGCN đưa tài liệu test vào đồ thị; mã gốc Trans2Vec học embedding trên train + test). Đây là chỗ nối với phát hiện về giao thức đánh giá của GĐ6 (Mục 3.1 RESULTS.md, Bảng 9.6 survey).
- **Ví dụ điển hình cho Chương 8 (mối đe dọa đến tính hợp lệ):** cùng một mô hình (TextGCN) mà số liệu chênh nhau tới 11 điểm giữa các nguồn. Điều này củng cố đề xuất giao thức chuẩn của survey (Mục 7.3): chạy lại baseline trong cùng điều kiện, báo mean ± std.
- **Không** đưa vào bảng so sánh kết quả tin tức tiếng Việt.

## 7. Ý dùng trong survey
- **Chương 4 (nhánh G, mới):** 1 đoạn: TextGCN → đồ thị phân cấp + PLM; điểm chung "đồng xuất hiện" với Trans2Vec.
- **Chương 8.2 và 8.4:** ví dụ baseline lệch so với công bố gốc (trích chéo [K05], [K06]).
- **Chương 9:** lý do không chọn hướng đồ thị cho hệ thống tiếng Việt (chi phí, công cụ ngôn ngữ, tái lập).
