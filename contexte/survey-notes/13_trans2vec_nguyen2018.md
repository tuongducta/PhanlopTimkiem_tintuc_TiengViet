# [13] Trans2Vec: Learning Transaction Embedding via Items and Frequent Itemsets

> **Vai trò trong survey:** PHƯƠNG PHÁP LÕI · Taxonomy nhánh **E** · Dùng ở Chương 3 (nền tảng), Chương 5 (toàn bộ), Chương 9 (đề xuất hệ thống)

## 1. Thông tin thư mục

| | |
|---|---|
| **IEEE** | D. Nguyen, T. D. Nguyen, W. Luo, and S. Venkatesh, "Trans2Vec: Learning transaction embedding via items and frequent itemsets," in *Advances in Knowledge Discovery and Data Mining (PAKDD 2018)*, LNAI vol. 10939. Cham: Springer, 2018, pp. 361–372, doi: 10.1007/978-3-319-93040-4_29. |
| Đơn vị | Center for Pattern Recognition and Data Analytics (PRaDA), Deakin University, Úc |
| Loại | Hội nghị KDD hạng tốt (PAKDD), bài 12 trang |
| File | `sources/papers/[13] Tran2Vec-nguyen2018.pdf` |

## 2. Bài toán và động lực

- **Dữ liệu transaction:** mỗi transaction là một *tập* item rời rạc, không có thứ tự (giỏ hàng, triệu chứng bệnh, từ khóa tìm kiếm). Các thuật toán ML (SVM, K-means) cần vector độ dài cố định.
- **Cách truyền thống:** khai phá **Frequent Itemsets (FI)** rồi biểu diễn transaction bằng vector nhị phân $f(T)=[x_1,\dots,x_F]$ với $x_i = 1$ nếu $X_i \subseteq T$. Cách này gặp hai vấn đề:
  1. **Số chiều rất lớn:** số FI có thể vượt $10^5$ khi $\delta < 5\%$.
  2. **Thưa (sparsity).**
- **Các cách khắc phục đi trước** (discriminative FI dựa trên information gain, support difference, support ratio) đều **cần nhãn**, tức là có giám sát. Hệ quả là (a) biểu diễn gắn chặt với một tác vụ, không chuyển sang clustering được; (b) phụ thuộc vào lượng nhãn lớn.
- **Mục tiêu:** học hàm $f: D \to \mathbb{R}^d$ **không giám sát**, sao cho hai transaction giống nhau có vector gần nhau.

## 3. Phương pháp

### 3.1 Định nghĩa
- Tập item $I=\{i_1,\dots,i_M\}$, CSDL $D=\{T_1,\dots,T_N\}$, $T_i \subseteq I$.
- Support: $\text{sup}(X) = |\{T_i \in D : X \subseteq T_i\}| / |D|$. $X$ là FI nếu $\text{sup}(X) \ge \delta$.

### 3.2 TRANS-IT: embedding từ item (thực chất là PV-DBOW)
Coi transaction là "tài liệu" và item là "từ". Hàm mục tiêu cực đại hóa $\sum_{j} \log \Pr(i_j \mid T_t)$, với $\Pr$ là softmax trên $g(i_j)\cdot f(T_t)$. Xấp xỉ bằng **negative sampling** (Eq. 3):

$$O_1 = -\log\sigma\big(g(i_j)\cdot f(T_t)\big) - \sum_{n=1}^{K}\mathbb{E}_{i_n\sim P(i)}\log\sigma\big(-g(i_n)\cdot f(T_t)\big)$$

Tối ưu bằng SGD.

### 3.3 TRANS-FI: embedding từ FI
Như trên, nhưng "từ vựng" là tập FI của transaction, $F(T_t)=\{X_1,\dots,X_l\}$, với embedding $h(X_j)$ (Eq. 5). **Vấn đề:** transaction không chứa FI nào thì nhận vector 0.

