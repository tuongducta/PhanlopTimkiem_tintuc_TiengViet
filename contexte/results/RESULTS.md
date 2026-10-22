# GĐ6 — Kết quả thực nghiệm Trans2Vec trên tin tức tiếng Việt (VNTC-10)

*07/10/2026 · Toàn bộ số liệu sinh từ `src/experiments/results/` (bảng đầy đủ: `results/tables.md`)*

## 1. Thiết lập

| Hạng mục | Cấu hình |
|---|---|
| **Dữ liệu** | VNTC-10 (MIT, github.com/duyvuleo/VNTC): **33.759 train / 50.373 test**, 10 chủ đề, cách chia gốc của Hoang et al. 2007. Bài dài trung bình **488 âm tiết** (trung vị 351) |
| **Tiền xử lý (M1)** | Unicode NFC, chữ thường, bỏ số và dấu câu. Hai góc nhìn: **từ** (pyvi) và **âm tiết** (không tách từ). Từ dừng xác định theo dữ liệu: token xuất hiện trong > 30% bài train (78 từ / 149 âm tiết); bỏ token có tần suất văn bản < 3 |
| **Lọc item (M2)** | Mỗi bài giữ **k = 50** item có tf·idf cao nhất (IDF tính trên train); thực nghiệm phụ với k = 20, 100 |
| **Khai phá FI (M3)** | Itemset độ dài ≤ 3. Đếm cặp bằng XᵀX thưa, bộ ba bằng cắt tỉa kiểu Apriori. δ chọn bằng **elbow** trên tập train, cho ra **δ = 0,535%** (181 bài) |
| **Trans2Vec (M4)** | gensim 4.4 Doc2Vec PV-DBOW (dm = 0, dbow_words = 0), d = 128, negative = 5, sample = 0, 20 epoch, min_count = 1. Bốn biến thể: TRANS-IT, TRANS-FI, IND (trung bình 2 vector), JOI (item ∪ FI). Vector test sinh bằng `infer_vector` (20 epoch) |
| **Phân loại (M6)** | SVM tuyến tính C = 1 (như [13]) và hồi quy logistic C = 1; trên vector chuẩn hóa L2. E5: C chọn bằng 3-fold CV trên train. Độ đo chính: **Macro-F1** |
| **Tìm kiếm (M7)** | 1.000 truy vấn (100 bài test mỗi chủ đề), kho = 33.759 bài train, cosine. Liên quan = cùng chủ đề (nhãn thay thế). P@10, MAP@100, nDCG@10 |
| **Chống rò rỉ** | Từ vựng, IDF, từ dừng, δ, FI, embedding đều chỉ fit trên train |
| **Môi trường** | `.venv-exp` (Python 3.11, gensim 4.4.0, pyvi, scikit-learn 1.9, numpy 2.2.6, scipy 1.15.3), MacBook 11 lõi CPU, không GPU |

## 2. Kết quả chính

### 2.1 Phân loại chuyên mục

**Bảng 1.** Macro-F1 trên 50.373 bài test (từ, k = 50, d = 128)

| Phương pháp | SVM C = 1 | LR C = 1 | Ghi chú |
|---|---|---|---|
| TF-IDF toàn văn (43.777 chiều) | **0,903** | **0,907** | Baseline mạnh nhất |
| MLP-128 có giám sát [7] | 0,902 | — | Học từ nhãn |
| TF-IDF trên 50 item mỗi bài | 0,889 | — | Lọc top-k chỉ mất 1,4 điểm |
| BOW toàn văn | 0,874 | — | |
| LDA-100 | 0,827 | — | |
| FI-BIN / FI-SUP (3.586 chiều) | 0,824 / 0,788 | — | |
| TF-IDF + χ² (128 chiều) | 0,754 | — | |
| **TRANS-IT** *(train suy luận lại)* | **0,841** | **0,847** | ≡ Doc2Vec PV-DBOW |
| **TRANS-FI** *(train suy luận lại)* | 0,820 | 0,826 | |
| **Trans2Vec-JOI** *(train suy luận lại)* | **0,842** | **0,849** | LR + C tinh chỉnh: 0,852 |
| Trans2Vec-JOI *(train = model.dv)* | 0,766 ± 0,001 | 0,814 | 3 seed; xem Mục 3.1 |
| TRANS-IT / FI / IND *(model.dv)* | 0,771 / 0,757 / 0,767 | — | 3 seed, độ lệch chuẩn ≤ 0,006 |

