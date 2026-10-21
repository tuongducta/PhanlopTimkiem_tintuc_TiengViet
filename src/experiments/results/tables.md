# Bảng kết quả (sinh tự động)

## E1 — Phân loại (word, SVM tuyến tính C=1, test 50.373 bài)

| Phương pháp | k | d | Accuracy | Macro-F1 | Số seed |
|---|---|---|---|---|---|
| TF-IDF (toàn văn) | full | 43777 | 0.9228 | 0.9028 | 1 |
| MLP-128 có giám sát [7] | full | 128 | 0.9212 | 0.9025 | 1 |
| TF-IDF (top-k item) | 50 | 43777 | 0.9107 | 0.8887 | 1 |
| BOW (toàn văn) | full | 43777 | 0.8990 | 0.8742 | 1 |
| JOI + TF-IDF (A5) | 50 | 128 | 0.8913 | 0.8671 | 1 |
| LDA-100 | full | 100 | 0.8511 | 0.8272 | 1 |
| FI-BIN | 50 | 3586 | 0.8573 | 0.8243 | 1 |
| FI-SUP | 50 | 3586 | 0.8217 | 0.7884 | 1 |
| TRANS-IT | 50 | 128 | 0.8047 ± 0.0051 | 0.7709 ± 0.0056 | 3 |
| JOI – FI đóng (A3) | 50 | 128 | 0.8080 | 0.7695 | 1 |
| Trans2Vec-IND | 50 | 128 | 0.8031 ± 0.0041 | 0.7674 ± 0.0038 | 3 |
| Trans2Vec-JOI | 50 | 128 | 0.8059 ± 0.0013 | 0.7664 ± 0.0006 | 3 |
| TRANS-FI | 50 | 128 | 0.7917 ± 0.0023 | 0.7573 ± 0.0020 | 3 |
| TF-IDF + χ² (128) | full | 128 | 0.7822 | 0.7541 | 1 |

**Hồi quy logistic (bộ phân loại triển khai):**

| Phương pháp | Accuracy | Macro-F1 |
|---|---|---|
| TF-IDF (toàn văn) | 0.9231 | 0.9065 |
| Trans2Vec-JOI | 0.8431 | 0.8144 |

**Thời gian (trung bình qua seed):**

| Phương pháp | Huấn luyện (s) | Suy luận 50.373 bài (s) |
|---|---|---|
| JOI – FI đóng (A3) | 17.5 | 43.1 |
| TRANS-FI | 13.0 | 20.6 |
| TRANS-IT | 15.5 | 36.2 |
| Trans2Vec-JOI | 16.2 | 42.3 |

## E5z — C tinh chỉnh + chuẩn hóa z-score (lẫn hai yếu tố, chỉ tham khảo)

| Phương pháp | view | k | Bộ phân loại | C | Accuracy | Macro-F1 |
|---|---|---|---|---|---|---|
| TF-IDF (toàn văn) | word | 50 | svm-tuned | 1 | 0.9228 | 0.9028 |
| TF-IDF (toàn văn) | word | 50 | lr-tuned | 10 | 0.9246 | 0.9065 |
| TRANS-IT | word | 50 | svm-tuned | 1 | 0.7879 | 0.7521 |
| TRANS-IT | word | 50 | lr-tuned | 0.1 | 0.7935 | 0.7620 |
| TRANS-FI | word | 50 | svm-tuned | 0.1 | 0.7740 | 0.7386 |
| TRANS-FI | word | 50 | lr-tuned | 0.1 | 0.7824 | 0.7506 |
| Trans2Vec-JOI | word | 50 | svm-tuned | 10 | 0.7810 | 0.7406 |
| Trans2Vec-JOI | word | 50 | lr-tuned | 0.1 | 0.7942 | 0.7611 |
| TRANS-IT | word | 100 | svm-tuned | 1 | 0.8068 | 0.7679 |
| TRANS-IT | word | 100 | lr-tuned | 0.01 | 0.8462 | 0.8171 |
| Trans2Vec-JOI | word | 100 | svm-tuned | 1 | 0.8544 | 0.8242 |
| Trans2Vec-JOI | word | 100 | lr-tuned | 0.1 | 0.8559 | 0.8271 |

