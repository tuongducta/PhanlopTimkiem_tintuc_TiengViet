# [K25] Theoretical Properties of Closed Frequent Itemsets in Frequent Pattern Mining

> **Vai trò:** R1 – Nền tảng KDD cho **bước (3) khai phá FI** của đường ống · Taxonomy **E3** (đề xuất) · Chương 3.2, 5.6, 9 · Liên quan ★★★★★

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | H. Zhang, H. Li, Y. Li, G. Teng, and X. Cao, "Theoretical properties of closed frequent itemsets in frequent pattern mining," *Mathematics*, vol. 13, no. 11, Art. no. 1709, May 2025, doi: 10.3390/math13111709. |
| Đơn vị | Beijing Technology and Business Univ.; Harbin Institute of Technology |
| Loại bài | Bài lý thuyết kèm thực nghiệm minh họa, MDPI (open access) |
| File | `sources/papers/Paper_KDD_Data/25.pdf` |

## 2. Bài toán và động lực
- FIM bị **bùng nổ số itemset** khi minsup thấp, kéo theo dư thừa lớn giữa các ứng viên.
- **Closed FI (CFI)** là biểu diễn **nén và không mất thông tin** của toàn bộ FI. Tuy vậy, các nghiên cứu trước tập trung cải tiến thuật toán (Closet, Closet+, NECLATCLOSED, DFI-Growth…) mà ít hệ thống hóa tính chất lý thuyết.
- Một itemset "phổ biến" trên một mẫu dữ liệu có thể chỉ là **giả phổ biến** do dao động lấy mẫu. Chưa có tiêu chí thống kê để đánh giá độ ổn định của CFI.

## 3. Phương pháp
1. **Định nghĩa** (Def. 1–7):
   - support, FI;
   - hai ánh xạ $t: 2^I \to 2^T$ (itemset → tập giao dịch chứa nó) và $i: 2^T \to 2^I$ (tập giao dịch → item chung);
   - **toán tử bao đóng** $c = i \circ t$;
   - CFI: X phổ biến và $c(X) = X$;
   - **lớp tương đương** $[X]$: các itemset có cùng tập giao dịch.
2. **Tính chất đã chứng minh:**
   - Thm. 1: $t$ và $i$ là hàm đơn điệu (nghịch biến).
   - Prop. 1: $c$ có tính mở rộng, đơn điệu và lũy đẳng.
   - Prop. 2: $|CFI| \le |FI|$.
   - Prop. 3: các itemset cùng bao đóng có cùng support, và mỗi lớp $[X]$ có **duy nhất** một phần tử lớn nhất là CFI.
   - Hệ quả 1–3: tập FI **phân hoạch** được thành các lớp tương đương rời nhau, mỗi lớp đại diện bởi một CFI.
3. **CICFI** (Def. 8, Thm. 2): X là CICFI nếu X đóng **và cận dưới khoảng tin cậy** $P_L$ của relative support $\ge \theta$. Ba cách ước lượng khoảng:
   - **Wald**: xấp xỉ chuẩn, cần N lớn và $\tilde p$ không ở biên;
   - **Wilson**: hiệu chỉnh độ lệch của Wald;
   - **Clopper–Pearson**: chính xác theo phân phối nhị thức/Beta, dùng được với mọi cỡ mẫu.

## 4. Dữ liệu và kết quả
| Dataset | Giao dịch | Item | Độ dài TB / max | Loại |
|---|---|---|---|---|
| Ví dụ minh họa | 7 | 5 | – | – |
| retail (SPMF) | 88.162 | 16.407 | 10,3 / 76 | Thưa |
| mushroom (SPMF) | 8.124 | 119 | 23 / 23 | Dày |

- Ước lượng CI trên **mẫu ngẫu nhiên** (cỡ mẫu 40 với retail, minsup 6%; cỡ mẫu 60 với mushroom, minsup 60%).
- **Wald** ổn khi rsup cao nhưng mất ổn định khi rsup thấp. **Clopper–Pearson** rộng nhất (bảo thủ, độ phủ cao nhất). **Wilson** cân bằng tốt nhất, hẹp hơn Wald một chút.
- CI hẹp lại khi cỡ mẫu tăng (Fig. 5).
- Kết luận của tác giả: CFI có support cao và CI hẹp là mẫu "phổ biến **và** ổn định". CFI có CI rộng có thể là giả phổ biến.