![Macro-F1](results/fig_macro_f1.png)

### 2.2 Tìm kiếm ngữ nghĩa

**Bảng 2.** Truy vấn là bài báo (1.000 truy vấn)

| Biểu diễn | P@10 | MAP@100 | nDCG@10 |
|---|---|---|---|
| TF-IDF toàn văn | 0,731 | 0,565 | 0,740 |
| LDA-100 | 0,760 | 0,603 | 0,765 |
| TRANS-FI | 0,782 | 0,651 | 0,788 |
| TRANS-IT | 0,795 | 0,671 | 0,800 |
| **Trans2Vec-JOI** | **0,805** | **0,686** | **0,809** |
| *MLP-128 có giám sát* | *0,889* | *0,856* | *0,891* |

*MLP-128 được học từ chính nhãn chủ đề, mà nhãn chủ đề lại là tiêu chí "liên quan", nên con số của nó không so sánh công bằng được (in nghiêng). Bản Trans2Vec "train suy luận lại" (E6) cho kết quả gần như nhau: JOI 0,812, IT 0,803.*

**Bảng 3.** Truy vấn từ khóa ngắn (A6: 3 từ có tf·idf cao nhất của bài truy vấn)

| Nhóm truy vấn | Số truy vấn | TF-IDF nDCG@10 | JOI nDCG@10 |
|---|---|---|---|
| Tất cả | 1.000 | 0,634 | **0,692** |
| Có chứa FI | 56 | 0,805 | **0,852** |
| Không chứa FI | 944 | 0,624 | **0,686** |

### 2.3 Thực nghiệm loại trừ

**Bảng 4.** Vai trò của FI: JOI − TRANS-IT (Macro-F1)

| Cấu hình | FI / bài | train = `model.dv` (SVM C = 1) | **train suy luận lại (LR C = 1)** |
|---|---|---|---|
| Từ, k = 20 | 5,7 | −0,5 | — |
| Từ, k = 50 | 38 | −0,5 (3 seed) | **+0,1** |
| Từ, k = 100 | 282 | +3,7 | **−0,3** |
| Âm tiết, k = 50 | 96 | +4,2 (FI − IT: +4,1) | **+0,9** |

| Ablation | Kết quả |
|---|---|
| **A1** âm tiết so với từ | TF-IDF: 0,891 so với 0,903. TRANS-IT: 0,816 so với 0,847. JOI: 0,824 so với 0,849 (LR, suy luận lại). Không tách từ làm mất khoảng 1–3 điểm |
| **A2** k | k = 100: 30.866 FI (gấp 9 lần k = 50), khai phá 14 s, JOI huấn luyện 56 s + suy luận 220 s (k = 50: 16 s + 42 s), mà không cải thiện khi đánh giá nhất quán |
| **A3** chỉ FI đóng | 0,770 so với JOI 0,766 (model.dv). *Đính chính 22/10:* ở cấu hình này mọi FI đều đóng, nên hai tập FI giống hệt nhau; chênh lệch là dao động ngẫu nhiên (Mục 7.1) |
| **A4** d ∈ {64, 128, 256} | 0,775 / 0,767 / 0,764 (model.dv). Không tăng theo d, khớp với quan sát của [13] |
| **A5** JOI ghép thẳng với TF-IDF | 0,867 < TF-IDF 0,903. Hai khối lệch thang đo; cần chuẩn hóa hoặc gán trọng số |

