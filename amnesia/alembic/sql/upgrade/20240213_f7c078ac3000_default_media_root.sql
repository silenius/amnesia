alter table folder add default_media boolean not null default false;

create unique index u_idx_folder_default_media
    on folder((1)) where default_media is true; 
