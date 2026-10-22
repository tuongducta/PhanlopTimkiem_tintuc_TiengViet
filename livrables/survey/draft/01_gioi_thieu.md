## 1. Giới thiệu

### 1.1 Bối cảnh

Báo điện tử là một trong những nguồn văn bản tiếng Việt lớn và tăng nhanh nhất. Mỗi ngày, hàng chục trang tin như VnExpress, Tuổi Trẻ, Thanh Niên, Dân trí xuất bản hàng nghìn bài, và mỗi bài được biên tập viên xếp vào một chuyên mục: Thời sự, Kinh doanh, Thể thao, Sức khỏe, v.v. Hai nhu cầu xử lý cơ bản nảy sinh từ khối dữ liệu này:
- **Phân loại chuyên mục tự động:** gán chuyên mục cho bài mới, cho bài từ nguồn chưa được phân loại, hoặc thống nhất hệ thống chuyên mục khác nhau giữa các trang.
- **Tìm kiếm:** truy xuất những bài *liên quan về nội dung* tới một truy vấn hay một bài đang đọc, vượt ra ngoài việc khớp từ khóa chính xác.

Về hình thức, phân loại văn bản là bài toán học một ánh xạ từ tập tài liệu vào tập chuyên mục định trước [@sebastiani2002; @duong2019]. Chất lượng của mọi bộ phân loại, cũng như mọi hệ thống tìm kiếm dựa trên độ tương đồng, phụ thuộc trước hết vào **cách biểu diễn văn bản thành vector**. Với tiếng Việt, câu hỏi biểu diễn càng khó hơn: ranh giới từ không trùng với khoảng trắng, và phần lớn từ có nghĩa được ghép từ hai âm tiết trở lên [@hoang2007; @nguyen2009].

### 1.2 Động lực: điểm giao giữa khai phá mẫu và học biểu diễn

Nghiên cứu phân loại văn bản tiếng Việt đã trải qua ba thế hệ biểu diễn:
1. **Biểu diễn thưa và chọn đặc trưng:** túi từ và TF-IDF [@duong2019], n-gram âm tiết, các tiêu chí chọn đặc trưng như Information Gain, χ² hay OCFS [@hoang2007; @nguyen2009], và các phương pháp trích từ khóa [@van2017; @huynh2020].
2. **Biểu diễn dày học từ dữ liệu:** mạng nơ-ron trích đặc trưng [@vinh2021; @hien2024] và embedding tĩnh Word2Vec, GloVe, Doc2Vec [@huong2022].
3. **Mô hình ngôn ngữ tiền huấn luyện:** họ BERT, đặc biệt PhoBERT [@phobert2020; @pham2020; @luu2024; @nguyen2025].

Ở một nhánh khác, cộng đồng khai phá dữ liệu (KDD) từ lâu đã biểu diễn dữ liệu dạng tập hợp bằng **tập phổ biến** (frequent itemsets): những tổ hợp phần tử cùng xuất hiện với tần suất vượt một ngưỡng [@agrawal1994; @han2000]. Tập phổ biến đã được dùng cho phân cụm và phân loại văn bản [@beil2002; @fung2003; @cheng2007], kể cả văn bản tiếng Việt [@dophuc2006]. Tuy nhiên, cách dùng này gặp hai trở ngại cố hữu: số chiều rất lớn và vector rất thưa.

Năm 2018, Nguyen và cộng sự đề xuất **Trans2Vec** [@trans2vec]: coi mỗi tập phổ biến như một "từ" và học vector cho mỗi transaction bằng mô hình Paragraph Vector [@le2014]. Kết quả là một biểu diễn **dày, ít chiều, không cần nhãn**, nhưng vẫn mang tri thức đồng xuất hiện bậc cao của tập phổ biến. Áp vào văn bản, mỗi bài báo là một transaction và mỗi từ là một item. Khi đó tập phổ biến chính là các cụm từ hay đi cùng nhau, chẳng hạn {chứng_khoán, cổ_phiếu, sàn} cho chuyên mục Kinh doanh. Với tiếng Việt, có thêm một điểm đáng chú ý: nếu item là âm tiết, các tập phổ biến hai phần tử có khả năng tự "khôi phục" từ ghép, ví dụ {chứng, khoán}. Nhờ vậy hệ thống phần nào bớt phụ thuộc vào bộ tách từ.

