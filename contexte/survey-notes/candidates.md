# Ứng viên tài liệu bổ sung (tìm ngày 08/10/2026)

Mức xác minh: ✅ đã xác minh qua Crossref / DOI · ◐ có nguồn nhưng chưa đọc toàn văn.
Ưu tiên: 🔴 nên đọc ngay · 🟠 nên có · ⚪ tham khảo.

## A. Gần đề tài nhất (nên tải PDF vào `sources/papers/`)

| Ưu tiên | Tài liệu | XM | Vì sao liên quan |
|---|---|---|---|
| 🔴 | **Mã nguồn chính thức Trans2Vec**: github.com/nphdang/Trans2Vec (`codes/trans2vec_joi_classify.py`, `trans2vec_ind_classify.py`, `FIM_Trans.exe`) | ✅ | Xem Mục C bên dưới |
| 🔴 | B. N. Chau, D. Duong, P. Tran, "A large-scale Vietnamese news dataset for text classification: Construction and evaluation," *IEEE Access*, vol. 14, pp. 109797–109808, 2026, doi: 10.1109/ACCESS.2026.3711994 | ✅ (chưa đọc tóm tắt) | Bộ dữ liệu tin tức tiếng Việt lớn, rất mới; ứng viên làm "corpus khó" cho thực nghiệm. Tác giả đầu (Bao Nhan Chau) nhiều khả năng là người đã đăng các mô hình VNTC-10 / UIT-ViON và bản chia lại 67.305 / 8.413 / 8.414 trên Hugging Face |
| 🔴 | X.-Y. Chen, Y. Chen, L. Wang, Y.-F. Hu, "Text categorization based on frequent patterns with term frequency," in *Proc. ICMLC*, 2004, pp. 1610–1615, doi: 10.1109/ICMLC.2004.1382032 | ✅ | **Kết hợp tập phổ biến với tần suất từ**, đúng hạn chế H1 mà thực nghiệm chỉ ra (Trans2Vec bỏ tần suất nên thua TF-IDF) |
| 🟠 | K. Q. Tran, P. N. Trinh, K. N.-A. Tran, A. T.-H. Le, L. V. Ha, K. V. Nguyen, "An empirical investigation of online news classification on an open-domain, large-scale and high-quality dataset in Vietnamese," *Frontiers in Artificial Intelligence and Applications*, 2021, doi: 10.3233/FAIA210036 | ✅ | Bộ **UIT-ViON**: 260.000 tiêu đề tin, 13 nhãn, chia cố định 208k / 26k / 26k, công khai (github.com/kh4nh12/UIT-ViON-Dataset). Hợp để thử Trans2Vec trên **văn bản ngắn** (giống điều kiện Snippets của [13]) |
| 🟠 | P.-V. Nguyen, M.-N. Tran, L. Nguyen, D. Dinh, "Advancing Vietnamese information retrieval with learning objective and benchmark," PACLIC 38, 2024 (arXiv:2503.07470) | ◐ | Benchmark **truy hồi** tiếng Việt và so sánh các mô hình embedding: cơ sở cho chức năng tìm kiếm (M7) |
| 🟠 | T. Do, D. Nguyen, "A computational semantic information retrieval model for Vietnamese texts," *Int. J. Computational Science and Engineering*, 2021, p. 301, doi: 10.1504/IJCSE.2021.115657 | ✅ | Mô hình truy hồi ngữ nghĩa cho văn bản tiếng Việt (đồ thị phụ thuộc ngữ nghĩa); đối chứng về hướng tiếp cận tìm kiếm |

## B. Tham khảo thêm

| Ưu tiên | Tài liệu | XM | Ghi chú |
|---|---|---|---|
| ⚪ | F. Dsouza, Ananthanarayana V.S., "Document classification with a weighted frequency pattern tree algorithm," *SAPIENCE*, 2016, pp. 29–34, doi: 10.1109/SAPIENCE.2016.7684140 | ✅ | FP-tree có trọng số cho phân loại văn bản, cũng hướng giữ tần suất |
| ⚪ | Mô hình embedding câu tiếng Việt: `sup-SimCSE-VietNamese-phobert-base`, `vietnamese-sbert`, `AITeamVN/Vietnamese_Embedding` (BGE-M3) trên Hugging Face | ◐ | Baseline dày mạnh cho tìm kiếm (thay PhoBERT fine-tune khi không có GPU, vì chỉ cần suy luận) |
| ⚪ | Bộ "Vietnamese NewsCategory" (VnExpress, khoảng 596.524 bài, có tiêu đề / sapo / nội dung / nhãn) | ◐ | Mới thấy qua kết quả tìm kiếm, chưa xác định nguồn công bố |

## C. Phát hiện từ mã nguồn chính thức của Trans2Vec (đã clone vào `sources/repos/Trans2Vec`)
- Doc2Vec PV-DBOW học **transductive** trên toàn bộ dữ liệu (train + test, không dùng nhãn); vector lấy từ `docvecs`, không có `infer_vector`.
- Mặc định **chia cố định** (`use_train = "fix"`: các dòng đầu làm train). Chia ngẫu nhiên 90/10 chỉ là tùy chọn `"cv"`. Lỗi `if/else` khiến Snippets dùng 80% (9.872) thay cho 10.060.
- `iter = 50` epoch (bài báo không nêu); có tùy chọn GridSearch C (bài báo ghi C = 1 cố định); FI khai phá bằng `FIM_Trans.exe` (Windows, .NET 4.0); dùng gensim 3.4.
- **E7 đã chạy** (`src/experiments/replicate_snippets.py`, xem `contexte/results/RESULTS.md` Mục 2.5):
  - TRANS-IT tái hiện 75,29% (bài báo 75,23%);
  - JOI chỉ đạt 75,99% (bài báo 79,05%);
  - đóng góp của FI là +0,7 điểm, không phải +3,8.
  
  Đã đưa vào survey Mục 9.5 (Bảng 9.6).

## D. Từ khóa tìm kiếm gợi ý (Google Scholar / Semantic Scholar)
- `"frequent itemset" OR "frequent pattern" "document embedding"` · `"pattern-based" "paragraph vector"`
- Bài trích dẫn Trans2Vec / Sqn2Vec: mục "Cited by" trên Google Scholar
- `"Vietnamese" "news" "text classification" dataset 2024..2026` · `"Vietnamese" "semantic search" OR "dense retrieval"`
- `"term frequency" "frequent patterns" text categorization` (hướng giải H1)
- `"transductive" "doc2vec" evaluation` (giao thức đánh giá embedding không giám sát)