### 2.4 Diễn giải: FI đặc trưng cho từng chuyên mục (M6)

FI có tích vô hướng lớn nhất với tâm vector bài báo của từng chuyên mục (JOI, từ, k = 50):

| Chuyên mục | FI tiêu biểu |
|---|---|
| Kinh doanh | {doanh_nghiệp, thị_trường}, {thương_mại, thị_trường}, {tỷ, usd} |
| Thế giới | {iraq, mỹ}, {baghdad, iraq}, {bush, tổng_thống}, {bầu_cử, tổng_thống} |
| Thể thao | {cúp, đội}, {thi_đấu, vô_địch}, {chung_kết, đội}, {bóng_đá, trận} |
| Pháp luật | {công_an, tội}, {bắt, án}, {tỉnh, điều_tra} |
| Sức khỏe | {bệnh, chữa}, {chữa, thuốc}, {bệnh, triệu_chứng} |
| Vi tính | {máy_tính, phần_mềm}, {dịch_vụ, internet}, **{e, mail}** |

{e, mail}: pyvi tách sai "email" thành hai token, và FI tự ghép lại. Đây là minh họa cụ thể cho giả thuyết "FI bù lỗi tách từ". Tuy vậy, chỉ **713/5.299 (13,5%)** cặp âm tiết phổ biến trùng một từ của pyvi. Phần lớn FI âm tiết là các âm tiết thuộc những từ khác nhau nhưng hay đi cùng nhau, không phải từ ghép.

### 2.5 E7 — Tái hiện Trans2Vec trên Snippets bằng dữ liệu và mã nguồn chính thức
`src/experiments/replicate_snippets.py`, dữ liệu lấy từ `sources/repos/Trans2Vec/datasets/snippets/` (FI tại δ = 0,2%, 2.667 FI). Cấu hình theo `codes/trans2vec_joi_classify.py`: PV-DBOW d = 128, **50 epoch**, min_count = 0, `LinearSVC()` C = 1, không chuẩn hóa. Chia cố định 10.060 / 2.280 như Bảng 1 của [13]. 3 seed.

**Bảng 5.** Accuracy (%) trên Snippets

| Phương pháp | Bài báo [13] | Transductive (như mã gốc) | Inductive (như E6) |
|---|---|---|---|
| TRANS-IT | 75,23 | **75,29 ± 0,66** | 73,44 ± 0,60 |
| TRANS-FI | 77,88 | 75,23 ± 0,47 | 74,84 ± 0,64 |
| Trans2Vec-JOI | 79,05 | 75,99 ± 0,43 | 76,51 ± 0,14 |
| **JOI − IT** | **+3,82** | **+0,70** | +3,07 |

**Ý nghĩa:**
- Cách cài đặt của đề tài là **chính xác**: TRANS-IT tái hiện đúng con số của bài báo.
- **Phần đóng góp của FI không tái hiện được**, ngay trên dữ liệu và FI do chính tác giả cung cấp: JOI chỉ hơn IT 0,7 điểm so với 3,8 trong bài báo. Điều này nhất quán với kết quả trên VNTC (−0,3 đến +0,9). Nguyên nhân có thể nằm ở khác biệt phiên bản (bài báo dùng gensim 3.4), ở siêu tham số không công bố, hoặc ở độ dao động giữa các lần chạy, vì bài báo không báo độ lệch chuẩn.
- **Mã nguồn chính thức khác bài báo ở 4 điểm:**
  1. học transductive (Doc2Vec học trên cả tài liệu test, không dùng nhãn);
  2. 50 epoch, không được nêu trong bài;
  3. có tùy chọn tinh chỉnh C, trong khi bài ghi C = 1 cố định;
  4. lỗi `if/else` khiến Snippets thực tế dùng 80% (9.872 bài) làm train thay cho 10.060.
- Cảnh báo `our_dot_float` cũng xuất hiện ở đây, mỗi mô hình một lần; kết quả vẫn khớp (Mục 3.3).