Dù vậy, cho tới nay chưa có công trình nào đưa hướng tiếp cận này vào văn bản tiếng Việt, và cũng chưa có công trình nào dùng nó cho bài toán tìm kiếm. Hai bài tổng quan lớn gần đây về phân loại văn bản [@li2022; @minaee2021] phủ từ phương pháp truyền thống tới mạng đồ thị và mô hình tiền huấn luyện, nhưng không có nhánh nào cho biểu diễn dựa trên mẫu phổ biến. Bài khảo sát này nhằm lấp khoảng trống đó.

Để bài khảo sát phục vụ trực tiếp việc xây hệ thống, các chương được tổ chức theo **đường ống xử lý** của một hệ thống tìm kiếm và phân loại tin tức (Hình 1.1). Mỗi bước ứng với một câu hỏi thiết kế, và mỗi tài liệu được đặt vào bước mà nó đóng góp.

```
Tin tức thô → (1) Tiền xử lý tiếng Việt → (2) Văn bản → transaction → (3) Khai phá FI → (4) Học embedding
                                                                                            │
                                     ┌──────────────────────────────────────────────────────┤
                                     ▼                                                      ▼
                         (5a) Phân loại chuyên mục                          (5b) Tìm kiếm (truy vấn → top-k)
                                     └───────────► (6) Dữ liệu và giao thức đánh giá ◄──────┘
```
*Hình 1.1. Đường ống hệ thống và các bước được khảo sát.*

### 1.3 Câu hỏi nghiên cứu

Bài khảo sát được tổ chức quanh sáu câu hỏi nghiên cứu (RQ). Mỗi câu gắn với một bước của Hình 1.1:

| RQ | Câu hỏi | Bước | Chương |
|---|---|---|---|
| **RQ1** | Tiếng Việt đặt ra những thách thức tiền xử lý nào (tách từ, dấu thanh, bảng mã, từ dừng), và tầm quan trọng của chúng thay đổi thế nào theo từng họ biểu diễn? | (1) | 2 |
| **RQ2** | Các họ biểu diễn văn bản (thưa, chọn đặc trưng, dày có giám sát, embedding, mẫu phổ biến, mô hình tiền huấn luyện, đồ thị) so sánh với nhau ra sao trên tiếng Việt? | (4) | 4, 8 |
| **RQ3** | Tri thức đồng xuất hiện dưới dạng tập phổ biến có làm giàu được embedding tài liệu không, nên khai phá loại FI nào, và Trans2Vec cần điều chỉnh gì để áp dụng cho tin tức tiếng Việt? | (2)–(4) | 3, 5, 9 |
| **RQ4** | Bộ phân loại nào phù hợp với từng loại biểu diễn, và chi phí tính toán đổi lại được gì? | (5a) | 6 |
| **RQ5** | Các tập dữ liệu và giao thức đánh giá hiện có có đủ chuẩn để so sánh công bằng giữa các nghiên cứu không? | (6) | 7, 8 |
| **RQ6** | Biểu diễn nào phục vụ được *đồng thời* phân loại và tìm kiếm, và nên đánh giá phần tìm kiếm thế nào cho đúng? | (5b) | 3, 9 |

### 1.4 Phương pháp khảo sát

Tài liệu được thu thập theo hai vòng:
- **Vòng 1:** 11 công trình nòng cốt do người thực hiện tuyển chọn. Gồm 10 nghiên cứu phân loại văn bản tiếng Việt giai đoạn 2007–2025 và bài gốc Trans2Vec. Mỗi công trình được đọc toàn văn và lập phiếu đọc theo mẫu thống nhất: bài toán, phương pháp, dữ liệu, kết quả, hạn chế, liên hệ với Trans2Vec.
- **Vòng 2:** 27 tài liệu bổ sung, tìm theo bốn hướng:
  - các công trình cùng mô thức với Trans2Vec;
  - nền tảng khai phá tập phổ biến;
  - tập phổ biến cho văn bản;
  - tài nguyên và benchmark tiếng Việt.

  Mọi tài liệu bổ sung đều được xác minh thông tin thư mục qua nguồn chính thức (ACL Anthology, DBLP, kho của nhà xuất bản hoặc của trường).
