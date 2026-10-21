# [K29] LLMEmbed: Rethinking Lightweight LLM's Genuine Function in Text Classification

> **Vai trò:** R3 – Đối chứng hiện đại có **cùng hình dạng đường ống** với Trans2Vec (embedding không fine-tune + bộ phân loại nhẹ), cho cả bước (4) và (5a/5b) · Taxonomy **F2** (mới) · Chương 4, 5.4, 6, 9 · Liên quan ★★★★

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | C. Liu, H. Zhang, K. Zhao, X. Ju, and L. Yang, "LLMEmbed: Rethinking lightweight LLM's genuine function in text classification," in *Proc. 62nd Annu. Meeting Assoc. Comput. Linguistics (ACL) (Volume 1: Long Papers)*, Bangkok, Thailand, Aug. 2024, pp. 7994–8004. *(DOI ACL Anthology cần tra ở GĐ11.)* |
| Đơn vị | Systems Engineering Institute, AMS, Bắc Kinh; State Key Lab of Mathematical Engineering and Advanced Computing |
| Mã nguồn | github.com/ChunLiu-cs/LLMEmbed-ACL2024 |
| File | `sources/papers/Paper_KDD_Data/29.pdf` |

## 2. Bài toán và động lực
- Phân loại văn bản bằng **prompt** (ICL, CoT, CARP) tốt với LLM rất lớn (GPT-3 175B), nhưng **kém và rất tốn kém** với LLM nhẹ có thể triển khai cục bộ (LLaMA2-7B). Chúng còn chạy tuần tự và dễ ảo giác.
- **Đề xuất:** không dùng khả năng *sinh* của LLM mà dùng **biểu diễn tiềm ẩn** của nó làm đặc trưng cho một bộ phân loại nhẹ, theo kiểu học chuyển giao cổ điển.

## 3. Phương pháp
1. **Trích embedding (đóng băng mọi backbone):**
   - LLaMA2-7B: lấy **trung bình token** ở mỗi tầng trong **5 tầng cuối** (tầng 28–32);
   - BERT, RoBERTa: lấy embedding câu.
2. **Hợp nhất:**
   - Avg / Max pooling giữa các tầng của LLaMA2;
   - Cat: ghép với BERT/RoBERTa;
   - **Co-occurrence pooling**: tích ngoài $\phi\phi^T$, sau đó chuẩn hóa lũy thừa $PN(X;\sigma)=\frac{1-e^{-\sigma X}}{1+e^{-\sigma X}}$ với $\sigma \in [0{,}1;0{,}5]$, để nắm **tương tác bậc hai** giữa các chiều.
3. **Bộ phân loại:** đầu phân loại nhẹ, cross-entropy, batch 1024, lr 1e-4, hội tụ sau khoảng 50 epoch. **Chỉ huấn luyện đầu phân loại.**
4. **Giao thức:** theo CARP; 5 benchmark; GPU A100-40G.

## 4. Dữ liệu và kết quả
| Phương pháp | SST-2 | MR | **AGNews** | R8 | R52 | TB |
|---|---|---|---|---|---|---|
| BERT-large (đóng băng) | 0,876 | 0,813 | 0,822 | 0,825 | 0,658 | 0,799 |
| RoBERTa-large (đóng băng) | 0,903 | 0,935 | 0,944 | 0,968 | **0,422** | 0,834 |
| CARP + LLaMA2-7B | 0,884 | 0,839 | 0,852 | 0,751 | 0,731 | 0,811 |
| CARP + GPT-3 175B | 0,957 | 0,907 | 0,953 | 0,978 | 0,963 | 0,952 |
| **LLMEmbed** (Cat + Co + Avg + Cat, 3 backbone) | 0,958 | 0,955 | **0,958** | 0,982 | 0,957 | **0,962** |

