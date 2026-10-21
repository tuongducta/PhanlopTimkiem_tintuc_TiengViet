## 1. Giới thiệu

### 1.1 Bối cảnh

Báo điện tử là một trong những nguồn văn bản tiếng Việt lớn và tăng nhanh nhất. Mỗi ngày, hàng chục trang tin như VnExpress, Tuổi Trẻ, Thanh Niên, Dân trí xuất bản hàng nghìn bài, và mỗi bài được biên tập viên xếp vào một chuyên mục: Thời sự, Kinh doanh, Thể thao, Sức khỏe, v.v. Hai nhu cầu xử lý cơ bản nảy sinh từ khối dữ liệu này:
- **Phân loại chuyên mục tự động:** gán chuyên mục cho bài mới, cho bài từ nguồn chưa được phân loại, hoặc thống nhất hệ thống chuyên mục khác nhau giữa các trang.
- **Tìm kiếm:** truy xuất những bài *liên quan về nội dung* tới một truy vấn hay một bài đang đọc, vượt ra ngoài việc khớp từ khóa chính xác.

Về hình thức, phân loại văn bản là bài toán học một ánh xạ từ tập tài liệu vào tập chuyên mục định trước [@sebastiani2002; @duong2019]. Chất lượng của mọi bộ phân loại, cũng như mọi hệ thống tìm kiếm dựa trên độ tương đồng, phụ thuộc trước hết vào **cách biểu diễn văn bản thành vector**. Với tiếng Việt, câu hỏi biểu diễn càng khó hơn: ranh giới từ không trùng với khoảng trắng, và phần lớn từ có nghĩa được ghép từ hai âm tiết trở lên [@hoang2007; @nguyen2009].

### 1.2 Động lực: điểm giao giữa khai phá mẫu và học biểu diễn

Nghiên cứu phân loại văn bản tiếng Việt đã trải qua ba thế hệ biểu diễn:
1. **Biểu diễn thưa và chọn đặc trưng:** túi từ và TF-IDF [@duong2019], n-gram âm tiết, các tiêu chí chọn đặc trưng như Information Gain, χ² hay OCFS [@hoang2007; @nguyen2009], và các phương pháp trích từ khóa [@van2017; @huynh2020].
2. **Biểu diễn dày học từ dữ liệu:** mạng nơ-ron trích đặc trưng [@vinh2021] và embedding tĩnh Word2Vec, GloVe, Doc2Vec [@huong2022].
3. **Mô hình ngôn ngữ tiền huấn luyện:** họ BERT, đặc biệt PhoBERT [@phobert2020; @pham2020; @luu2024; @nguyen2025].

Ở một nhánh khác, cộng đồng khai phá dữ liệu (KDD) từ lâu đã biểu diễn dữ liệu dạng tập hợp bằng **tập phổ biến** (frequent itemsets): những tổ hợp phần tử cùng xuất hiện với tần suất vượt một ngưỡng [@agrawal1994; @han2000]. Tập phổ biến đã được dùng cho phân cụm và phân loại văn bản [@beil2002; @fung2003; @cheng2007], kể cả văn bản tiếng Việt [@dophuc2006]. Tuy nhiên, cách dùng này gặp hai trở ngại cố hữu: số chiều rất lớn và vector rất thưa.

Năm 2018, Nguyen và cộng sự đề xuất **Trans2Vec** [@trans2vec]: coi mỗi tập phổ biến như một "từ" và học vector cho mỗi transaction bằng mô hình Paragraph Vector [@le2014]. Kết quả là một biểu diễn **dày, ít chiều, không cần nhãn**, nhưng vẫn mang tri thức đồng xuất hiện bậc cao của tập phổ biến. Áp vào văn bản, mỗi bài báo là một transaction và mỗi từ là một item. Khi đó tập phổ biến chính là các cụm từ hay đi cùng nhau, chẳng hạn {chứng_khoán, cổ_phiếu, sàn} cho chuyên mục Kinh doanh. Với tiếng Việt, có thêm một điểm đáng chú ý: nếu item là âm tiết, các tập phổ biến hai phần tử có khả năng tự "khôi phục" từ ghép, ví dụ {chứng, khoán}. Nhờ vậy hệ thống phần nào bớt phụ thuộc vào bộ tách từ.

Dù vậy, cho tới nay chưa có công trình nào đưa hướng tiếp cận này vào văn bản tiếng Việt, và cũng chưa có công trình nào dùng nó cho bài toán tìm kiếm. Bài khảo sát này nhằm lấp khoảng trống đó ở mức tổng quan và đề xuất.

