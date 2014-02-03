ALTER TABLE organization_organization ADD COLUMN contacts text;

ALTER TABLE komoo_resource_resource ADD COLUMN contacts text;

ALTER TABLE komoo_project_project ADD COLUMN contacts text;

ALTER TABLE need_need ADD COLUMN contacts text;
ALTER TABLE need_need RENAME COLUMN title TO name;

ALTER TABLE community_community ADD COLUMN contacts text;

ALTER TABLE investment_investment ADD COLUMN contacts text;
ALTER TABLE investment_investment RENAME COLUMN title TO name;

ALTER TABLE proposal_proposal ADD COLUMN short_description VARCHAR(250);
ALTER TABLE proposal_proposal ADD COLUMN contacts text;

ALTER TABLE authentication_user RENAME COLUMN contact to contacts;
UPDATE authentication_user
SET contacts=null;
