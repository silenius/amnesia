-------------
-- DOMAINS --
-------------

create domain url as text
    constraint check_proto_length check (
        value ~* '^https?://' and
        length(value) > 10
    );

create domain tinytext as text
    constraint check_length check(
        length(value) <= 32
    );

create domain smalltext as text
    constraint check_length check(
        length(value) <= 128
    );

create domain mediumtext as text
    constraint check_length check(
        length(value) <= 512
    );

------------
-- TABLES --
------------

------------------
-- content_type --
------------------

create table content_type (
    id          smallserial not null,
    name        smalltext   not null,
    icon        text        not null,
    description text,

    constraint pk_content_type
        primary key(id)
);

create unique index u_idx_content_type_name
    on content_type(lower(name));

insert into content_type(name, icon) values('folder', 'folder.png');
insert into content_type(name, icon) values('page', 'page.png');
insert into content_type(name, icon) values('event', 'event.png');
insert into content_type(name, icon) values('news', 'news.png');
insert into content_type(name, icon) values('file', 'file.png');

-----------
-- state --
-----------

create table state (
    id          smallserial not null,
    name        smalltext   not null,
    description text,

    constraint pk_state
        primary key(id)
);

create unique index u_idx_state_name
    on state(lower(name));

insert into state(name) values ('private');
insert into state(name) values ('pending');
insert into state(name) values ('published');

-----------
-- account --
-----------

create table account (
    id          serial      not null,
    login       smalltext   not null,
    password    char(60)    not null,
    first_name  text        not null,
    last_name   text        not null,
    gender      char,
    email       text        not null,
    created     timestamptz not null    default current_timestamp,
    blocked     boolean     not null    default false,

    constraint pk_account
        primary key(id),

    constraint check_account_length_password
        check (length(password) = 60),

    constraint u_idx_account_login
        unique(login),

    constraint check_account_gender
        check(lower(gender) in ('m', 'f'))
);

insert into account(login, password, first_name, last_name, email)
values ('admin', '$2b$12$vx/HBrgoKLP3z5.f6vfRbOlxBI0OOrESvPTpI3V4R84/D477YxMnS', 'admin', 'admin', 'admin@change.this');

----------------
-- mime_major --
----------------

create table mime_major (
    id      smallserial not null,
    name    smalltext   not null,
    icon    text,

    constraint pk_mime_major
        primary key(id)
);

create unique index u_idx_mime_major_name
    on mime_major(lower(name));

----------
-- mime --
----------

create table mime (
    id          smallserial not null,
    name        smalltext   not null,
    template    smalltext   not null,
    major_id    smallint    not null,
    icon        text,
    ext         smalltext,

    constraint pk_mime
        primary key(id),

    constraint fk_mime_major
        foreign key(major_id) references mime_major(id)
);

create index idx_mime_major_id
    on mime(major_id);

---------
-- tag --
---------

create table tag (
    id          serial      not null,
    name        smalltext   not null,
    description text,

    constraint pk_tag
        primary key(id)
);

create unique index u_idx_tag_name
    on tag(lower(name));

-------------
-- content --
-------------

create table content (
    id                  serial      not null,
    added               timestamptz not null    default current_timestamp,
    updated             timestamptz,
    title               mediumtext  not null,
    description         text,
    effective           timestamptz,
    expiration          timestamptz,
    exclude_nav         boolean     not null    default false,
    weight              integer     not null,
    is_fts              boolean     not null    default true,
    props               json,
    fts                 tsvector,

    content_type_id     smallint    not null,
    owner_id            integer     not null,
    state_id            smallint    not null,
    container_id        integer,

    -- PRIMARY KEY

    constraint pk_content
        primary key(id),

    -- FOREIGN KEYS

    constraint fk_content_content_type
        foreign key(content_type_id) references content_type(id),

    constraint fk_account
        foreign key(owner_id) references account(id),

    constraint fk_state
        foreign key(state_id) references state(id),

    -- CHECK CONSTRAINTS

    constraint check_container
        check(id != container_id),

    constraint check_added_updated
        check(updated > added),

    constraint check_effective_expiration
        check(expiration > effective)
--
--    constraint content_unique_weight_container_id
--        unique(container_id, weight)
);