### 3.4 Hai mô hình Trans2Vec
| Mô hình | Cách làm | Ưu / nhược |
|---|---|---|
| **Trans2Vec-IND** (individual) | Học $f_1(T)$ từ item, $f_2(T)$ từ FI rồi lấy trung bình $f(T) = (f_1 + f_2)/2$ | Đơn giản, nhưng không nắm quan hệ giữa item và FI |
| **Trans2Vec-JOI** (joint) | Gộp item ∪ FI thành tập **pattern** $p_j$ và học một vector duy nhất (Eq. 6–8): $O = -\sum_{p_j \in I(T)\cup F(T)} \log \Pr(p_j\mid T)$ | Nắm đồng thời quan hệ transaction–item và transaction–FI. **Tốt nhất** |

### 3.5 Tham số
- $d = 128$.
- $\delta$ chọn bằng **elbow method** trên đường cong "số FI theo δ" của tập train, không dùng nhãn. Tham khảo Rousseau et al., ACL 2015.

## 4. Thực nghiệm

| Dataset | #trans | #train/#test | #items | Độ dài TB | #lớp |
|---|---|---|---|---|---|
| **Snippets** (đoạn trích kết quả tìm kiếm web, Phan et al. WWW 2008) | 12.340 | 10.060 / 2.280 | 23.686 | 13,00 | 8 |
| Cancer (bệnh án) | 15.000 | 12.000 / 3.000 | 3.234 | 6,00 | 3 |
| Retail (UK online retail) | 3.000 | 2.400 / 600 | 3.376 | 26,93 | 2 |
| Food (giỏ thực phẩm) | 4.000 | 3.200 / 800 | 1.559 | 25,87 | 2 |

- **Baseline (đều không giám sát):** BOW, TF-IDF (nhóm NLP); FI-BIN, FI-SUP (nhóm FI); TRANS-IT, TRANS-FI (nhóm embedding).
- **Bộ phân loại:** SVM tuyến tính (LIBSVM), **C = 1 cố định, không tinh chỉnh**, vì mục tiêu là so sánh biểu diễn.
- **Giao thức:** cùng tập train/test cho mọi phương pháp, lặp 10 lần, báo Accuracy và F1-macro trung bình. Không báo độ lệch chuẩn, với lý do "< 10⁻²".

### Kết quả (Table 2)

| Phương pháp | Snippets AC/F1 | Cancer AC/F1 | Retail AC/F1 | Food AC/F1 |
|---|---|---|---|---|
| BOW | 66,32 / 65,83 | 48,57 / 48,57 | 77,33 / 77,31 | 63,12 / 63,12 |
| TF-IDF | 70,26 / 69,52 | 49,43 / 49,43 | 81,67 / 81,56 | 64,50 / 64,49 |
| FI-BIN | 64,52 / 63,96 | 48,52 / 48,44 | 77,67 / 77,62 | 61,75 / 61,74 |
| FI-SUP | 37,94 / 32,19 | 47,30 / 46,54 | 80,33 / 79,20 | 71,00 / 70,03 |
| TRANS-IT | 75,23 / 74,79 | 49,35 / 49,32 | 81,17 / 81,07 | 65,95 / 65,81 |
| TRANS-FI | 77,88 / 77,41 | 50,03 / 49,92 | 82,07 / 81,90 | 69,14 / 68,95 |
| Trans2Vec-IND | 78,80 / 77,92 | 50,10 / 50,02 | 82,23 / 82,12 | 69,22 / 69,12 |
| **Trans2Vec-JOI** | **79,05 / 78,31** | **50,34 / 50,28** | **83,43 / 83,36** | **72,51 / 72,47** |
| δ (elbow) | 0,2% | 0,2% | 0,7% | 0,2% |

**Nhận xét của tác giả:**
- JOI hơn BOW 4–19% và hơn TF-IDF 2–13% (tương đối).
- TRANS-FI luôn hơn TRANS-IT, tức là FI giàu thông tin hơn item đơn.
- JOI luôn hơn IND.
- **Độ nhạy:** δ chọn bằng elbow luôn cho accuracy tốt nhất. Với *d*, accuracy tăng rồi giảm trên Snippets/Food và tăng đều trên Cancer, khác với document embedding, nơi *d* lớn thường có lợi.

## 5. Đóng góp
1. Phương pháp embedding transaction đầu tiên (theo tác giả), **hoàn toàn không giám sát**.
2. Kết hợp tri thức **khai phá mẫu** (FI, đúng mạch KDD) với **học biểu diễn** (PV-DBOW).
3. Ablation đầy đủ: IT, FI, IND, JOI.

