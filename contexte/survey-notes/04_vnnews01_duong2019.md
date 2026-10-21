# [4] A Survey on the Multiple Classifier for New Benchmark Dataset of Vietnamese News Classification

> **Vai trò:** Benchmark **VNNews-01** (25 chuyên mục, khó, sát thực tế); tổng quan các bộ phân loại kèm chi phí thời gian · Taxonomy **A2** + trục bộ phân loại · Chương 3, 6, 7

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | H.-T. Duong and V. T. Hoang, "A survey on the multiple classifier for new benchmark dataset of Vietnamese news classification," in *Proc. 11th Int. Conf. Knowledge and Smart Technology (KST)*, Phuket, Thailand, 2019, pp. 23–28. |
| Đơn vị | ĐH Mở TP.HCM |
| File | `[4] VNNews01-MultipleClassifier-duong2019.pdf` |

## 2. Bài toán
- Định nghĩa hình thức: cho $D=\{d_1..d_N\}$ và $C=\{c_1..c_k\}$, bộ phân loại là ánh xạ $F: D\times C \to \{\text{true},\text{false}\}$. Phân biệt binary, multi-class và multi-label. Bài này tập trung vào **multi-class**.
- Tổng quan lý thuyết các bộ phân loại: kNN, NB (Multinomial, Bernoulli, Laplace smoothing), LR, Decision Tree (ID3, C4.5, CART với Gini), RF, SVM (hard/soft margin, kernel), OVO, OVA.

## 3. Dataset VNNews-01
- Thu thập bằng newspaper3k và Selenium từ hơn 30 trang (thanhnien, vietnamnet, vnexpress, dantri, tuoitre, …), crawl hằng ngày.
- Gộp chuyên mục thủ công thành **25 lớp** (giáo dục, sức khỏe, thể thao, chính trị, du lịch, quốc phòng, giải trí, công nghệ, khoa học, bất động sản, kinh doanh, …).
- **37.500 tài liệu.** Tách từ tiếng Việt → TF-IDF. Dataset cung cấp theo yêu cầu (không công khai trực tiếp).

## 4. Thực nghiệm và kết quả
- **5-fold CV**, báo **F-measure trung bình** và thời gian (Xeon 3,2 GHz, 16 GB RAM).

| Bộ phân loại | F1 VNNews-01 | F1 20NG | Train / Test (s) trên VNNews-01 |
|---|---|---|---|
| Multinomial NB (α = 0,01) | 0,716 | 0,910 | 0,34 / 0,05 |
| LR multinomial | 0,734 | 0,892 | 77,5 / 0,06 |
| kNN (k = 5) | 0,626 (k = 3: **0,500**) | 0,775 | 0,08 / 28,8 |
| CART | 0,567 | 0,622 | 86,2 / 0,05 |
| RF (100 cây) | 0,689 | 0,822 | 407,7 / 0,98 |
| **SVM RBF** | **0,749** | 0,914 | 838,7 / 290,7 |
| OVO linear SVM | 0,747 | 0,913 | 827 / 4.785 |
| OVA linear SVM | 0,742 | **0,923** | 4.743 / 828 |

- **Kết luận:** SVM (và OVO/OVA dựa trên SVM) tốt nhất nhưng chậm nhất. **LR gần bằng mà inference nhanh hơn nhiều.** Thứ hạng các bộ phân loại trên VNNews-01 và 20NG gần như trùng nhau.

## 5. Hạn chế và phản biện
- Chỉ dùng TF-IDF; **không thử embedding** hay chọn đặc trưng.
- Không công bố phân bố lớp; không báo macro hay micro.
- Không phân tích lỗi giữa các chuyên mục chồng lấn (khoa học/công nghệ, kinh doanh/bất động sản).
- Tên "survey" nhưng thực chất là benchmark + tổng quan bộ phân loại.

## 6. Liên hệ với đề tài / Trans2Vec
- **F1 0,749 so với > 95% ở [1]/[3]** là bằng chứng chính cho luận điểm: *độ khó corpus (số lớp, chồng lấn) chi phối kết quả*.
- VNNews-01 (hoặc corpus tự crawl tương tự) là **benchmark khó**, nơi một biểu diễn tốt hơn TF-IDF như Trans2Vec có không gian để cải thiện rõ.
- **Bảng thời gian** là mẫu để đo chi phí (H7 của [13]). LR nhanh và mạnh, là bộ phân loại hợp lý cho hệ thống thời gian thực.
- Phương pháp crawl (newspaper3k, Selenium) có thể dùng lại cho pipeline thu thập dữ liệu.

## 7. Ý dùng trong survey
- Định nghĩa hình thức bài toán (Chương 3).
- Bảng so sánh bộ phân loại và chi phí (Chương 6).
- Bảng dataset (Chương 7).