create index idx_content_container_id
    on content(container_id);

create index idx_content_owner_id
    on content(owner_id);

create index idx_content_weight
    on content(weight);

create index idx_content_coalesce_updated_added 
    on content(COALESCE(updated, added));

create index idx_content_fts
    on content using gin(fts);

insert into content (title, content_type_id, owner_id, state_id, weight) 
values ('Home', (select id from content_type where name='folder'), (select id from account where login='admin'), (select id from state where name='published'), 1);

create or replace function compute_weight() returns trigger as $weight$
    begin
        if (TG_OP = 'INSERT' or (TG_OP = 'UPDATE' and NEW.container_id is distinct from OLD.container_id)) then
            NEW.weight := (
                select
                    coalesce(max(weight) + 1, 1)
                from
                    content
                where
                    container_id = NEW.container_id
            );
        end if;

        return NEW;
    end;
$weight$ language plpgsql;

create trigger compute_weight before insert or update on content
    for each row execute procedure compute_weight();

-----------------
-- content tag --
-----------------

create table content_tag (
    content_id  integer not null,
    tag_id      integer not null,

    constraint pk_content_tag
        primary key(content_id, tag_id),

    constraint fk_content_tag_content
        foreign key (content_id) references content(id),

    constraint fk_content_tag_tag
        foreign key (tag_id) references tag(id)
);

----------
-- page --
----------

create table page (
    content_id  integer not null,
    body        text    not null,

    constraint pk_page
        primary key(content_id),

    constraint fk_content
        foreign key(content_id) references content(id)
);

------------
-- folder --
------------

create table folder (
    content_id          integer not null,
    max_children        integer,
    index_content_id    integer,
    polymorphic_loading boolean not null default false,
    rss                 boolean not null default false,
    default_order       json,

    constraint pk_folder
        primary key(content_id),

    constraint fk_content
        foreign key(content_id) references content(id),

    constraint fk_content_index_view
        foreign key(index_content_id) references content(id)
);

insert into folder(content_id) values (1);

alter table content add constraint fk_folder 
    foreign key(container_id) references folder(content_id);

-------------------------------------
-- folder polymorphic content type --
-------------------------------------

create table folder_polymorphic_loading (
    folder_id       integer     not null,
    content_type_id smallint    not null,

    constraint pk_folder_polymorphic_loading
        primary key(folder_id, content_type_id),

    constraint fk_folder
        foreign key(folder_id) references folder(content_id),

    constraint fk_content_type
        foreign key(content_type_id) references content_type(id)
);

----------
-- data --
----------

create table data (
    content_id      integer not null,
    mime_id         integer not null,
    original_name   text    not null,
    file_size       real    not null,

    constraint pk_data
        primary key(content_id),

    constraint fk_content
        foreign key(content_id) references content(id),

    constraint fk_mime
        foreign key(mime_id) references mime(id) deferrable initially deferred
);

-------------
-- country --
-------------

create table country (
    iso     char(2) not null,    
    name    text    not null,

    constraint pk_country
        primary key(iso)
);

create unique index u_idx_country_name
    on country(lower(name));

-----------
-- event --
-----------

create table event (
    starts              timestamptz not null,
    ends                timestamptz not null,
    location            text,
    address             text,
    address_latitude    float,
    address_longitude   float,
    url                 url,
    body                text        not null,
    attendees           text,
    contact_name        text,
    contact_email       text,
    contact_phone       text,
    country_iso         char(2)     not null,
    content_id          integer     not null,

    constraint pk_event
        primary key(content_id),

    constraint fk_country
        foreign key(country_iso) references country(iso),

    constraint fk_content
        foreign key(content_id) references content(id),

    constraint event_check_starts_ends
        check(starts <= ends),

    constraint event_check_latitude
        check(address_latitude between -90 and 90),

    constraint event_check_longitude
        check(address_longitude between -180 and 180)
);

create index idx_event_starts
    on event(starts);

create index idx_event_country_iso
    on event(country_iso);