- Chỉ dùng **Avg** trên LLaMA2 đã đạt 0,959. Ghép thêm BERT/RoBERTa và co-occurrence pooling chỉ thêm khoảng +0,3 điểm.
- **Chi phí** (so với CARP): thời gian khoảng 1,5% (1 giờ 41 phút so với 115 giờ 36 phút trung bình); điện năng 0,38 kWh so với 20,93 kWh; chi phí $0,025 so với $199 (token GPT-3).
- Tác giả tự nêu hạn chế: (1) **yếu với văn bản dài** nếu không fine-tune; (2) khả năng diễn giải kém hơn prompt.

## 5. Hạn chế và phản biện
- **Baseline có vấn đề:** RoBERTa-large đạt 0,4217 trên R52, **đúng bằng tỉ lệ lớp lớn nhất** (*earn*: 1.083/2.568 bài test = 42,17%). Mô hình đoán toàn bộ là một lớp, tức đầu phân loại không hội tụ. Biến thể "Cat" của LLMEmbed cũng rơi đúng về 0,4217 (Bảng 2). So sánh với PLM vì vậy kém tin cậy.
- So sánh chính là với **prompt-based**, một đối thủ yếu và đắt. Thiếu đối chứng **fine-tune** PLM và **sentence encoder chuyên dụng** (SimCSE, E5, BGE), vốn mới là đối thủ tự nhiên của "embedding + bộ phân loại".
- Không báo độ lệch chuẩn hay kiểm định. Chỉ dùng Accuracy. Chỉ thử tiếng Anh.
- Cần GPU (trích embedding 7B). Thời gian trích trên MR (văn bản dài) chiếm phần lớn chi phí, nên **văn bản dài là điểm nghẽn cả về chất lượng lẫn chi phí**.

## 6. Liên hệ với đề tài / Trans2Vec
- **Đối chứng có cùng hình dạng pipeline:** embedding không giám sát hoặc đóng băng, rồi bộ phân loại tuyến tính/nhẹ, đúng như Trans2Vec + SVM/LR. So sánh này công bằng về mặt *mô thức* hơn so với PhoBERT fine-tune ([10]).
- **Tương tác bậc cao: ký hiệu và tiềm ẩn.** FI trong Trans2Vec là đồng xuất hiện bậc cao **giữa các từ, đếm tường minh, đọc được**. Co-occurrence pooling là tương tác bậc hai **giữa các chiều tiềm ẩn, không đọc được**. Cả hai cùng xuất phát từ quan sát "tương tác bậc cao bổ sung cho biểu diễn bậc một". Đây là trục so sánh khái niệm mới cho Mục 5.4 của survey (họ "mẫu + embedding").
- **Cho bước (5b) tìm kiếm:** một embedding dùng chung cho phân loại và truy hồi. Bản khả thi trên CPU cho tiếng Việt là sentence encoder đóng băng (BGE-M3, multilingual-e5, SimCSE-PhoBERT; xem `candidates.md`). Đây là cơ sở cho **E10**.
- **Chi phí (RQ4):** đặt cạnh số liệu của Trans2Vec trên CPU (FIM 3 s, huấn luyện JOI 16 s, suy luận 50.373 bài 42 s). Đánh đổi là "rẻ, giải thích được, độ chính xác thấp hơn" so với "đắt, khó giải thích, độ chính xác cao".
- **Cảnh báo chuyển giao:** tin tức tiếng Việt dài (hàng trăm từ), đúng điểm yếu tác giả tự nhận. Không thể giả định mức 0,96 chuyển sang VNTC.

## 7. Ý dùng trong survey
- **Chương 4 (nhánh F2):** mô thức "LLM như bộ trích đặc trưng".
- **Chương 5.4:** đối chiếu FI và co-occurrence pooling.
- **Chương 6:** bảng chi phí (thời gian, kWh, $).
- **Chương 9:** baseline trần trên dạng đóng băng (E10); lập luận vì sao Trans2Vec vẫn có chỗ đứng (CPU, giải thích được, văn bản dài).
