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

--------------
-- language --
--------------

create table language (
    id      char(2)     not null,
    name    smalltext   not null,

    constraint pk_language
        primary key(id)
);

insert into language(id, name) values ('en', 'English');

------------------
-- content_type --
------------------

create table content_type (
    id          smallserial not null,
    name        smalltext   not null,
    icons       json,
    description text,

    constraint pk_content_type
        primary key(id)
);

create unique index u_idx_content_type_name
    on content_type(lower(name));

insert into content_type(name, icons) values('folder', '{"fa": "fa-folder"}');
insert into content_type(name, icons) values('document', '{"fa": "fa-file-text-o"}');
insert into content_type(name, icons) values('event', '{"fa": "fa-calendar"}');
insert into content_type(name, icons) values('file', '{"fa": "fa-file-o"}');

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

-------------
-- account --
-------------

create table account (
    id          serial      not null,
    login       smalltext   not null,
    password    char(60)    not null,
    first_name  text        not null,
    last_name   text        not null,
    email       smalltext   not null,
    created     timestamptz not null    default current_timestamp,
    enabled     boolean     not null    default false,
    lost_token 	char(32),

    constraint pk_account
        primary key(id),

    constraint check_account_length_password
        check (length(password) = 60),

    constraint u_idx_account_login
        unique(login),

    constraint u_idx_account_lost_token
        unique(lost_token)
);

create unique index u_idx_account_email on account(lower(email));

insert into account(login, password, first_name, last_name, email, enabled)
values ('admin', '$2b$12$vx/HBrgoKLP3z5.f6vfRbOlxBI0OOrESvPTpI3V4R84/D477YxMnS', 'admin', 'admin', 'admin@change.this', true);

----------
-- role --
----------

create table role (
    id          serial      not null,
    name        smalltext   not null,
    created     timestamptz not null    default current_timestamp,
    enabled     boolean     not null    default false,
    locked      boolean     not null    default false,
    description text,

    constraint pk_role
        primary key(id)
);

create unique index u_idx_role_name on role(lower(name));

insert into role(name, enabled, locked, description)
values ('system.Everyone', true, true, 'This principal id is granted to all requests');

insert into role(name, enabled, locked, description)
values ('system.Authenticated', true, true, 'Any user with credentials as determined by the current security policy. You might think of it as any user that is "logged in".');

insert into role(name, enabled, locked, description)
values ('Manager', true, true, 'The Manager role is the role that can do everything.');

------------------
-- account_role --
------------------

create table account_role (
    account_id  integer     not null,
    role_id     integer     not null,
    created     timestamptz not null    default current_timestamp,

    constraint pk_account_role
        primary key(account_id, role_id),

    constraint fk_account
        foreign key (account_id) references account(id),

    constraint fk_role
        foreign key(role_id) references role(id)
);

----------------
-- permission --
----------------

create table permission (
    id              serial      not null,
    name            smalltext   not null,
    created         timestamptz not null    default current_timestamp,
    enabled         boolean     not null    default false,
    description     text,
    content_type_id smallint,

    constraint pk_permission
        primary key(id),

    constraint fk_permission_content_type
        foreign key(content_type_id) references content_type(id)
);

create unique index u_idx_permisison_name on permission(lower(name));

---------------
-- resources --
---------------

create table resource (
    id      serial  not null,
    name    text    not null,

    constraint pk_resource
        primary key (id)
);

create unique index u_idx_resource_name on resource(lower(name));

insert into resource(name) values ('GLOBAL');
insert into resource(name) values ('CONTENT');

---------
-- acl --
---------

create table acl (
    id              serial      not null,
    role_id         integer     not null,
    permission_id   integer     not null,
    resource_id     integer     not null,
    content_id      integer,
    allow           boolean     not null,
    weight          smallint    not null,
    created         timestamptz not null    default current_timestamp,

    constraint pk_acl
        primary key (id),

    constraint fk_role
        foreign key(role_id) references role(id),

    constraint fk_permission
        foreign key (permission_id) references permission(id),

    constraint fk_resource
        foreign key (resource_id) references resource(id),

    constraint fk_acl_content
        foreign key (content_id) references content(id),

    constraint unique_content_resource_weight
        unique (content_id, resource_id, weight) deferrable initially deferred,

    constraint unique_role_permission_resource
        unique(role_id, permission_id, resource_id, content_id)
);

