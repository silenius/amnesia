ALTER TABLE mime RENAME icons TO icon;
UPDATE mime SET icon=NULL;
ALTER TABLE mime alter icons type TEXT;
ALTER TABLE mime_major RENAME icons TO icon;
UPDATE mime_major SET icon=NULL;
ALTER TABLE mime_major alter icons type TEXT;
