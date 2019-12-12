-- Take from https://github.com/bbangert/beaker/blob/master/beaker/ext/sqla.py#L129

create table _sessions (
    namespace   varchar(255)    not null,
    accessed    timestamp       not null,
    created     timestamp       not null,
    data        json            not null,

    constraint pk_sessions
        primary key(namespace)
);
