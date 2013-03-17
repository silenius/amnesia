------------
-- passwd --
------------

create table passwd (
    id          serial      not null,
    login       text        not null,
    password    text        not null,
    first_name  text        not null,
    last_name   text        not null,
    gender      char,
    email       text        not null,
    created     timestamptz not null    default current_timestamp,
    blocked     boolean     not null    default false,

    constraint pk_passwd
        primary key(id),

    constraint check_passwd_length_password
        check (length(password) = 60),

    constraint check_passwd_length_login
        check (length(login) >= 4),

    constraint check_passwd_gender
        check (lower(gender) in ('m', 'f')),

    constraint u_idx_passd_login
        unique(login)
);

insert into passwd(login, password, first_name, last_name, email)
values('admin', '$2a$12$2lX5LisvKqtGAmxJVLe.OuHCdTJ2Ep2vxiM.nGG2Xx0LZRNNLOs5O', 'admin', 'admin', 'change@this.com');

------------------
-- content_type --
------------------

create table content_type (
    id          serial      not null,
    name        varchar(64) not null,
    icon        text        not null,
    description text,

    constraint pk_content_type
        primary key(id)
);

create unique index u_idx_content_type_name
    on content_type(lower(name));

insert into content_type(name, icon) values ('folder', 'folder.png');
insert into content_type(name, icon) values ('page', 'page.png');
insert into content_type(name, icon) values ('event', 'event.png');
insert into content_type(name, icon) values ('news', 'news.png');
insert into content_type(name, icon) values ('file', 'file.png');

-----------
-- state --
-----------

create table state (
    id          serial      not null,
    name        varchar(32) not null,
    description text,

    constraint pk_state
        primary key(id)
);

create unique index u_idx_state_name
    on state(lower(name));

insert into state(name) values ('private');
insert into state(name) values ('pending');
insert into state(name) values ('published');

---------
-- tag --
---------

create table tag (
    id          serial      not null,
    name        varchar(64) not null,
    description text,

    constraint pk_tag
        primary key(id)
);

create unique index u_idx_tag_name
    on tag(lower(name));

-------------
-- country --
-------------

create table country (
    name        varchar(200)    not null,
    iso_code    char(2)         not null,

    constraint pk_country
        primary key(iso_code)
);

-------------
-- content --
-------------

create table content (
    id                  serial          not null,
    added               timestamptz     not null    default current_timestamp,
    updated             timestamptz,
    title               varchar(1024)   not null,
    description         text,
    effective           timestamptz,
    expiration          timestamptz,
    weight              integer         not null,
    is_fts              boolean         not null    default true,
    fts                 tsvector,
    content_type_id     integer         not null,
    icon_content_id     integer,
    container_id        integer,
    owner_id            integer         not null,
    state_id            integer         not null,

    constraint pk_content
        primary key(id),

    constraint fk_content_content_type
        foreign key(content_type_id) references content_type(id),

    constraint fk_passwd
        foreign key(owner_id) references passwd(id),

    constraint fk_state
        foreign key(state_id) references state(id),

    constraint check_container
        check(id != container_id),

    constraint check_added_updated
        check(updated > added),

    constraint check_effective_expiration
        check(expiration > effective)
);

create index idx_content_content_type_id
    on content(content_type_id);

create index idx_content_owner_id
    on content(owner_id);

create index idx_content_state_id
    on content(state_id);

create index idx_content_coalesce_updated_added 
    on content(coalesce(updated, added));

create index idx_content_fts
    on content using gin(fts);

create unique index u_idx_content_container_weight
    on content(container_id, weight);

-- FIXME: two concurrent inserts on the same container will get the same weight
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

insert into content (title, content_type_id, owner_id, state_id) 
values ('Home', (select id from content_type where name='folder'), (select id from passwd where login='admin'), (select id from state where name='published'));

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
    index_content_id    integer,
    max_children        integer,
    polymorphic_loading boolean,
    default_order       bytea,

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

--------------------------------
-- folder polymorphic loading --
--------------------------------

create table folder_polymorphic (
    folder_id       integer not null,
    content_type_id integer not null,

    constraint pk_folder_polymorphic
        primary key(folder_id, content_type_id),

    constraint fk_folder
        foreign key(folder_id) references folder(content_id),

    constraint fk_content_type
        foreign key(content_type_id) references content_type(id)
);

----------------
-- mime_major --
----------------

create table mime_major (
    id      serial      not null,
    name    varchar(64) not null,
    icon    text,

    constraint pk_mime_major
        primary key(id)
);

create unique index u_idx_mime_major_name
    on mime_major(lower(name));

insert into mime_major(name, icon) values ('application', 'application.png');
insert into mime_major(name, icon) values ('audio', 'audio.png');
insert into mime_major(name, icon) values ('image', 'image.png');
insert into mime_major(name, icon) values ('text', 'text.png');
insert into mime_major(name, icon) values ('video', 'video.png');

----------
-- mime --
----------

create table mime (
    id          serial      not null,
    name        varchar(64) not null,
    major_id    integer     not null,
    icon        text,
    ext         varchar(4),

    constraint pk_mime
        primary key(id),

    constraint fk_mime_major
        foreign key(major_id) references mime_major(id)
);

create unique index u_idx_mime_name
    on mime(lower(name));

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

create index idx_data_mime_id
    on data(mime_id);

alter table content add constraint fk_icon_data
    foreign key(icon_content_id) references data(content_id);

-----------
-- event --
-----------

create table event (
    starts              timestamptz     not null,
    ends                timestamptz     not null,
    location            text,
    address             text,
    address_latitude    float,
    address_longitude   float,
    url                 text,
    body                text            not null,
    attendees           text,
    contact_name        varchar(128),
    contact_email       text,
    contact_phone       varchar(64),
    country_iso_code    char(2)         not null,
    content_id          integer         not null,

    constraint pk_event
        primary key(content_id),

    constraint fk_country
        foreign key(country_iso_code) references country(iso_code),

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

----------
-- news --
----------

create table news (
    content_id  integer         not null,
    body        text            not null,
    url         text,

    constraint pk_news
        primary key(content_id),

    constraint fk_content
        foreign key(content_id) references content(id)
);