## 3. Phát hiện về phương pháp đánh giá (quan trọng)

### 3.1 Lệch phân phối giữa vector train và test
Theo cách làm phổ biến (và có vẻ cũng là cách của [13]), vector train lấy từ `model.dv` (học cùng mô hình), còn vector test sinh bằng `infer_vector`. Trên VNTC, cách này:
- làm Trans2Vec **thấp hơn 7–8 điểm Macro-F1** so với khi suy luận lại vector train bằng cùng quy trình như test (JOI: 0,766 → 0,842 với SVM C = 1);
- khiến CV trên train chọn C quá lớn (10–100) mà điểm test lại *giảm* (E5);
- **tạo ra những "cải thiện nhờ FI" giả** (+3,7 với k = 100; +4,1 ở âm tiết). Chúng gần như biến mất khi đánh giá nhất quán (Bảng 4).

**Khuyến nghị:** khi dùng PV-DBOW / Trans2Vec, vector train và test phải được sinh bằng cùng một quy trình. Đây là bổ sung cụ thể cho Mục 7.3 (giao thức chuẩn) của survey.

### 3.2 Hai lỗi cấu hình tái hiện kiểu lỗi đã nghi ở bài [8]
- **Huấn luyện thiếu:** với 5 epoch trên mẫu 3.000 bài, chuẩn vector trung bình chỉ 0,063 (gần giá trị khởi tạo) và accuracy ≈ 0,16 (ngẫu nhiên 0,10). Với 20 epoch: chuẩn 1,86, accuracy 0,68. Đây chính là cơ chế "vector chưa được huấn luyện" mà survey dùng để giải thích kết quả ≈ 50% của [8].
- **Cách tính elbow:** chuẩn hóa trên thang log-log chọn δ = 2,16%, cho ra 255 FI, chỉ 20 cặp, và 82% bài test không có FI dài ≥ 2, tức Trans2Vec suy biến thành TRANS-IT. Chuẩn hóa tuyến tính (đúng cách đọc Fig. 4 của [13]) chọn δ = 0,535%, cho ra 3.586 FI. Ngoài ra, cả 4 cấu hình đều chọn cùng δ, nên elbow trên lưới hình học kém nhạy.

### 3.3 Sự cố môi trường
gensim không build được trên Python 3.14. Bản đầu trên Python 3.11 (numpy 2.4 / scipy 1.17) báo `Exception ignored in our_dot_float`.

**Đính chính (08/10):** sau khi hạ xuống numpy 2.2.6 / scipy 1.15.3, cảnh báo này **vẫn còn**: 193 lần (E1–E4), 70 lần (E5), 128 lần (E6). Bản trước đã ghi nhầm là "hết lỗi" do chỉ kiểm tra trên bản chạy thử. Kiểm tra lại cho thấy cảnh báo **vô hại**:
- nó xuất hiện đúng một lần mỗi khi khởi tạo một mô hình (3 mô hình → 3 cảnh báo, như nhau với 1 hay 8 luồng), tức phát sinh ở bước khởi tạo, không phải trong tính toán;
- vector đầu ra không có NaN, chuẩn hợp lý;
- toy test (hai cụm tách bạch) đạt accuracy 1,0;
- tái hiện TRANS-IT trên Snippets khớp bài gốc tới 0,06 điểm (Mục 2.5).

## 4. Trả lời câu hỏi nghiên cứu (cập nhật từ thực nghiệm)

