ALTER TABLE organization_organization ADD COLUMN contacts text;

ALTER TABLE komoo_resource_resource ADD COLUMN contacts text;

ALTER TABLE komoo_project_project ADD COLUMN contacts text;

ALTER TABLE need_need ADD COLUMN contacts text;
ALTER TABLE need_need RENAME COLUMN title TO name;

ALTER TABLE community_community ADD COLUMN contacts text;
