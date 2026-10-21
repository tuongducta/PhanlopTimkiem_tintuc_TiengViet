# GĐ3 — Tài liệu bổ sung đã xác minh

**Ngày:** 07/10/2026 · **Phương pháp:** tìm kiếm web, đối chiếu ACL Anthology, DBLP, kho của nhà xuất bản và kho của trường, cùng danh mục tham khảo của bài [13].

**Ký hiệu trạng thái xác minh:**
- ✅ Đã xác minh qua nguồn chính thức trong phiên này.
- ☑️ Xác minh gián tiếp: trùng khớp với danh mục tham khảo của bài [13] hoặc bài gốc.
- ⚠️ Còn thiếu một chi tiết, ghi rõ chi tiết nào.

**Mức ưu tiên:** 🔴 bắt buộc trích dẫn · 🟠 nên có · ⚪ tham khảo/tùy chọn.

Mã **S01–S27** là mã tạm. Khi chốt danh mục tham khảo, chúng sẽ được đánh số tiếp sau [13] (hoặc lấp vào [11], [12]; xem đề xuất cuối file).

---

## Nhóm 1 — Họ phương pháp "pattern + embedding" của nhóm tác giả Trans2Vec (MỚI, quan trọng nhất)

> **Phát hiện:** Trans2Vec không đứng một mình. Cùng nhóm Deakin/PRaDA (Dang Nguyen, Wei Luo, Tu Dinh Nguyen, Svetha Venkatesh, Dinh Phung) đã áp dụng **cùng một mô thức** cho 4 kiểu dữ liệu: *khai phá mẫu phổ biến → coi mẫu như "từ" → học embedding kiểu PV-DBOW*. Survey có thể trình bày đây là **một mô thức (paradigm)**, không chỉ một phương pháp lẻ.

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Tóm tắt và vai trò trong survey |
|---|---|---|---|---|
| S01 | D. Nguyen, W. Luo, T. D. Nguyen, S. Venkatesh, and D. Phung, "Sqn2Vec: Learning sequence representation via sequential patterns with a gap constraint," in *Proc. ECML PKDD 2018*, LNCS 11052, Springer, 2018, pp. 569–584, doi: 10.1007/978-3-030-10928-8_34. | ✅ [mlanthology](https://mlanthology.org/ecmlpkdd/2018/nguyen2018ecmlpkdd-sqn2vec) | 🔴 | Bản cho **dữ liệu chuỗi**: mẫu tuần tự có ràng buộc khoảng cách (gap). **Giải trực tiếp hạn chế H1 của [13] (mất thứ tự từ)**, vì văn bản vốn là chuỗi. Là hướng mở rộng tự nhiên cho tin tức (Chương 5.5, Chương 10) |
| S02 | D. Nguyen, W. Luo, T. D. Nguyen, S. Venkatesh, and D. Phung, "Learning graph representation via frequent subgraphs," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2018, pp. 306–314. | ✅ [Deakin DRO](https://dro.deakin.edu.au/articles/conference_contribution/Learning_graph_representation_via_frequent_subgraphs/20800771) | 🟠 | Bản cho **đồ thị**: đồ thị con phổ biến làm đơn vị nhúng, không giám sát, dùng cho cả phân loại và **phân cụm**. Kết hợp được với graph-of-words (S04) |
| S03 | D. Nguyen *et al.*, "Con2Vec: Learning embedding representations for contrast sets," *Knowledge-Based Systems*, vol. 229, Art. no. 107382, 2021. | ✅ Crossref: 10/2021, doi 10.1016/j.knosys.2021.107382; tác giả: D. Nguyen, W. Luo, B. Vo, L. T. T. Nguyen, W. Pedrycz | ⚪ | Nhúng **contrast set** (mẫu tương phản gắn với biến mục tiêu) để xây vector cho dữ liệu transaction. Là phiên bản "có định hướng nhãn" của mô thức |

## Nhóm 2 — Khai phá tập phổ biến (nền tảng Chương 3)

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Vai trò |
|---|---|---|---|---|
| S05 | R. Agrawal and R. Srikant, "Fast algorithms for mining association rules in large databases," in *Proc. 20th Int. Conf. Very Large Data Bases (VLDB)*, 1994, pp. 487–499. | ✅ [VLDB](https://vldb.org/conf/1994/P487.PDF) | 🔴 | Apriori: định nghĩa support, tính chất anti-monotone |
| S06 | J. Han, J. Pei, and Y. Yin, "Mining frequent patterns without candidate generation," in *Proc. ACM SIGMOD*, 2000, pp. 1–12, doi: 10.1145/342009.335372. | ✅ [Duke](https://courses.cs.duke.edu/spring02/cps296.1/papers/HPY-SIGMOD2000.pdf) | 🔴 | FP-Growth, thuật toán đề xuất dùng trong pipeline (nhanh, không sinh ứng viên) |
| S07 | M. J. Zaki and C.-J. Hsiao, "CHARM: An efficient algorithm for closed itemset mining," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2002, pp. 457–473. | ✅ [DBLP](https://dblp1.uni-trier.de/rec/conf/sdm/ZakiH02.html) | 🔴 | **Closed itemsets**: giải pháp số 1 cho **H2 (bùng nổ FI)** khi transaction là bài báo dài |
| S08 | P. Fournier-Viger, J. C.-W. Lin, B. Vo, T. T. Chi, J. Zhang, and H. B. Le, "A survey of itemset mining," *WIREs Data Mining Knowl. Discov.*, vol. 7, no. 4, e1207, 2017. | ☑️ ref [6] của [13] | 🟠 | Tổng quan: closed, maximal, top-k itemset. Thư viện SPMF dùng cho thực nghiệm |

## Nhóm 3 — Tập phổ biến cho văn bản (khẳng định và giới hạn tính mới của đề tài)

> **Phát hiện:** dùng FI cho văn bản **không mới**. Nó có từ đầu thập niên 2000, kể cả cho tiếng Việt (S12). Điểm mới của Trans2Vec, và của đề tài, là **dùng FI như đơn vị để học embedding**, rồi dùng embedding đó cho **cả tìm kiếm lẫn phân loại**. Phần "khoảng trống nghiên cứu" của survey cần diễn đạt chính xác điều này.

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Vai trò |
|---|---|---|---|---|
| S09 | F. Beil, M. Ester, and X. Xu, "Frequent term-based text clustering," in *Proc. 8th ACM SIGKDD*, 2002, pp. 436–442. | ✅ Crossref: tr. 436–442, doi 10.1145/775047.775110 | 🔴 | Phân cụm văn bản bằng **frequent term sets**, có mô tả cụm dễ hiểu. Tiền thân trực tiếp của ý tưởng "FI = chủ đề" |
| S10 | B. C. M. Fung, K. Wang, and M. Ester, "Hierarchical document clustering using frequent itemsets," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2003, pp. 59–70. | ✅ Crossref: tr. 59–70, doi 10.1137/1.9781611972733.6 | 🟠 | FIHC: **cây chủ đề phân cấp** gán nhãn bằng FI. Gợi ý cho hệ thống: duyệt chuyên mục theo cây (chuyên mục → chuyên mục con, giống Level 1/Level 2 của [1]) |
| S04 | F. Rousseau, E. Kiagias, and M. Vazirgiannis, "Text categorization as a graph classification problem," in *Proc. 53rd ACL & 7th IJCNLP*, 2015, pp. 1702–1712. | ✅ [ACL Anthology P15-1164](https://aclanthology.org/P15-1164/) | 🔴 | Graph-of-words + **khai phá đồ thị con phổ biến** làm đặc trưng ("long-distance n-grams"); k-core để giảm kích thước. **Nguồn của phương pháp elbow chọn δ** mà [13] dùng |
| S11 | B. Wang, R. Qi, J. Gao, J. Zhang, X. Yuan, and W. Ke, "Mining the frequent patterns of named entities for long document classification," *Applied Sciences*, vol. 12, no. 5, 2544, 2022, doi: 10.3390/app12052544. | ✅ (DOI, tác giả) | 🟠 | Văn bản dài nhiều nhiễu nên chỉ khai phá FI trên **thực thể có tên**. **Gợi ý giải H2 cho tin tức:** item = thực thể (người, tổ chức, địa danh) lấy từ NER của VnCoreNLP |
| S12 | P. Do, "Research on application of frequent sets and association rules to semantic Vietnamese document classification," *VNUHCM J. Science and Technology Development*, vol. 9, no. 2, 2006. | ✅ [VJOL](https://vjol.info.vn/JSTD/article/view/28928); trang đầu 23, ◐ trang cuối chưa xác minh | 🔴 | **Tiền lệ tiếng Việt:** FI + luật kết hợp để phân loại văn bản tiếng Việt (tóm tắt bài báo CNTT); dùng cụm danh từ (tách từ + POS) và từ điển đồng nghĩa. Cần trích dẫn để tránh tuyên bố "chưa ai dùng FI cho tiếng Việt" |
| S13 | H. Cheng, X. Yan, J. Han, and C.-W. Hsu, "Discriminative frequent pattern analysis for effective classification," in *Proc. IEEE ICDE*, 2007, pp. 716–725. | ☑️ ref [5] của [13] | 🟠 | Hướng FI **có giám sát** (chọn FI theo information gain) mà [13] phê phán |
| S14 | B. Liu, W. Hsu, and Y. Ma, "Integrating classification and association rule mining," in *Proc. KDD*, 1998, pp. 80–86. | ☑️ ref [1] của [13] | ⚪ | CBA, phân lớp dựa trên luật kết hợp. Mốc lịch sử |

## Nhóm 4 — Học biểu diễn văn bản (nền tảng PV-DBOW)

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Vai trò |
|---|---|---|---|---|
| S15 | Q. Le and T. Mikolov, "Distributed representations of sentences and documents," in *Proc. 31st ICML*, 2014, pp. 1188–1196. | ☑️ ref [10] của [13] | 🔴 | Paragraph Vector (PV-DM, **PV-DBOW**), lõi của Trans2Vec |
| S16 | T. Mikolov, I. Sutskever, K. Chen, G. S. Corrado, and J. Dean, "Distributed representations of words and phrases and their compositionality," in *Proc. NIPS*, 2013, pp. 3111–3119. | ☑️ ref [12] của [13] | 🔴 | Skip-gram, **negative sampling** (Eq. 3 của [13]) |
| S17 | J. H. Lau and T. Baldwin, "An empirical evaluation of doc2vec with practical insights into document embedding generation," in *Proc. 1st Workshop on Representation Learning for NLP*, 2016, pp. 78–86. | ✅ [ACL W16-1609](https://aclanthology.org/W16-1609/) | 🔴 | **Doc2Vec hoạt động tốt khi cấu hình đúng**; khuyến nghị siêu tham số cho PV-DBOW. Dùng để (a) **phản biện [8]**, (b) cấu hình Trans2Vec |

## Nhóm 5 — Dữ liệu Snippets và đối chứng của [13]

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Vai trò |
|---|---|---|---|---|
| S18 | X.-H. Phan, L.-M. Nguyen, and S. Horiguchi, "Learning to classify short and sparse text & web with hidden topics from large-scale data collections," in *Proc. 17th Int. Conf. World Wide Web (WWW)*, 2008, pp. 91–100, doi: 10.1145/1367497.1367510. | ✅ [IW3C2](https://archives.iw3c2.org/www2008/papers/pdf/p91-phanA.pdf) (đã đọc PDF) | 🔴 | **Nguồn gốc bộ Snippets:** 8 lĩnh vực, 10.060 train / 2.280 test, tiếng Anh. LDA học trên Wikipedia (~470.000 tài liệu) làm "chủ đề ẩn", rồi MaxEnt. **Accuracy 65,75% → 82,18%** khi thêm chủ đề ẩn |

> **Phát hiện phản biện mới cho [13] (bổ sung vào H3):** trên **cùng bộ Snippets**, phương pháp của Phan et al. đạt **82,18%**, cao hơn Trans2Vec-JOI (**79,05%**), nhưng [13] **không so sánh** với kết quả này. Hai con số không hoàn toàn cùng điều kiện: Phan dùng dữ liệu ngoài (Wikipedia) và bộ phân loại MaxEnt; [13] chỉ dùng dữ liệu trong bộ và SVM với C = 1. Dù vậy, điều này cho thấy **tri thức ngoài (topic hoặc pretrained) vẫn hơn embedding chỉ học từ dữ liệu trong bộ**. Đây là lập luận ủng hộ việc **thử khởi tạo hoặc kết hợp Trans2Vec với embedding pretrained** (gợi ý của S17).
> Ghi chú: bài Phan 2008 **chỉ thực nghiệm trên tiếng Anh** (Snippets và tóm tắt y khoa Ohsumed/MEDLINE), không có tiếng Việt.

## Nhóm 6 — Topic model và tìm kiếm ngữ nghĩa (đối chứng hiện đại)

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Vai trò |
|---|---|---|---|---|
| S19 | D. Angelov, "Top2Vec: Distributed representations of topics," arXiv:2008.09470, 2020. | ✅ [arXiv](https://arxiv.org/abs/2008.09470) | 🟠 | Embedding chung tài liệu + từ → chủ đề; có sẵn **tìm kiếm ngữ nghĩa**; tự xác định số chủ đề. Đối chứng gần nhất về chức năng "tìm kiếm + chủ đề" |
| S20 | M. Grootendorst, "BERTopic: Neural topic modeling with a class-based TF-IDF procedure," arXiv:2203.05794, 2022. | ✅ [arXiv](https://arxiv.org/abs/2203.05794) | 🟠 | Topic model dựa trên embedding Transformer + c-TF-IDF; được dùng trong [10] |
| S21 | N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. EMNLP-IJCNLP*, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410. | ✅ [ACL D19-1410](https://aclanthology.org/D19-1410) | 🟠 | Embedding câu cho tìm kiếm bằng cosine, làm baseline tìm kiếm dày |
| S22 | V. Karpukhin *et al.*, "Dense passage retrieval for open-domain question answering," in *Proc. EMNLP*, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550. | ✅ [ACL 2020.emnlp-main.550](https://aclanthology.org/2020.emnlp-main.550) | ⚪ | Khung dense retrieval, cơ sở lý thuyết cho chức năng tìm kiếm |

## Nhóm 7 — Tài nguyên và benchmark tiếng Việt

| Mã | Tài liệu (IEEE) | XM | Ưu tiên | Vai trò |
|---|---|---|---|---|
| S23 | D. Q. Nguyen and A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," in *Findings of EMNLP 2020*, 2020, pp. 1037–1042. | ✅ [ACL 2020.findings-emnlp.92](https://preview.aclanthology.org/author-url/2020.findings-emnlp.92/) | 🔴 | Pretrain trên ~20 GB văn bản gồm Wikipedia + **~19 GB tin tức tiếng Việt**, nên rất hợp miền tin tức. Trần trên đối chứng |
| S24 | T. Vu, D. Q. Nguyen, D. Q. Nguyen, M. Dras, and M. Johnson, "VnCoreNLP: A Vietnamese natural language processing toolkit," in *Proc. NAACL-HLT: Demonstrations*, 2018, pp. 56–60. | ✅ [ACL N18-5012](https://aclanthology.org/N18-5012/) | 🔴 | Tách từ, POS, **NER** (phục vụ S11), dùng trong pipeline |
| S25 | VNTC — Vietnamese News Text Classification corpus, GitHub: duyvuleo/VNTC (corpus của [1]). | ✅ (qua mô tả trên Hugging Face) | 🔴 | **Kiểm tra chéo:** 84.132 bài = 33.759 + 50.373, **khớp đúng Level 1 của [1]**. Một bản chia lại cố định do cộng đồng tạo: 67.305 / 8.413 / 8.414 (train / dev / test). Dataset công khai, nên là **benchmark chính** |
| S26 | L. Pham, T. Luu, T. Vo, M. Nguyen, and V. Hoang, "VN-MTEB: Vietnamese massive text embedding benchmark," in *Findings of EACL 2026*, 2026 (arXiv:2507.21500). | ✅ [arXiv](https://arxiv.org/abs/2507.21500) | 🟠 | 41 dataset, 6 tác vụ (**retrieval, clustering, classification**, …) cho embedding tiếng Việt. Dùng để chọn embedding tiếng Việt mạnh làm baseline tìm kiếm. ⚠️ Dữ liệu được dịch máy từ MTEB tiếng Anh |
| S27 | VLUE (arXiv:2403.15882, 2024), SMTCE (arXiv:2209.10482, 2022), CafeBERT (Findings NAACL 2024) | ⚠️ mới xác minh ở mức tiêu đề | ⚪ | Bối cảnh benchmark NLU tiếng Việt hiện đại; nhắc ngắn trong Chương 7 |

---

## Tác động lên kế hoạch và survey

1. **Taxonomy nhánh E** mở rộng thành **"mô thức pattern-based embedding"**: E1 FI làm đặc trưng ([13] baseline, S09, S10, S12) → E2 FI làm đơn vị embedding ([13], S01, S02, S03).
2. **Phát biểu khoảng trống nghiên cứu (chính xác hơn):** đã có FI cho văn bản tiếng Việt (S12, 2006), nhưng **chưa có embedding dựa trên mẫu phổ biến cho văn bản/tin tức tiếng Việt**, và **chưa ai dùng nó cho tìm kiếm**.
3. **Hướng giải hạn chế của [13], nay có tài liệu làm cơ sở:**
   - **H1 (mất thứ tự):** dùng Sqn2Vec (S01).
   - **H2 (bùng nổ FI):** closed itemsets (S07), item = thực thể có tên (S11), top-k từ khóa ([3], [5]), k-core (S04).
   - **H3 (baseline yếu):** đối chứng Phan 2008 (S18), Top2Vec (S19), PhoBERT (S23).
4. **Benchmark chính được xác nhận là VNTC (S25):** công khai và khớp với [1], nên so sánh được với [1] và [3].
5. **Chức năng tìm kiếm:** đánh giá theo cách của VN-MTEB (S26, retrieval/clustering), với baseline dày là SBERT hoặc PhoBERT (S21, S23).

## Đề xuất lấp số [11], [12] (anh/chị quyết định)

Nếu muốn tải PDF về `sources/papers/` để đọc kỹ như 11 bài kia, hai ứng viên đáng nhất:
- **[11] = S01 Sqn2Vec (2018).** Cùng tác giả, giải hạn chế lớn nhất H1, mở rộng tự nhiên cho văn bản.
- **[12] = S04 Rousseau et al. (ACL 2015).** Khai phá mẫu cho phân loại văn bản ở hội nghị NLP hàng đầu, và là nguồn của phương pháp elbow.

Các phương án thay thế: S18 Phan 2008 (đã đọc trong phiên này), S12 Đỗ Phúc 2006 (tiền lệ tiếng Việt).