| Câu hỏi | Trả lời |
|---|---|
| **RQ3 — FI có làm giàu embedding trên tin tức tiếng Việt?** | **Gần như không cho phân loại**: JOI − IT = −0,3 đến +0,9 điểm khi đánh giá nhất quán. Mức +2,7 của [13] trên Snippets không tái hiện được trên VNTC, **và cũng không tái hiện được trên chính Snippets** với dữ liệu và mã nguồn của tác giả (JOI − IT: +0,7 so với +3,8, Mục 2.5). Lợi ích của FI nằm ở **diễn giải** (FI chuyên mục đọc được, tự sửa lỗi tách từ) và ở **tìm kiếm**, nơi JOI tốt nhất trong các biểu diễn không giám sát (nDCG@10 0,809 so với IT 0,800, TF-IDF 0,740) |
| **H1 (mất tần suất)** | Được xác nhận: TF-IDF (có tần suất) 0,903 so với embedding tập hợp 0,849. Cách ghép thẳng (A5) chưa khai thác được; cần phương án khác |
| **H2 (bùng nổ FI)** | Được xác nhận định lượng: k = 50 → 3.586 FI; k = 100 → 30.866 FI, tổng thời gian huấn luyện + suy luận gấp khoảng 4,7 lần (275 s so với 58 s), không cải thiện. Top-k ≈ 50 là đủ. *Đính chính 22/10:* lọc FI đóng không có tác dụng ở cấu hình này vì mọi FI đều đóng (Mục 7.1) |
| **H5 (truy vấn)** | `infer_vector` xử lý được truy vấn 3 từ. 94% truy vấn không chứa FI nhưng JOI vẫn hơn TF-IDF, nên lợi thế chủ yếu đến từ biểu diễn dày |
| **H7 (chi phí)** | Rẻ: khai phá FI 3 s, huấn luyện JOI 16 s, suy luận 50.373 bài 42 s, toàn bộ trên CPU (k = 50) |
| **A1 (từ so với âm tiết)** | Không tách từ mất 1–3 điểm với mọi biểu diễn. FI chỉ bù được một phần nhỏ (+0,9) |

## 5. Hạn chế của thực nghiệm
- Một corpus (VNTC-10), giai đoạn 2003–2006, 10 chủ đề tương đối tách bạch. Chưa thử corpus khó ≥ 25 chuyên mục.
- Kết quả E6 (đánh giá nhất quán) mới chạy 1 seed. Các kết quả 3 seed ở E1 dùng `model.dv`.
- Tiêu chí "liên quan" trong tìm kiếm là nhãn thay thế (cùng chủ đề), chưa có đánh giá thủ công.
- Chưa có PhoBERT (không có GPU / PyTorch), Top2Vec, Sqn2Vec.
- δ được chọn giống nhau ở mọi cấu hình. Chưa quét δ một cách có hệ thống.
- Đoạn đầu E6 chạy chồng khoảng 1 phút với cuối E5 (lệnh chờ bắt nhầm dòng log), có thể ảnh hưởng nhẹ đến số đo thời gian, không ảnh hưởng độ chính xác.

## 6. Tái lập
```bash
.venv-exp/bin/python src/experiments/prepare.py          # ~1 phút
.venv-exp/bin/python src/experiments/run_experiments.py  # E1–E4, ~27 phút
.venv-exp/bin/python src/experiments/run_tuned.py        # E5, ~12 phút
.venv-exp/bin/python src/experiments/run_consistent.py   # E6, ~20 phút
.venv-exp/bin/python src/experiments/replicate_snippets.py # E7, ~5 phút (cần repo sources/repos/Trans2Vec)
.venv-exp/bin/python src/experiments/make_report.py      # bảng + hình
.venv-exp/bin/python src/experiments/run_e8_profile.py   # E8, ~7 phút
.venv-exp/bin/python src/experiments/run_e9_fi_types.py --delta 0.002 --skip-closed  # E9, ~1–2 giờ
```

## 7. GĐ10 (22/10/2026): E8 và E9

Thiết kế ở `contexte/plans/KE_HOACH_SURVEY_v3.md` Mục 10. Số liệu gốc: `src/experiments/results/e8_profile.json`, `e9_fi_types.json`.

### 7.1 E8 — Hồ sơ dữ liệu giao dịch theo K26

