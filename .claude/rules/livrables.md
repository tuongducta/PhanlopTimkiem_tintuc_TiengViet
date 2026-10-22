# Quy tắc cho sản phẩm nộp (livrables/)
- Chỉ sửa `draft/*.md`, `draft/refs.tsv`, `figures/` và script build. Không sửa `.md`/`.docx` đã build.
- Trích dẫn dạng `[@key]`. Tài liệu mới phải xác minh qua api.crossref.org trước khi thêm vào `refs.tsv`.
- Báo cáo CSDL: 25–30 trang A4. Sau mỗi lần sửa, chạy `scripts/build-docs.sh` rồi `scripts/count-pages.sh`.
- `livrables/survey/draft/` là nguồn của survey v3 (Q5 chốt 22/10). Sau mỗi lần sửa, build lại và kiểm tra mọi tham chiếu "Mục / Bảng / Hình".
- Văn phong: câu ngắn, tiếng Việt chuẩn; số thập phân dùng dấu phẩy (0,816), hàng nghìn dùng dấu chấm (84.132).
