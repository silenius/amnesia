alter table content alter column props set data type jsonb;
alter table folder alter column default_order set data type jsonb;

create index idx_content_props_gin ON content USING GIN (props jsonb_ops);
create index idx_folder_default_order_gin ON folder USING GIN (default_order jsonb_ops);