`src/experiments/run_e8_profile.py`, chỉ tập train. Ở mỗi δ, bỏ item có support < δ rồi tính độ đo (như K26). Độ đo theo K26 Eq. 1–12:
- Density, IT, |T|, |B| tái tạo đúng Bảng 3 của K26 (kiểm bằng phép tính trên Chess, Mushrooms, Retail).
- Similarity, ID, IS cài theo công thức in trong bài, nhưng công thức đó không cho ra số trong Bảng 3. Vì vậy ba độ đo này chỉ dùng để so giữa các corpus ở đây. "Sim %" là số item một giao dịch chia sẻ trung bình với một giao dịch khác, tính theo % độ dài giao dịch.

**Bảng 6.** Hồ sơ giao dịch trước khi lọc (δ = 0) và ở δ dùng trong thực nghiệm

| Cấu hình | δ | \|T\| | \|B\| | IT (± std) | Density | Sim % | FI (≤ 3) | FI dài ≥ 2 / bài | Bài không có FI dài ≥ 2 | FI không đóng | JOI − IT (đánh giá nhất quán) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Snippets | 0 | 10.060 | 20.302 | 13,0 ± 3,6 | 6,4×10⁻⁴ | 1,56 | — | — | — | — | |
| Snippets | 0,2% (δ của [13]) | 10.047 | 1.125 | 8,7 ± 2,9 | 7,7×10⁻³ | 2,23 | 2.740 | 5,7 | 14% | 3,4% | **+3,07** (E7 inductive) |
| VNTC từ, k = 50 | 0 | 33.759 | 43.572 | 49,0 ± 4,0 | 1,1×10⁻³ | 1,10 | — | — | — | — | |
| VNTC từ, k = 50 | 0,535% | 33.759 | 2.102 | 26,0 ± 7,5 | 1,2×10⁻² | 1,88 | 3.586 | 12,0 | 14% | 0% | **+0,1** (E6) |
| VNTC từ, k = 100 | 0,535% | 33.759 | 3.232 | 59,6 ± 16,1 | 1,8×10⁻² | 3,57 | 30.866 | 222,7 | 0% | 0,02% | **−0,3** (E6) |
| VNTC âm tiết, k = 50 | 0,535% | 33.759 | 1.991 | 39,0 ± 7,5 | 2,0×10⁻² | 3,12 | 8.984 | 56,8 | 1% | 0,01% | **+0,9** (E6) |
| VNTC từ, không lọc top-k | 0 | 33.759 | 43.777 | 138,0 ± 92,2 | 3,2×10⁻³ | 6,82 | — | — | — | — | |
| *Retail (K26, Bảng 3)* | 0 | 88.162 | 16.470 | 10,3 ± 8,2 | 6,3×10⁻⁴ | — | | | | | |

Hai mức δ của nhóm phải đọc khác nhau: 0,2% là δ do tác giả [13] chọn cho Snippets, còn 0,535% là δ do elbow của nhóm chọn cho VNTC. Ở δ = 0,2%, VNTC từ k = 50 có 22.291 FI, k = 100 có 284.384 FI, âm tiết có 84.097 FI.

**Nhận xét:**
1. **Hồ sơ dữ liệu không giải thích được vì sao FI giúp Snippets mà không giúp VNTC.**
   - Trước khi lọc, hai corpus cùng loại *thưa*: density 6,4×10⁻⁴ so với 1,1×10⁻³, cả hai cùng bậc với Retail. Sim % cũng gần nhau (1,56 so với 1,10).
   - Ở δ dùng trong thực nghiệm, tỉ lệ bài không có FI dài ≥ 2 bằng nhau (14%).
   - Khác biệt rõ nhất là **độ dài giao dịch**: 13 item so với 49. Vì vậy FI chiếm tỉ trọng token khác nhau trong JOI: khoảng 30% với Snippets (5,7 trên 13 + 5,7), khoảng 20% với VNTC k = 50.
   - Nhưng trong chính VNTC, tỉ trọng FI tăng lên khoảng 54% (âm tiết) và 72% (k = 100) mà JOI − IT vẫn chỉ +0,9 và −0,3. Lượng FI vì thế cũng không giải thích được.
   - Giả thuyết ở `synthesis_v3.md` §5.3 ("thưa so với dày") **không được ủng hộ**. Các khả năng còn lại chưa kiểm chứng: văn bản ngắn hưởng lợi vì FI làm dài thêm "câu" huấn luyện cho vector bài; độ khó của tác vụ (Snippets accuracy khoảng 75%, VNTC Macro-F1 khoảng 0,85); khác ngôn ngữ (tiếng Anh đã stem so với tiếng Việt đã tách từ).
