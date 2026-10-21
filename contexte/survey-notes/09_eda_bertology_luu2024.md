# [9] An Approach of Data Augmentation to Improve the Performance of BERTology Models for Vietnamese Hate Speech Detection

> **Vai trò:** Ảnh hưởng của tiền xử lý tiếng Việt lên mô hình Transformer; xử lý mất cân bằng (EDA, Focal loss) (bài lệch miền) · Taxonomy **F** + trục tiền xử lý · Chương 2, 4

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | S. T. Luu, K. V. Nguyen, and N. L.-T. Nguyen, "An approach of data augmentation to improve the performance of BERTology models for Vietnamese hate speech detection," *Multimedia Tools and Applications*, vol. 83, pp. 56763–56783, 2024, doi: 10.1007/s11042-023-16968-5. |
| Đơn vị | ĐH CNTT, ĐHQG TP.HCM (nhóm UIT-NLP) |
| Loại | Tạp chí (Springer, SCIE), 21 trang |
| File | `[9] DataAugmentation-BERTology-VN-HSD-luu2024.pdf` |

## 2. Bài toán và câu hỏi nghiên cứu
1. Các bước tiền xử lý tiếng Việt phổ biến (tách từ, bỏ stopword, chữ thường, bỏ emoji, hashtag, URL) **có còn giúp** mô hình BERTology không?
2. Cải tiến **EDA** để xử lý mất cân bằng.
3. Hiệu quả của **Focal loss**.

## 3. Dữ liệu
| | ViHSD | UIT-ViCTSD |
|---|---|---|
| Nhãn | 3 (CLEAN / OFFENSIVE / HATE) | 2 (toxic / non-toxic) |
| Số bình luận | 33.400 | 10.000 |
| Nguồn | Facebook, YouTube | **VnExpress** (bình luận báo điện tử) |
| Đồng thuận người gán nhãn | 0,52 | 0,58 |
| Đặc điểm | Teencode, viết tắt, tục | Viết rõ ràng hơn |

## 4. Phương pháp
- **Mô hình:** đa ngữ (mBERT cased/uncased, XLM-R, DistilBERT) và đơn ngữ (**PhoBERT**, BERT4News, ViELECTRA).
- **Tiền xử lý thử nghiệm:** pyvi (hoặc VnCoreNLP cho PhoBERT), bỏ stopword, chữ thường, bỏ emoji, hashtag, URL.
- **EDA** gồm 4 phép: Synonym Replacement, Random Insertion, Random Swap, Random Deletion.
  - **Cải tiến của bài:** lấy từ đồng nghĩa từ **embedding fastText `cc.vi.300`** (most-similar) thay cho Vietnamese WordNet, vì nó hợp với văn bản mạng xã hội và sinh được mẫu "ngoài miền".
- **Focal loss** cho dữ liệu mất cân bằng.
- **Độ đo:** **Macro-F1**, vì accuracy thiên về lớp đa số.

## 5. Kết quả chính (Macro-F1 %)
| Thí nghiệm | Phát hiện |
|---|---|
| Tiền xử lý | **Bỏ tiền xử lý thì kết quả tốt hơn** với hầu hết mô hình. Tốt nhất: BERT4News 65,55 (ViHSD), PhoBERT 73,21 (UIT-ViCTSD) |
| Tách từ với PhoBERT | **Có tách từ (VnCoreNLP) tốt hơn ~2 điểm**: 65,23 so với 63,26 (ViHSD); 73,21 so với 71,23 (ViCTSD) |
| EDA cải tiến | PhoBERT đạt **74,63** trên ViCTSD (so với gốc 73,21); trên ViHSD 65,51. Tốt hơn EDA cũ với XLM-R, PhoBERT |
| Focal loss | Có lợi cho **đa lớp** (ViHSD: PhoBERT 65,74); kém EDA trên **nhị phân** |

## 6. Hạn chế và phản biện
- Lệch miền. Cải thiện tuyệt đối nhỏ (1–2 điểm), không có kiểm định thống kê.
- Đồng thuận người gán nhãn thấp (0,52–0,58), là giới hạn trên tự nhiên của độ chính xác.
- Bảng kết quả có điểm bất thường: XLM-R "Original" trên ViHSD chỉ 47,04, nhiều khả năng do huấn luyện không hội tụ.

## 7. Liên hệ với đề tài / Trans2Vec
- **Điểm tương phản quan trọng về tiền xử lý:**
  - Với **Transformer**, tiền xử lý truyền thống thừa hoặc có hại (trừ tách từ cho PhoBERT).
  - Với **Trans2Vec** (dựa trên tập item và FI), tiền xử lý **là cốt lõi**. Bỏ stopword và tách từ quyết định item nào tồn tại, và từ đó FI nào được khai phá.
  - Survey nên có một bảng "tiền xử lý × họ biểu diễn".
- **fastText `cc.vi.300`** là embedding tiếng Việt pretrained có sẵn, có thể dùng để (a) mở rộng truy vấn trong tìm kiếm, (b) làm baseline embedding tĩnh.
- **Macro-F1** là độ đo bắt buộc vì chuyên mục tin tức mất cân bằng.
- UIT-ViCTSD lấy từ **VnExpress**, cùng nguồn với corpus tin tức nhưng là phần bình luận.

## 8. Ý dùng trong survey
- Chương 2 (ảnh hưởng tách từ).
- Chương 4 (nhánh F, danh sách mô hình BERT tiếng Việt).
- Chương 7 (Macro-F1, đồng thuận người gán nhãn).