## E5 — C tinh chỉnh bằng 3-fold CV trên train (vector train = model.dv)

| Phương pháp | view | k | Bộ phân loại | C | Accuracy | Macro-F1 |
|---|---|---|---|---|---|---|
| TF-IDF (toàn văn) | word | 50 | svm-tuned | 1 | 0.9228 | 0.9028 |
| TF-IDF (toàn văn) | word | 50 | lr-tuned | 10 | 0.9246 | 0.9065 |
| TRANS-IT | word | 50 | svm-tuned | 10 | 0.7884 | 0.7542 |
| TRANS-IT | word | 50 | lr-tuned | 100 | 0.7790 | 0.7482 |
| TRANS-FI | word | 50 | svm-tuned | 10 | 0.7789 | 0.7439 |
| TRANS-FI | word | 50 | lr-tuned | 100 | 0.7679 | 0.7363 |
| Trans2Vec-JOI | word | 50 | svm-tuned | 100 | 0.7816 | 0.7406 |
| Trans2Vec-JOI | word | 50 | lr-tuned | 100 | 0.7749 | 0.7423 |
| TRANS-IT | word | 100 | svm-tuned | 10 | 0.8078 | 0.7686 |
| TRANS-IT | word | 100 | lr-tuned | 10 | 0.8262 | 0.7954 |
| Trans2Vec-JOI | word | 100 | svm-tuned | 10 | 0.8519 | 0.8213 |
| Trans2Vec-JOI | word | 100 | lr-tuned | 10 | 0.8541 | 0.8250 |

## E6 — Vector train suy luận lại bằng infer_vector (nhất quán với test)

| Phương pháp | view | k | Bộ phân loại | C | Accuracy | Macro-F1 |
|---|---|---|---|---|---|---|
| TRANS-IT (train suy luận lại) | word | 50 | svm | 1 | 0.8700 | 0.8412 |
| TRANS-IT (train suy luận lại) | word | 50 | lr | 1 | 0.8740 | 0.8473 |
| TRANS-IT (train suy luận lại) | word | 50 | svm-tuned | 1 | 0.8700 | 0.8412 |
| TRANS-IT (train suy luận lại) | word | 50 | lr-tuned | 10 | 0.8761 | 0.8491 |
| TRANS-FI (train suy luận lại) | word | 50 | svm | 1 | 0.8491 | 0.8198 |
| TRANS-FI (train suy luận lại) | word | 50 | lr | 1 | 0.8539 | 0.8263 |
| TRANS-FI (train suy luận lại) | word | 50 | svm-tuned | 1 | 0.8491 | 0.8198 |
| TRANS-FI (train suy luận lại) | word | 50 | lr-tuned | 1 | 0.8539 | 0.8263 |
| Trans2Vec-JOI (train suy luận lại) | word | 50 | svm | 1 | 0.8708 | 0.8424 |
| Trans2Vec-JOI (train suy luận lại) | word | 50 | lr | 1 | 0.8749 | 0.8487 |
| Trans2Vec-JOI (train suy luận lại) | word | 50 | svm-tuned | 1 | 0.8708 | 0.8424 |
| Trans2Vec-JOI (train suy luận lại) | word | 50 | lr-tuned | 10 | 0.8779 | 0.8519 |
| TRANS-IT (train suy luận lại) | word | 100 | svm | 1 | 0.8676 | 0.8393 |
| TRANS-IT (train suy luận lại) | word | 100 | lr | 1 | 0.8744 | 0.8484 |
| TRANS-IT (train suy luận lại) | word | 100 | svm-tuned | 100 | 0.8678 | 0.8395 |
| TRANS-IT (train suy luận lại) | word | 100 | lr-tuned | 1 | 0.8744 | 0.8484 |
| Trans2Vec-JOI (train suy luận lại) | word | 100 | svm | 1 | 0.8657 | 0.8384 |
| Trans2Vec-JOI (train suy luận lại) | word | 100 | lr | 1 | 0.8704 | 0.8452 |
| Trans2Vec-JOI (train suy luận lại) | word | 100 | svm-tuned | 1 | 0.8657 | 0.8384 |
| Trans2Vec-JOI (train suy luận lại) | word | 100 | lr-tuned | 1 | 0.8704 | 0.8452 |
| TRANS-IT (train suy luận lại) | syl | 50 | svm | 1 | 0.8385 | 0.8091 |
| TRANS-IT (train suy luận lại) | syl | 50 | lr | 1 | 0.8441 | 0.8159 |
| TRANS-IT (train suy luận lại) | syl | 50 | svm-tuned | 1 | 0.8385 | 0.8091 |
| TRANS-IT (train suy luận lại) | syl | 50 | lr-tuned | 1 | 0.8441 | 0.8159 |
| TRANS-FI (train suy luận lại) | syl | 50 | svm | 1 | 0.8339 | 0.8045 |
| TRANS-FI (train suy luận lại) | syl | 50 | lr | 1 | 0.8386 | 0.8113 |
| TRANS-FI (train suy luận lại) | syl | 50 | svm-tuned | 10 | 0.8338 | 0.8042 |
| TRANS-FI (train suy luận lại) | syl | 50 | lr-tuned | 10 | 0.8386 | 0.8104 |
| Trans2Vec-JOI (train suy luận lại) | syl | 50 | svm | 1 | 0.8460 | 0.8180 |
| Trans2Vec-JOI (train suy luận lại) | syl | 50 | lr | 1 | 0.8502 | 0.8244 |
| Trans2Vec-JOI (train suy luận lại) | syl | 50 | svm-tuned | 100 | 0.8460 | 0.8178 |
| Trans2Vec-JOI (train suy luận lại) | syl | 50 | lr-tuned | 1 | 0.8502 | 0.8244 |

