create table account_audit_login(
    id          serial      not null,
    account_id  integer     not null,
    ts          timestamptz not null    default current_timestamp,
    ip          inet        not null,
    success     boolean     not null,
    info        jsonb,

    constraint pk_account_login
        primary key(id),

    constraint fk_account_login_account
        foreign key(account_id) references account(id)
);