### 1.3 Câu hỏi nghiên cứu

Bài khảo sát được tổ chức quanh năm câu hỏi nghiên cứu (RQ):

| RQ | Câu hỏi |
|---|---|
| **RQ1** | Tiếng Việt đặt ra những thách thức tiền xử lý nào (tách từ, dấu thanh, bảng mã, từ dừng), và tầm quan trọng của chúng thay đổi thế nào theo từng họ biểu diễn? |
| **RQ2** | Các họ biểu diễn văn bản (thưa, chọn đặc trưng, từ khóa, dày có giám sát, embedding tĩnh, Transformer) so sánh với nhau ra sao trên tiếng Việt? |
| **RQ3** | Tri thức đồng xuất hiện dưới dạng tập phổ biến có làm giàu được embedding tài liệu không, và Trans2Vec cần điều chỉnh gì để áp dụng cho tin tức tiếng Việt? |
| **RQ4** | Bộ phân loại nào phù hợp với từng loại biểu diễn, và chi phí tính toán đổi lại được gì? |
| **RQ5** | Các tập dữ liệu và giao thức đánh giá hiện có có đủ chuẩn để so sánh công bằng giữa các nghiên cứu không? |

### 1.4 Phương pháp khảo sát

Tài liệu được thu thập theo hai vòng:
- **Vòng 1:** 11 công trình nòng cốt do người thực hiện tuyển chọn. Gồm 10 nghiên cứu phân loại văn bản tiếng Việt giai đoạn 2007–2025 và bài gốc Trans2Vec. Mỗi công trình được đọc toàn văn và lập phiếu đọc theo mẫu thống nhất: bài toán, phương pháp, dữ liệu, kết quả, hạn chế, liên hệ với Trans2Vec.
- **Vòng 2:** 27 tài liệu bổ sung, tìm theo bốn hướng:
  - các công trình cùng mô thức với Trans2Vec;
  - nền tảng khai phá tập phổ biến;
  - tập phổ biến cho văn bản;
  - tài nguyên và benchmark tiếng Việt.

  Mọi tài liệu bổ sung đều được xác minh thông tin thư mục qua nguồn chính thức (ACL Anthology, DBLP, kho của nhà xuất bản hoặc của trường).

Kết quả được tổng hợp vào các ma trận đối chiếu (khung phân loại × tài liệu, dataset, kết quả theo nhóm so sánh được, tiền xử lý × biểu diễn). Các ma trận này là xương sống của các Chương 4–8. Ba công trình về phát hiện ngôn từ thù ghét và phân tích cảm xúc [@pham2020; @huong2022; @luu2024] nằm ngoài miền tin tức. Chúng được giữ lại vì chứa bằng chứng về biểu diễn và tiền xử lý tiếng Việt có thể chuyển giao, nhưng không đưa vào so sánh trực tiếp với kết quả trên tin tức.

### 1.5 Đóng góp

Bài khảo sát có ba đóng góp:
1. **Hệ thống hóa** các phương pháp biểu diễn văn bản cho phân loại tiếng Việt theo khung sáu nhánh, và lần đầu đặt **mô thức biểu diễn dựa trên mẫu phổ biến** (pattern-based embedding) vào bức tranh đó.
2. **Phân tích phản biện** Trans2Vec qua bảy hạn chế khi áp dụng cho tin tức tiếng Việt. Mỗi hạn chế đi kèm giải pháp có cơ sở tài liệu và cách kiểm chứng.
3. **Đề xuất** kiến trúc hệ thống dùng một biểu diễn chung cho phân loại và tìm kiếm, cùng **giao thức đánh giá chuẩn hóa** khắc phục các vấn đề về tính so sánh được, rò rỉ dữ liệu và khả năng tái lập đã phát hiện trong tài liệu.

### 1.6 Cấu trúc bài

- Chương 2: đặc thù tiếng Việt.
- Chương 3: nền tảng khai phá tập phổ biến và học biểu diễn phân tán.
- Chương 4: tiến hóa của biểu diễn văn bản tiếng Việt.
- Chương 5: phân tích sâu Trans2Vec và họ phương pháp của nó.
- Chương 6: bộ phân loại và chi phí.
- Chương 7: dữ liệu và giao thức đánh giá.
- Chương 8: so sánh tổng hợp và các mâu thuẫn.
- Chương 9: đề xuất hệ thống.
- Chương 10: kết luận.
