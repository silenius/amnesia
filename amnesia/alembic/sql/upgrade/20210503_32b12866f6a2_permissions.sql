DO $$
DECLARE
    all_permissions text[][] := '{{"ALL_PERMISSIONS", "All permissions"}, {"create_content", "Add any type of content"}, {"read_content", "Read any type of content"}, {"edit_content", "Edit any type of content"}, {"delete_content", "Delete any type of content"}, {"manage_acl", "Manage access control list (ACL)"}, {"manage_roles", "Manage roles"}, {"bulk_delete", "Folder bulk delete content"}, {"bulk_delete_own", "Folder bulk delete own content"}}';
    perm text[];
BEGIN

    FOREACH perm slice 1 IN ARRAY all_permissions
    LOOP
        IF NOT EXISTS (
            SELECT name FROM permission WHERE name=perm[1]
        )
        THEN
            INSERT INTO permission(name, enabled, description)
            VALUES (perm[1], true, perm[2]);
        ELSE
            RAISE NOTICE 'Permission % already exists', perm[1];
        END IF;
    END LOOP;

END$$;
