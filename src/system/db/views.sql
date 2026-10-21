-- View phân tích cho tab "Dữ liệu và đánh giá" và báo cáo môn CSDL. Chạy lặp lại được (CREATE OR REPLACE).
-- Áp dụng:  docker exec -i t2v-mariadb mariadb -ut2v -pt2v_pass trans2vec < src/system/db/views.sql

-- Thống kê corpus theo chuyên mục và tập.
CREATE OR REPLACE VIEW v_corpus_stats AS
SELECT c.code, c.name, a.split, COUNT(*) AS n_article,
       ROUND(AVG(a.n_word)) AS avg_words, ROUND(AVG(a.n_syl)) AS avg_syllables
FROM article a JOIN category c ON c.id = a.category_id
GROUP BY c.id, a.split;

-- Item đặc trưng của mỗi chuyên mục: số bài train của chuyên mục có item trong transaction,
-- xếp hạng bằng window function.
CREATE OR REPLACE VIEW v_category_top_item AS
SELECT code, token, n_article, rk FROM (
  SELECT c.code, i.token, COUNT(*) AS n_article,
         ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY COUNT(*) DESC, i.token) AS rk
  FROM article a
  JOIN article_item ai ON ai.article_id = a.id
  JOIN item i          ON i.id = ai.item_id
  JOIN category c      ON c.id = a.category_id
  WHERE a.split = 'train'
  GROUP BY c.id, i.id
) t WHERE rk <= 20;

-- FI đặc trưng của mỗi chuyên mục (cần itemset/article_itemset từ GĐ-H3).
CREATE OR REPLACE VIEW v_category_fi AS
SELECT run_id, code, label, size, n_article, rk FROM (
  SELECT s.run_id, c.code, s.label, s.size, COUNT(*) AS n_article,
         ROW_NUMBER() OVER (PARTITION BY s.run_id, c.id ORDER BY COUNT(*) DESC, s.label) AS rk
  FROM article_itemset ais
  JOIN itemset s  ON s.id = ais.itemset_id
  JOIN article a  ON a.id = ais.article_id
  JOIN category c ON c.id = a.category_id
  WHERE a.split = 'train' AND s.size >= 2
  GROUP BY s.run_id, c.id, s.id
) t WHERE rk <= 20;

-- Ma trận nhầm lẫn trên tập test cho từng lần chạy bộ phân loại.
CREATE OR REPLACE VIEW v_confusion AS
SELECT p.run_id, ct.code AS true_code, cp.code AS pred_code, COUNT(*) AS n
FROM prediction p
JOIN article a   ON a.id = p.article_id AND a.split = 'test'
JOIN category ct ON ct.id = a.category_id
JOIN category cp ON cp.id = p.pred_category_id
GROUP BY p.run_id, ct.id, cp.id;