## 5. Hạn chế và phản biện
- **Thực nghiệm minh họa rất nhỏ:** CI được tính trên mẫu 40–60 giao dịch, chỉ 2 dataset thật. Không có tác vụ hạ nguồn (phân loại, gợi ý) nào chứng minh CICFI giúp ích thực tế.
- Phần lý thuyết về CFI (Prop. 1–3) là **kết quả kinh điển** (Pasquier 1999, Zaki 2002). Đóng góp mới thực chất nằm ở cách trình bày hệ thống và ở định nghĩa CICFI.
- CI được tính **riêng từng itemset**, chưa hiệu chỉnh cho kiểm định bội (hàng nghìn FI cùng lúc). Mức tin cậy chung thực tế sẽ thấp hơn $1-\alpha$.
- Không đưa ra thuật toán khai phá CICFI hiệu quả, mà chỉ lọc sau khi đã có CFI.

## 6. Liên hệ với đề tài / Trans2Vec
- **Giải hạn chế H2 (bùng nổ FI với tin tức dài) có trích dẫn sơ cấp.** Prop. 3 và Hệ quả 3 cho thấy thay toàn bộ FI bằng CFI **không mất thông tin support**. Với PV-DBOW, các FI cùng lớp tương đương xuất hiện ở *đúng cùng* các bài báo. Do đó chúng là các token **hoàn toàn trùng ngữ cảnh**: chỉ làm tăng kích thước từ vựng mà không thêm tín hiệu (giả thuyết **H8**).
- **Đối chiếu với thực nghiệm sẵn có:** ablation **A3** của GĐ6 (`contexte/results/RESULTS.md` Mục 2.3) cho kết quả chỉ dùng FI đóng = 0,770 so với JOI 0,766 (Macro-F1, model.dv). Như vậy **bỏ FI không đóng không làm mất gì**, khớp với dự đoán từ K25. Survey có thể dùng K25 làm *giải thích lý thuyết* cho A3.
- > **Đính chính (22/10):** hai ý trên không còn đúng. Ở cấu hình chính mọi FI đều đóng, nên A3 so hai tập FI giống hệt nhau và không kiểm chứng K25. E8 cho thấy FI không đóng rất hiếm trong giao dịch văn bản (≤ 3,4%, chủ yếu là cụm cố định như {sea, games}); xem `contexte/results/RESULTS.md` Mục 7.1. Giá trị của K25 cho đề tài nằm ở CICFI (E9), không nằm ở closed FI.
- **CICFI và tổng quát hóa train → test/query:** FI được khai phá trên tập train. Câu hỏi "FI đó còn phổ biến trên dữ liệu mới không" chính là câu hỏi về CI của rsup. Đây là **tiêu chí chọn FI có cơ sở thống kê**, có thể thay hoặc bổ sung cho elbow của [13]. GĐ6 cho thấy elbow kém nhạy (Mục 3.2: cả 4 cấu hình chọn cùng δ).
- **Gợi ý cài đặt:** với N = 33.759 bài train, CI Wilson của FI có rsup 0,5% có bán kính khoảng ±0,075 điểm %, rất hẹp. Nên CICFI chỉ tạo khác biệt thật khi **ước lượng theo từng chuyên mục** (N nhỏ hơn) hoặc ở FI gần ngưỡng δ. Cần ghi chú điều này khi đề xuất E9.

## 7. Ý dùng trong survey
- **Chương 3.2:** thêm định nghĩa toán tử bao đóng, CFI, lớp tương đương (rút gọn Def. 3–7, Prop. 3).
- **Chương 5.6:** H2 nêu lời giải CFI có trích dẫn; thêm H8; liên kết ablation A3.
- **Chương 9 (mô-đun FIM):** khai phá CFI; tùy chọn lọc CICFI (Wilson, ước lượng theo chuyên mục).
- **E9 (điều chỉnh so với kế hoạch v3):** phần closed FI **đã có** (A3), nên E9 chỉ còn phần **lọc theo CI**, và nên đánh giá cả nDCG chứ không chỉ Macro-F1.