create or replace function t_acl_weight() returns trigger as $weight$
    BEGIN
        PERFORM 1
            FROM acl
            WHERE role_id = NEW.role_id 
                AND resource_id = NEW.resource_id
            FOR UPDATE;

        IF NEW.content_id IS NOT NULL THEN
            NEW.weight := (
                SELECT coalesce(max(weight) + 1, 1)
                FROM acl
                WHERE resource_id = NEW.resource_id
                    AND content_id = NEW.content_id
            );
        ELSE
            NEW.weight := (
                SELECT coalesce(max(weight) + 1, 1)
                FROM acl
                WHERE role_id = NEW.role_id 
                    AND resource_id = NEW.resource_id
            );

        END IF;

        RETURN NEW;
    END;
$weight$ language plpgsql;

create trigger t_acl_weight before insert on acl
    for each row execute procedure t_acl_weight();

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

create unique index u_idx_mime_name_major_id 
    on mime(lower(name), major_id);

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
    title               mediumtext  not null,
    description         text,
    fts                 tsvector,
    added               timestamptz not null    default current_timestamp,
    updated             timestamptz,
    effective           timestamptz,
    expiration          timestamptz,
    exclude_nav         boolean     not null    default false,
    weight              integer     not null,
    is_fts              boolean     not null    default true,
    props               json,

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
        check(expiration > effective),

    constraint content_unique_weight_container_id
        unique(container_id, weight) deferrable initially deferred
);

create index idx_content_container_id
    on content(container_id);

create unique index u_idx_content_container_id
    on content((1)) where container_id is null; 

create index idx_content_owner_id
    on content(owner_id);

create index idx_content_weight
    on content(weight);

create index idx_content_coalesce_updated_added 
    on content(COALESCE(updated, added));

create index idx_content_fts
    on content using gin(fts);

insert into content (content_type_id, owner_id, state_id, weight, title, description) 
values (
    (select id from content_type where name='folder'), 
    (select id from account where login='admin'), 
    (select id from state where name='published'), 
    1,
    'Home',
    'Root'
);

create or replace function t_container_id() returns trigger as $weight$
    declare
        container_id_changed CONSTANT boolean := TG_OP = 'UPDATE' AND NEW.container_id IS DISTINCT FROM OLD.container_id;
        compute_new_weight CONSTANT boolean := TG_OP = 'INSERT' OR container_id_changed;
    begin
        if container_id_changed then
            -- Prevent concurrent modifications.
            PERFORM 1
            FROM folder
            WHERE content_id = NEW.container_id
            FOR UPDATE;

            PERFORM 1
            FROM folder
            WHERE content_id = NEW.id
            FOR UPDATE;

            IF FOUND THEN

                /*
                    Imagine we have the following:

                           A
                          / \
                        B     C
                       / \   /
                      D   F G
                     /     \
                    E       H
                           / \
                          I   J
               
                    We must ensure that the NEW.container_id is not part of it's 
                    lower hierarchy. 

                    For example an error must be raised if:
                    - we update B and NEW.container_id equals to the id 
                      of any D,F,E,H,I,J
                    - we update F and NEW.container_id equals to the id 
                      of any H,I,J
                    - ...

                    The query below checks that if we update B.container_id the 
                    NEW.container_id is not a child of B.
                */

                IF EXISTS (
                    WITH RECURSIVE children AS (
                            SELECT c1.id
                            FROM content c1
                            JOIN folder f1 ON c1.id = f1.content_id 
                            WHERE c1.container_id = NEW.id
                        UNION ALL 
                            SELECT c2.id
                            FROM content c2 
                            JOIN folder f2 ON c2.id = f2.content_id 
                            JOIN children ch ON ch.id = c2.container_id
                    ) 

                    SELECT * FROM children WHERE id = NEW.container_id
                ) 
                THEN
                    RAISE EXCEPTION '% is a child of %', NEW.container_id, 
                        NEW.id;
                END IF;
                
            END IF;  -- FOUND

        END IF;  -- container_id_changed

        IF compute_new_weight THEN
            NEW.weight := (
                SELECT coalesce(max(weight) + 1, 1)
                FROM content
                WHERE container_id = NEW.container_id
            );

            RAISE NOTICE 'weight of % within container % set to %', NEW.id, 
                NEW.container_id, NEW.weight;
        END IF;  -- compute_new_weight

        return NEW;
    end;
$weight$ language plpgsql;

create trigger t_container_id before insert or update on content
    for each row execute procedure t_container_id();


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

--------------
-- document --
--------------

create table document (
    content_id  integer not null,
    body        text    not null,

    constraint pk_document
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
        foreign key(index_content_id) references document(content_id)
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
    path_name       serial  not null,

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
    body                text        not null,
    starts              timestamp   not null,
    ends                timestamp   not null,
    location            text,
    address             text,
    address_latitude    float,
    address_longitude   float,
    url                 url,
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
