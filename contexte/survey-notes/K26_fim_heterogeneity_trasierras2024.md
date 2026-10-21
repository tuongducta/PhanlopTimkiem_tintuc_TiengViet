# [K26] Data heterogeneity's impact on the performance of frequent itemset mining algorithms

> **Vai trò:** R1 – Nền tảng KDD cho **bước (3) khai phá FI**: chọn thuật toán, mô tả dữ liệu dạng giao dịch · Taxonomy **E3** · Chương 3.2, 6, 7, 9 · Liên quan ★★★★★

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | A. M. Trasierras, J. M. Luna, P. Fournier-Viger, and S. Ventura, "Data heterogeneity's impact on the performance of frequent itemset mining algorithms," *Information Sciences*, vol. 678, Art. no. 120981, 2024, doi: 10.1016/j.ins.2024.120981. |
| Đơn vị | Univ. of Córdoba (DaSCI), Tây Ban Nha; Shenzhen Univ., Trung Quốc |
| Ghi chú | Fournier-Viger là tác giả thư viện **SPMF**. Bài có uy tín cao trong cộng đồng pattern mining |
| File | `sources/papers/Paper_KDD_Data/26.pdf` |

## 2. Bài toán và động lực
- Các nghiên cứu so sánh thuật toán FIM thường **coi dataset là bất biến** ("thưa" hoặc "dày") và chỉ đổi ngưỡng support.
- Thực tế, **ngưỡng support làm thay đổi chính đặc trưng dữ liệu**: lọc item không phổ biến sẽ biến một dataset thưa thành dày. Vì vậy so sánh thuật toán dễ thiên lệch.

## 3. Phương pháp
1. **Chín thuật toán cơ sở:** Apriori (ngang, BFS), Eclat và dEclat (dọc, tidset/diffset), FP-Growth và Relim (lai), SaM, **LCM, LCMv2, LCMv3** (LCM đoạt giải FIMI 2003).
2. **Hai kỹ thuật mở rộng:** *hypercube decomposition* (perfect extension pruning) và *k-items machine*.
3. **Tám độ đo tính không đồng nhất** (Eq. 1–12):

| Độ đo | Ý nghĩa |
|---|---|
| Density | $\sum\|t\| / (\|B\|\cdot\|T\|)$: độ dài giao dịch trung bình chia cho số item |
| Similarity | Số item trung bình một giao dịch chia sẻ với các giao dịch khác |
| Item distribution (ID) | Mức đồng xuất hiện trung bình giữa các cặp item |
| Items per transaction (IT) | Độ dài giao dịch trung bình ± std |
| Itemset size (IS) | Kích thước itemset kỳ vọng |
| \|T\|, \|B\|, \|\|T\|\| | Số giao dịch, số item, tổng số phần tử |

4. **Giao thức:** 14 dataset thật + 1 tổng hợp (rời rạc hóa); quét nhiều mức support; độ đo hiệu năng là **số itemset khai phá được mỗi giây**; lặp 5 lần; kiểm định Wilcoxon; Xeon E5-2620, 64 GB RAM.

## 4. Kết quả
- Bảng 3 xếp dataset theo density, từ Chess (0,49) đến Kosarak ($1{,}96\times10^{-4}$). Retail có density $6{,}26\times10^{-4}$, IT 10,3.
- **Đặc trưng dữ liệu thay đổi mạnh theo ngưỡng.** Ví dụ ở Bảng 8: similarity bằng 98,39 tại support 8.000 nhưng chỉ còn 48,89 tại support 250.
- Ở ngưỡng cao, mọi thuật toán gần như ngang nhau. Ở ngưỡng thấp, chênh lệch tới **4–6 bậc độ lớn**.
- **Không có thuật toán thắng mọi nơi.** LCM (các phiên bản) và FP-Growth thường tốt nhất.
- Khi mọi thuật toán đều có hypercube decomposition và k-items machine, chúng gần như ngang nhau. Nghĩa là **các mở rộng này quan trọng hơn bản thân thuật toán**.
- Chi phí khó lường: Eclat mất **khoảng 140 giờ** trên BMSPOS nhưng chỉ 4 giây trên Accidents. Nhiều lần chạy hết bộ nhớ.
- Kết luận về ứng dụng: **bùng nổ tổ hợp vẫn chưa giải được**. Ứng dụng thực tế cần hậu xử lý (tóm tắt mẫu, nén mẫu, **top-k**, chú giải ngữ nghĩa) và phải tự định nghĩa độ đo để giữ lại các mẫu "thực sự đáng quan tâm".

## 5. Hạn chế và phản biện
- Chỉ đánh giá **tốc độ**, không đánh giá **chất lượng** hay tính hữu ích của mẫu cho tác vụ hạ nguồn.
- **Không có dataset văn bản.** Kết luận chuyển sang corpus tin tức phải coi là giả thuyết.
- Chỉ xét FI đầy đủ. Không so sánh trực tiếp chi phí khai phá closed hoặc maximal FI.
- Cách chọn mức support cho mỗi dataset mang tính thủ công (tác giả tự thừa nhận).

## 6. Liên hệ với đề tài / Trans2Vec
- **Hồ sơ dữ liệu giao dịch cho corpus văn bản.** Coi mỗi bài là một transaction thì các độ đo của K26 tính được ngay.
  - Ví dụ, từ thống kê trong [13], **Snippets** có density $\approx 13{,}00 / 23.686 \approx 5{,}5\times10^{-4}$, tức **thưa cỡ Retail**.
  - VNTC-10 trong GĐ6 dùng top-k = 50 item mỗi bài. Giao dịch dài gần gấp 4 lần Snippets, nên similarity và số FI ở cùng δ sẽ khác hẳn. Đây là **giả thuyết giải thích** vì sao vai trò của FI khác nhau giữa hai corpus (E8).
- **Chọn thuật toán cho mô-đun FIM:** mã gốc của [13] dùng `FIM_Trans.exe` (chỉ chạy trên Windows); GĐ6 tự cài đặt đếm cặp/bộ ba. K26 là căn cứ có trích dẫn để đề xuất **LCMv3 hoặc FP-Growth** (có sẵn trong SPMF và pyfim) cho hệ thống thật.
- **Củng cố H2 và các ablation A2:** k = 100 sinh 30.866 FI (gấp 9 lần k = 50) mà không cải thiện. Đây là đúng hiện tượng "bùng nổ, cần top-k hoặc hậu xử lý" mà K26 kết luận.
- **Chọn δ:** K26 cho thấy đặc trưng dữ liệu đổi theo δ, nên **δ cần được quét và báo cáo kèm hồ sơ dữ liệu**, thay vì một điểm elbow duy nhất. Điều này khớp với hạn chế ở Mục 5 của RESULTS.md ("chưa quét δ có hệ thống").

## 7. Ý dùng trong survey
- **Chương 3.2:** bảng họ thuật toán FIM (ngang / dọc / lai / LCM) và 8 độ đo hồ sơ dữ liệu.
- **Chương 6:** chi phí FIM là hàm của δ và hồ sơ dữ liệu, không phải hằng số.
- **Chương 7:** bảng "hồ sơ giao dịch" Snippets so với VNTC (E8).
- **Chương 9:** mô-đun FIM dùng LCM/FP-Growth, giới hạn độ dài itemset và top-k item. Báo cáo quét δ.
