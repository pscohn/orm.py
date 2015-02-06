

drop table if exists "user" CASCADE;
create table "user" ( 
id serial primary key,
username varchar(255),
password varchar(255)
);

drop table if exists message CASCADE;
create table message (
id serial primary key,
user_from_id integer REFERENCES "user" ON DELETE CASCADE,
user_to_id integer REFERENCES "user" ON DELETE CASCADE,
date_sent timestamp,
body varchar(255),
read boolean
);
