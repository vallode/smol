drop table if exists links;
create table links (
  id integer primary key autoincrement,
  'originalURL' text not null
);