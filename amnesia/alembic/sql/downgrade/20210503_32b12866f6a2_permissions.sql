DO $$
DECLARE
    all_permissions text[][] := '{{"ALL_PERMISSIONS", "All permissions"}, {"create_content", "Add any type of content"}, {"read_content", "Read any type of content"}, {"edit_content", "Edit any type of content"}, {"delete_content", "Delete any type of content"}, {"manage_acl", "Manage access control list (ACL)"}, {"manage_roles", "Manage roles"}, {"bulk_delete", "Folder bulk delete content"}, {"bulk_delete_own", "Folder bulk delete own content"}}';
    perm text[];
BEGIN

    FOREACH perm slice 1 IN ARRAY all_permissions
    LOOP
        DELETE FROM acl WHERE permission_id=(
            SELECT id FROM permission WHERE name=perm[1]
        );
        DELETE FROM permission WHERE name=perm[1];
    END LOOP;

END$$;