## 6. Hạn chế và phản biện
| # | Hạn chế | Hệ quả khi áp dụng cho tin tức tiếng Việt |
|---|---|---|
| H1 | Transaction là **tập**, nên **mất tần suất và thứ tự** | Tin tức dài, TF mang thông tin. Cần ablation so với TF-IDF. Hướng giải: **Sqn2Vec** (S01, cùng tác giả) dùng mẫu tuần tự nên giữ được thứ tự |
| H2 | Dữ liệu thử nghiệm có độ dài TB **6–27 item** | Một bài báo có 300–800 từ, nên **số FI bùng nổ tổ hợp** khi δ nhỏ. Cần lọc top-k từ, closed/maximal FI, giới hạn độ dài itemset, hoặc tách transaction theo câu/đoạn |
| H3 | Baseline yếu: không có LDA, Doc2Vec PV-DM, fastText, BERT; SVM không tinh chỉnh; không báo std. **Bỏ qua kết quả gốc của Snippets:** Phan et al. (WWW 2008, S18) đạt **82,18%** bằng MaxEnt + LDA học trên Wikipedia, so với JOI 79,05% (khác điều kiện: Phan dùng dữ liệu ngoài) | Survey phải bổ sung đối chứng hiện đại (PhoBERT, [7]) và cân nhắc khởi tạo hoặc kết hợp với tri thức ngoài |
| H4 | Cải thiện nhỏ trên Cancer (~50% cho mọi phương pháp, 3 lớp) | Hiệu quả phụ thuộc dữ liệu; mạnh khi FI có ý nghĩa ngữ nghĩa (Snippets là văn bản) |
| H5 | Không mô tả **suy luận vector cho transaction mới** | PV-DBOW cần bước *infer* bằng gradient. Query ngắn có thể không chứa FI nào, khi đó dùng riêng phần item. Đây là vấn đề thiết kế bắt buộc cho chức năng **tìm kiếm** |
| H6 | Chỉ đánh giá phân loại; clustering mới nằm trong hướng phát triển, retrieval thì không có | Phần tìm kiếm của đề tài là **đóng góp mới** |
| H7 | Chi phí khai phá FI và huấn luyện không được báo | Cần đo trong thực nghiệm (số FI theo δ, thời gian) |

## 7. Liên hệ với đề tài và các bài khác
- **Ánh xạ:** bài báo là transaction, từ (sau tách từ) là item, FI là **cụm từ đồng xuất hiện** kiểu {chứng_khoán, cổ_phiếu, sàn}, mang tính chuyên mục rõ.
- **Snippets là văn bản** (8 chuyên mục: business, computers, health, …), nên đây là bằng chứng trực tiếp rằng phương pháp dùng được cho phân loại chuyên mục văn bản.
- **[8]:** Doc2Vec ≈ 50% trên bình luận tiếng Việt, trong khi TRANS-IT (cùng là PV-DBOW) đạt 75% trên Snippets (văn bản ngắn). Điều này củng cố nghi ngờ [8] lỗi cài đặt.
- **[7]:** cũng 128 chiều + SVM, nhưng có giám sát. Đây là đối chứng công bằng nhất.
- **[1], [2]:** n-gram âm tiết tránh tách từ. **Giả thuyết:** Trans2Vec trên âm tiết, với FI kiểu {chứng, khoán}, có thể tự khôi phục từ ghép mà không cần bộ tách từ.
- **[3], [5]:** trích từ khóa (KeywordScore, TextRank) dùng làm **bước lọc item** để giải quyết H2.
- **[10]:** PhoBERT là trần trên tham chiếu; bảng chi phí của [10] là mẫu để đo H7.

## 8. Ý dùng trong survey
- Chương 3: nền tảng FI (support, δ) và PV-DBOW, negative sampling, dùng Eq. 1–3.
- Chương 5: trình bày 4 biến thể; bảng kết quả; hình IND vs JOI (vẽ lại Fig. 2–3); bảng hạn chế H1–H7.
- Chương 9: pipeline đề xuất giải quyết H2, H5, H6.
