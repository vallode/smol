DROP TABLE IF EXISTS links;
CREATE TABLE links (
  id integer primary key autoincrement,
  'originalURL' text,
  'encodedURL' text
);