## E2 (A1) — Âm tiết, không tách từ

| Phương pháp | view | k | d | Accuracy | Macro-F1 |
|---|---|---|---|---|---|
| TF-IDF (toàn văn) | syl | full | 19963 | 0.9115 | 0.8907 |
| TRANS-IT | syl | 50 | 128 | 0.7807 | 0.7328 |
| TRANS-FI | syl | 50 | 128 | 0.8090 | 0.7742 |
| Trans2Vec-JOI | syl | 50 | 128 | 0.8159 | 0.7745 |

## E3 (A2) — Số item k mỗi bài

| Phương pháp | view | k | d | Accuracy | Macro-F1 | n_fi | mine_s | train_s |
|---|---|---|---|---|---|---|---|---|
| TRANS-IT | word | 20 | 128 | 0.8049 | 0.7660 | 575.0 | 0.8 | 10.0 |
| Trans2Vec-JOI | word | 20 | 128 | 0.7993 | 0.7611 | 575.0 | 0.8 | 10.7 |
| TRANS-IT | word | 100 | 128 | 0.8243 | 0.7860 | 30866.0 | 14.1 | 29.1 |
| Trans2Vec-JOI | word | 100 | 128 | 0.8527 | 0.8225 | 30866.0 | 14.1 | 55.7 |

## E4 (A4) — Số chiều d

| Phương pháp | view | k | d | Accuracy | Macro-F1 |
|---|---|---|---|---|---|
| Trans2Vec-JOI | word | 50 | 64 | 0.8129 | 0.7750 |
| Trans2Vec-JOI | word | 50 | 256 | 0.8020 | 0.7635 |

## Tìm kiếm (1.000 truy vấn phân tầng, kho = 33.759 bài train, liên quan = cùng chủ đề)

