# [6] From Universal Language Model to Downstream Task: Improving RoBERTa-Based Vietnamese Hate Speech Detection

> **Vai trò:** Kỹ thuật fine-tune PhoBERT (bài lệch miền: hate speech) · Taxonomy **F** · Chương 4 (nhánh F), Chương 9 (trần trên tham chiếu)

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | Q. H. Pham, V. A. Nguyen, L. B. Doan, N. N. Tran, and T. M. Thanh, "From universal language model to downstream task: Improving RoBERTa-based Vietnamese hate speech detection," in *Proc. 12th Int. Conf. Knowledge and Systems Engineering (KSE)*, Can Tho, Vietnam, 2020, pp. 37–42. |
| Đơn vị | R&D Lab, Sun\* Inc.; HV Kỹ thuật Quân sự (Ta Minh Thanh là tác giả liên hệ của bài này và là đồng tác giả của [3]) |
| File | `[6] RoBERTa-VN-HateSpeech-pham2020.pdf` (**bản scan, không có lớp text**; đọc bằng cách render ảnh) |

## 2. Bài toán
- Phát hiện hate speech tiếng Việt, VLSP 2019 HSD: 3 lớp HATE / OFFENSIVE / CLEAN.
- 25.431 mẫu từ Facebook; train 20.345 mẫu (HATE 709, OFFENSIVE 1.022, **CLEAN 18.614**), **rất mất cân bằng**.
- Dữ liệu mạng xã hội: viết tắt, emoji, teencode, lỗi gõ. Trong khi đó PhoBERT được pretrain trên Wikipedia và tin tức.

## 3. Phương pháp
1. **Kiến trúc:** PhoBERT (RoBERTa-base, 12 khối); ghép (concat/add) đầu ra 768 chiều của nhiều khối Transformer rồi đưa vào head FC.
2. **Tiếp tục huấn luyện MLM trên dữ liệu miền** (domain-adaptive): mask 15%, batch 32, 10.000 bước, Adam lr 3e-5.
3. **Tăng cường dữ liệu bằng PhoBERT MLM:** mask ngẫu nhiên 1 token rồi điền lại, lặp 5 lần để sinh mẫu mới cho lớp HATE và OFFENSIVE.
4. **Chiến lược fine-tune:**
   - Warm-up learning rate (slanted triangular).
   - **Đóng băng** BERT ở các epoch đầu, sau đó mở băng với **learning rate theo khối** (khối sâu hơn có lr lớn hơn; BERT 1e-5, head 1e-4).
   - **Label smoothing** α = 0,2: $y'_k = y_k(1-\alpha)+\alpha/K$.
5. **Tiền xử lý:** chuẩn hóa Unicode, chữ thường, thay emoji bằng nhãn EMOJI, che thông tin cá nhân, **tách từ bằng RDRSegmenter (VnCoreNLP)** cho khớp với dữ liệu pretrain của PhoBERT.
6. **Đánh giá:** Stratified 10-fold, mỗi fold 10 epoch, **Macro-F1**.

## 4. Kết quả
- **Chọn khối (Table II):** 4 khối cuối (9–12) và 6 khối cuối (7–12) cùng đạt F1 cao nhất **0,6989**. Dùng 1 khối đơn (6 hoặc 12) chỉ được 0,685–0,698.
- **Kết hợp mọi kỹ thuật:** **Macro-F1 0,7221**, vượt đội thắng cuộc VLSP (0,67756) và kết quả tốt nhất trên public leaderboard (0,71432). Mỗi kỹ thuật riêng lẻ đóng góp 0,5–1,5%.

## 5. Hạn chế và phản biện
- Lệch miền so với đề tài (bình luận mạng xã hội, không phải tin tức).
- Không có ablation đầy đủ theo từng kỹ thuật trong phần trích được.
- Có so sánh với leaderboard, nhưng kết quả của bài là 10-fold CV trên tập train, còn leaderboard đo trên tập public/private test. **Hai con số không cùng giao thức.**

## 6. Liên hệ với đề tài / Trans2Vec
- **Vị trí:** đại diện nhánh F (contextual embedding) và là **trần trên tham chiếu** khi so với Trans2Vec.
- **"Đặc trưng từ các khối cuối tốt nhất"** cho thấy nếu dùng PhoBERT làm bộ mã hóa câu cho tìm kiếm thì nên lấy trung bình hoặc ghép các khối cuối.
- **Domain-adaptive MLM** ứng với khuyến nghị: nếu dùng PhoBERT cho tin tức thì PhoBERT vốn đã pretrain trên tin tức, nên lợi thế miền cao.
- **Tách từ bằng VnCoreNLP là bắt buộc với PhoBERT.** Điều này nhất quán với kết quả của [9].
- **Đối lập cần nêu trong survey:** PhoBERT đòi hỏi GPU (GTX 2080Ti) và nhiều giờ huấn luyện, trong khi Trans2Vec chạy trên CPU và không giám sát.

## 7. Ý dùng trong survey
- Chương 4 (nhánh F): fine-tune pipeline.
- Chương 6: đánh đổi chi phí.
- Chương 9: mô tả cấu hình baseline PhoBERT.