2. **δ làm đổi hồ sơ dữ liệu rất mạnh, đúng như K26.** Với VNTC k = 50, từ δ = 0 lên 2%: |B| giảm từ 43.572 xuống 268, density tăng 28 lần, Sim % từ 1,10 lên 3,60. Một corpus "thưa" thành "dày vừa" chỉ vì đổi ngưỡng. Hệ quả: δ phải được báo cáo kèm hồ sơ dữ liệu.
3. **FI không đóng rất hiếm trong giao dịch văn bản.**
   - Tỉ lệ cao nhất là 3,4% (Snippets, δ = 0,2%). VNTC từ k = 50 chỉ 0,17% ở δ = 0,2%, và bằng 0 ở mọi δ ≥ 0,535%.
   - Các FI không đóng hầu hết là cụm cố định hoặc chữ mẫu: {dir, yahoo} → {dir, directori, yahoo}; {wiki, …} → {…, wikipedia}; {games, đội} → {games, sea, đội}; {a, milan} → {a, milan, serie}; {hoátiêu} → {ban_văn, hoátiêu} (dòng ghi chuyên mục bị tách từ sai).
   - Lý do: một tập và tập cha của nó chỉ cùng support khi các item *luôn* đi cùng nhau, mà trong văn bản tự nhiên điều này chỉ xảy ra với cụm cố định.
   - **Hệ quả cho K25:** lợi ích nén của closed FI gần như không có với văn bản đã lọc top-k và FI dài ≤ 3. Đóng góp có thể dùng được của K25 cho đề tài nằm ở CICFI (E9), không nằm ở closed FI. Ablation A3 (Mục 2.3) so hai tập FI giống hệt nhau.
4. **Bùng nổ FI (H2) đo được theo δ:** VNTC từ k = 100 ở δ = 0,2% sinh 284.384 FI, trung bình 941 FI dài ≥ 2 mỗi bài.
5. **Kiểm tra chéo:** hàm khai phá của nhóm cho 2.740 FI trên Snippets ở δ = 0,2%, gần với 2.667 FI trong dữ liệu tác giả cung cấp. Phần chênh có thể do mã gốc không giới hạn độ dài FI.

### 7.2 E9 — Loại FI: all, ổn định (CICFI), ngẫu nhiên

`src/experiments/run_e9_fi_types.py --delta 0.002 --skip-closed`. VNTC từ, k = 50; JOI so với TRANS-IT; giao thức E6 (train và test cùng `infer_vector`, LR C = 1); **3 seed**; tìm kiếm 1.000 truy vấn bài báo.
- Bỏ biến thể closed, vì ở δ = 0,2% chỉ 0,17% FI là không đóng (Mục 7.1).
- Lần chạy đầu bị dừng và sửa thiết kế: ngưỡng "cận dưới Wilson ≥ δ trong từng chuyên mục" giữ lại cả 17.349/17.349 FI. Thay bằng ba biến thể **cùng cỡ** (10.374 FI dài ≥ 2), chỉ khác tiêu chí chọn.
- CICFI toàn cục tương đương nâng δ lên 0,249% (support ≥ 84 bài); điều này được kiểm bằng `assert` trong script.
- Ba tập cùng cỡ trùng nhau một phần: ổn định chuyên mục trùng 8.054/10.374 với CICFI toàn cục, ngẫu nhiên trùng 6.209/10.374.

