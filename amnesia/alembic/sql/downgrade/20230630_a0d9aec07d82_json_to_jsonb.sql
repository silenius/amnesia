alter table content alter column props set data type json;
alter table folder alter column default_order set data type json;

drop index if exists idx_content_props_gin;
drop index if exists idx_folder_default_order_gin;