- **Vòng 3:** 8 công trình (2013–2025) chọn để lấp những bước còn mỏng của đường ống:
  - hai bài về khai phá tập phổ biến, cho bước (3) [@zhang2025; @trasierras2024];
  - hai bài về văn bản tiếng Việt, cho bước (1) và (5a) [@le2013vnlp; @hien2024];
  - hai hướng hiện đại cạnh tranh với Trans2Vec: embedding từ mô hình ngôn ngữ lớn đóng băng [@liu2024] và mạng đồ thị [@onan2023];
  - hai bài tổng quan lớn về phân loại văn bản [@li2022; @minaee2021].

  Thông tin thư mục của cả 8 bài được xác minh qua Crossref. Hai bài tổng quan chỉ dùng làm **khung tham chiếu** (khung phân loại, danh mục dataset, độ đo, danh sách thách thức). Chúng không được dùng làm bằng chứng kết quả, vì số liệu trong đó được chép từ các bài gốc với giao thức khác nhau.

Ba tài liệu kỹ thuật về tìm kiếm (BM25, chỉ mục HNSW, Reciprocal Rank Fusion) [@robertson2009; @malkov2020; @cormack2009] được dùng thêm cho phần hệ thống; chúng không tính vào các vòng trên.

Song song với khảo sát, đề tài hiện thực hệ thống trên MariaDB và Manticore Search và chạy thực nghiệm có kiểm soát trên VNTC-10. Các phép đo này được dùng làm bằng chứng bổ sung, chủ yếu cho bước (5b) và (6), nơi tài liệu sơ cấp còn ít nhất.

Kết quả được tổng hợp vào các ma trận đối chiếu (đường ống × tài liệu, khung phân loại × tài liệu, dataset, kết quả theo nhóm so sánh được, tiền xử lý × biểu diễn). Các ma trận này là xương sống của các Chương 4–8. Ba công trình về phát hiện ngôn từ thù ghét và phân tích cảm xúc [@pham2020; @huong2022; @luu2024] nằm ngoài miền tin tức. Chúng được giữ lại vì chứa bằng chứng về biểu diễn và tiền xử lý tiếng Việt có thể chuyển giao, nhưng không đưa vào so sánh trực tiếp với kết quả trên tin tức.

### 1.5 Đóng góp

Bài khảo sát có ba đóng góp:
1. **Hệ thống hóa theo đường ống** các thành phần của một hệ thống tìm kiếm và phân loại tin tức tiếng Việt. Khung phân loại bảy nhánh đặt **mô thức biểu diễn dựa trên mẫu phổ biến** (pattern-based embedding) cạnh các nhánh mà hai bài tổng quan lớn [@li2022; @minaee2021] đã phủ, và cho thấy nhánh này vắng mặt trong cả hai.
2. **Phân tích phản biện có kiểm chứng.** Trans2Vec được phân tích qua tám hạn chế khi áp dụng cho tin tức tiếng Việt. Các hạn chế được kiểm chứng bằng thực nghiệm có kiểm soát giao thức: chạy trên VNTC-10, tái hiện trên chính dữ liệu của bài gốc, và đo sáu mối đe dọa đến tính hợp lệ của đánh giá. Kết quả cho thấy đóng góp của tập phổ biến bị thổi phồng khi giao thức không nhất quán.
3. **Đề xuất và hiện thực** một kiến trúc dùng chung biểu diễn cho phân loại và tìm kiếm, với ba chế độ tìm kiếm (từ khóa, vector, kết hợp) và cách xử lý dấu thanh tiếng Việt, cùng một **giao thức đánh giá chuẩn hóa** khắc phục các vấn đề về tính so sánh được, rò rỉ dữ liệu và khả năng tái lập.

### 1.6 Cấu trúc bài

Các chương đi theo đường ống ở Hình 1.1:
- Chương 2: bước (1), đặc thù tiếng Việt.
- Chương 3: nền tảng cho bước (2)–(4) và (5b): khai phá tập phổ biến, học biểu diễn phân tán, tìm kiếm từ khóa và tìm kiếm vector.
- Chương 4: bước (4), tiến hóa của biểu diễn văn bản.
- Chương 5: bước (2)–(4), phân tích sâu Trans2Vec và họ phương pháp của nó.
- Chương 6: bước (5a), bộ phân loại và chi phí.
- Chương 7: bước (6), dữ liệu và giao thức đánh giá.
- Chương 8: so sánh tổng hợp, các mâu thuẫn và các mối đe dọa đến tính hợp lệ.
- Chương 9: hệ thống đề xuất, phần hiện thực và kết quả thực nghiệm, gồm bước (5b).
- Chương 10: kết luận.