**Bảng 7.** Kết quả E9 (trung bình ± độ lệch chuẩn qua 3 seed; Δ so với TRANS-IT cùng seed)

| Biến thể | FI dài ≥ 2 | FI dài ≥ 2 / bài | Macro-F1 | Δ Macro-F1 | nDCG@10 | Δ nDCG@10 | Thời gian huấn luyện + suy luận |
|---|---|---|---|---|---|---|---|
| TRANS-IT (không FI) | 0 | 0 | 0,8473 ± 0,0001 | — | 0,8090 ± 0,0024 | — | 98 s |
| JOI, all FI, δ = 0,535% (cấu hình chính) | 1.484 | 12,0 | 0,8498 ± 0,0010 | +0,0025 ± 0,0011 | 0,8107 | +0,0018 | 98 s |
| **JOI, all FI, δ = 0,2%** | 17.349 | 57,0 | **0,8535 ± 0,0007** | **+0,0062 ± 0,0007** | 0,8164 | +0,0074 | 194 s |
| JOI, CICFI toàn cục (≡ δ' = 0,249%) | 10.374 | 41,6 | 0,8526 ± 0,0013 | +0,0053 ± 0,0011 | 0,8143 | +0,0054 | 147 s |
| JOI, ổn định theo chuyên mục (có giám sát) | 10.374 | 39,9 | 0,8534 ± 0,0002 | +0,0061 ± 0,0002 | 0,8175 | +0,0085 | 138 s |
| JOI, ngẫu nhiên cùng cỡ | 10.374 | 25,4 | 0,8533 ± 0,0006 | +0,0059 ± 0,0005 | 0,8179 | +0,0089 | 114 s |

Thời gian là trung bình 3 seed. Seed 1 của hai dòng đầu chạy chồng với E8, nên thời gian của chúng có thể bị đội lên.

**Nhận xét:**
1. **Hạ δ giúp, nhưng rất ít.** Từ 0,535% xuống 0,2%, số FI tăng 12 lần. Đóng góp của FI tăng từ +0,0025 lên +0,0062 Macro-F1 và từ +0,0018 lên +0,0074 nDCG@10. Mức tăng nhất quán qua 3 seed (độ lệch chuẩn ≤ 0,001) nên là thật, nhưng chỉ khoảng 0,6 điểm. Đổi lại, thời gian gấp đôi. JOI tốt nhất (0,8535) vẫn kém TF-IDF (0,907) khoảng 0,05.
2. **Tiêu chí chọn FI không quan trọng.** Ở cùng cỡ 10.374 FI, ba cách chọn cho kết quả ngang nhau trong vùng nhiễu: support toàn cục (+0,0053), ổn định theo chuyên mục dù dùng nhãn (+0,0061), và ngẫu nhiên (+0,0059). Bộ ngẫu nhiên thậm chí ít FI mỗi bài hơn (25,4 so với khoảng 40) mà vẫn ngang. Vậy **CICFI của K25 không đem lại gì thêm** so với chọn ngẫu nhiên cùng số lượng. Tín hiệu đến từ việc *có thêm* token đồng xuất hiện, không đến từ việc chọn *đúng* FI.
3. **Trả lời RQ3 (loại FI):** với tin tức tiếng Việt đã lọc top-k, closed FI không tạo khác biệt vì gần như mọi FI đã đóng (E8), và CICFI không hơn ngẫu nhiên (E9). Khuyến nghị cho hệ thống: giữ FI đầy đủ, chọn δ theo ngân sách tính toán. Không cần bước lọc FI đóng hay lọc theo khoảng tin cậy.
4. **Liên hệ E8:** ngay cả khi FI chiếm khoảng 54% token (57 FI dài ≥ 2 trên 49 item), JOI chỉ hơn IT 0,6 điểm. Như vậy mức +3 điểm trên Snippets không đến từ số lượng FI.
