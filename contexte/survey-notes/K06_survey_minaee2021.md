# [K06] Deep Learning–based Text Classification: A Comprehensive Review

> **Vai trò:** R4 – **Khung tham chiếu** (mô hình DL, dataset tin tức, công thức chọn mô hình, thách thức). **Không** dùng làm bằng chứng kết quả sơ cấp · Chương 1.4, 4, 7, 8, 9 · Liên quan ★★★★ (khung)

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | S. Minaee, N. Kalchbrenner, E. Cambria, N. Nikzad, M. Chenaghlu, and J. Gao, "Deep learning–based text classification: A comprehensive review," *ACM Comput. Surv.*, vol. 54, no. 3, Art. no. 62, Apr. 2021, doi: 10.1145/3439726. |
| Đơn vị | Snapchat; Google Brain; NTU Singapore; Univ. of Tabriz; Microsoft Research |
| Phạm vi | Hơn 150 mô hình DL, hơn 40 dataset; 40 trang |
| File | `sources/papers/Paper_KDD_Data/06.pdf` |

## 2. Cấu trúc và nội dung
1. **Tác vụ** (§1.1): sentiment, **news categorization**, topic, QA, NLI.
2. **Mô hình** (§2):
   - FFNN: DAN, fastText, **doc2vec / Paragraph Vector**;
   - RNN; CNN; Capsule; Attention; Memory;
   - **GNN** (TextGCN, …); Siamese; Hybrid;
   - Transformer/PLM;
   - **Ngoài học có giám sát** (§2.11): autoencoder, VAE (NVDM), học bán giám sát, học đối kháng.
3. **Công thức chọn mô hình 5 bước** (§3): (1) chọn PLM; (2) thích nghi miền (tiếp tục pre-train); (3) thiết kế lớp đầu ra theo tác vụ; (4) fine-tune (đóng băng hoặc không; multi-task cho các bộ phân loại tin tức thuộc nhiều miền); (5) **nén mô hình** (distillation) vì "PLMs are expensive to serve".
4. **Dataset tin tức** (§4.2): **AG News** (120k/7,6k, 4 lớp), **20 Newsgroups** (18.821), **Sogou News** (tiếng Trung, nhãn lấy từ domain URL), **Reuters** (ApteMod 90 lớp; R8, R52, RCV1); ngoài ra Bing, BBC, Google News.
5. **Kết quả** (§5.2):
   - Bảng 2 (tin tức): AG News fastText 92,50, DPCNN 93,13, ULMFiT 94,99, **XLNet 95,51**; TextGCN AG 67,61, 20NG 86,34, Ohsumed 68,36.
   - **Bảng 4 (WikiQA): Paragraph Vector MAP 0,511 / MRR 0,516**, so với BERT 0,813 / 0,828.
6. **Thách thức** (§6): dataset mới cho tác vụ khó (đa ngôn ngữ, **tài liệu rất dài**), tri thức thường thức, **mô hình diễn giải được**, mô hình tiết kiệm bộ nhớ, few/zero-shot.

## 3. Đánh giá phản biện
- **Điểm mạnh:** mục §3 "chọn mô hình" mang tính thực hành cao; mục dataset tin tức tách riêng; có bảng kết quả theo tác vụ.
- **Hạn chế:**
  - Thiên về DL. Phần phi-DL chỉ được in nghiêng trong bảng làm mốc.
  - Bảng kết quả tổng hợp từ các nguồn khác nhau.
  - Chưa có LLM.
  - Không nhắc tới biểu diễn dựa trên mẫu phổ biến.
  - Ngôn ngữ ít tài nguyên chỉ được nhắc ở mức chung ("đa ngôn ngữ").
  - Bài "chọn mô hình" giả định có GPU và PLM tốt cho ngôn ngữ đích. Với tiếng Việt, bước (1) dẫn tới PhoBERT/XLM-R.

## 4. Liên hệ với đề tài / Trans2Vec
- **Bằng chứng ngoài cho bước (5b) tìm kiếm:** Paragraph Vector (cùng họ với TRANS-IT, PV-DBOW) chỉ đạt **MAP 0,511 trên WikiQA**, rất xa BERT. Tức embedding kiểu PV yếu ở **khớp truy vấn – tài liệu theo nghĩa thật**. Kết quả này phải đặt cạnh nDCG@10 của nhóm (JOI 0,809 > TF-IDF 0,740). Khác biệt nằm ở định nghĩa liên quan: nhóm dùng **proxy "cùng chuyên mục"**, dễ hơn nhiều so với khớp câu hỏi – câu trả lời. Đây là **điểm phản biện mới cho RQ6** và Mục 8.4 (mối đe dọa đến tính hợp lệ).
- **Sogou News** là tiền lệ "tin tức trong ngôn ngữ không có ranh giới từ tường minh". Dùng ở Chương 2 để đặt vấn đề tách từ tiếng Việt vào bối cảnh quốc tế. Tiếng Việt khác ở chỗ khoảng trắng tách *âm tiết*, không tách *từ*.
- **Công thức 5 bước** là khung lập luận cho Chương 9:
  - bước (1) và (4) cho ra trần trên PhoBERT fine-tune ([10]);
  - bước (5) cho thấy chi phí phục vụ là vấn đề thật, mở chỗ cho phương án rẻ (Trans2Vec trên CPU) hoặc đóng băng (K29);
  - "multi-task cho nhiều miền tin tức" gợi ý mở rộng cho nhiều đầu báo.
- **Thách thức "tài liệu rất dài" và "diễn giải được"** trùng với đặc điểm tin tức tiếng Việt và với điểm mạnh của FI.

## 5. Ý dùng trong survey
- **Chương 1.4:** survey tham chiếu thứ hai.
- **Chương 2:** Sogou News và bài toán ranh giới từ.
- **Chương 4.5 (nhánh D):** doc2vec theo mô tả của K06.
- **Chương 7.1:** bảng dataset tin tức quốc tế.
- **Chương 8.4:** PV MAP 0,511 so với nDCG của nhóm.
- **Chương 9.1:** lập luận theo công thức 5 bước.