| exp | Phương pháp | view | Truy vấn | p@10 | map@100 | ndcg@10 | n_q |
|---|---|---|---|---|---|---|---|
| E1 | TF-IDF (toàn văn) | word | doc | 0.7308 | 0.5654 | 0.7402 |  |
| E1 | MLP-128 có giám sát [7] | word | doc | 0.8887 | 0.8557 | 0.8906 |  |
| E1 | LDA-100 | word | doc | 0.7601 | 0.6027 | 0.7654 |  |
| E1 | TRANS-IT | word | doc | 0.7949 | 0.6713 | 0.8001 |  |
| E1 | TRANS-FI | word | doc | 0.7821 | 0.6508 | 0.7875 |  |
| E1 | Trans2Vec-JOI | word | doc | 0.8049 | 0.6863 | 0.8094 |  |
| E1 | Trans2Vec-IND | word | doc | 0.7952 | 0.6704 | 0.7999 |  |
| E1 | TF-IDF (toàn văn) | word | 3 từ khóa – tất cả | 0.6223 | 0.4202 | 0.6339 | 1000 |
| E1 | Trans2Vec-JOI | word | 3 từ khóa – tất cả | 0.6910 | 0.6021 | 0.6922 | 1000 |
| E1 | TF-IDF (toàn văn) | word | 3 từ khóa – có FI | 0.7946 | 0.6442 | 0.8053 | 56 |
| E1 | Trans2Vec-JOI | word | 3 từ khóa – có FI | 0.8482 | 0.7633 | 0.8516 | 56 |
| E1 | TF-IDF (toàn văn) | word | 3 từ khóa – không FI | 0.6121 | 0.4069 | 0.6237 | 944 |
| E1 | Trans2Vec-JOI | word | 3 từ khóa – không FI | 0.6852 | 0.5955 | 0.6862 | 944 |
| E2 | TF-IDF (toàn văn) | syl | doc | 0.7293 | 0.5556 | 0.7390 |  |
| E2 | TRANS-IT | syl | doc | 0.7729 | 0.6120 | 0.7798 |  |
| E2 | TRANS-FI | syl | doc | 0.7628 | 0.5975 | 0.7675 |  |
| E2 | Trans2Vec-JOI | syl | doc | 0.7798 | 0.6253 | 0.7845 |  |
| E6 | TRANS-IT (train suy luận lại) | word | doc | 0.7989 | 0.6643 | 0.8029 |  |
| E6 | TRANS-FI (train suy luận lại) | word | doc | 0.7700 | 0.6225 | 0.7750 |  |
| E6 | Trans2Vec-JOI (train suy luận lại) | word | doc | 0.8062 | 0.6796 | 0.8117 |  |
| E6 | TRANS-IT (train suy luận lại) | word | doc | 0.7782 | 0.6226 | 0.7854 |  |
| E6 | Trans2Vec-JOI (train suy luận lại) | word | doc | 0.7640 | 0.5773 | 0.7700 |  |
| E6 | TRANS-IT (train suy luận lại) | syl | doc | 0.7471 | 0.5478 | 0.7575 |  |
| E6 | TRANS-FI (train suy luận lại) | syl | doc | 0.7498 | 0.5736 | 0.7565 |  |
| E6 | Trans2Vec-JOI (train suy luận lại) | syl | doc | 0.7712 | 0.6057 | 0.7782 |  |

## Thống kê khai phá tập phổ biến

| cấu hình | vocab | stopwords | delta | n_fi | n_fi_len | mine_s | fi_per_doc_train | docs_without_fi2_test |
|---|---|---|---|---|---|---|---|---|
| syl_k50 | 19963 | 149 | 0.00535 | 8984 | {'1': 1991, '2': 5299, '3': 1694} | 3.8 | 95.7 | 0.6% |
| word_k100 | 43777 | 78 | 0.00535 | 30866 | {'1': 3232, '2': 19976, '3': 7658} | 14.1 | 282.3 | 0.1% |
| word_k20 | 43777 | 78 | 0.00535 | 575 | {'1': 501, '2': 71, '3': 3} | 0.8 | 5.7 | 76.7% |
| word_k50 | 43777 | 78 | 0.00535 | 3586 | {'1': 2102, '2': 1069, '3': 415} | 2.8 | 38.0 | 15.3% |

**FI 2 âm tiết trùng một từ ghép của pyvi:** 713/5299 (13.5%).
