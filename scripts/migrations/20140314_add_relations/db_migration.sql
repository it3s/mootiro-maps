-- Table: relations_relation

-- DROP TABLE relations_relation;

CREATE TABLE relations_relation
(
  id serial NOT NULL,
  oid_1 character varying(64) NOT NULL,
  oid_2 character varying(64) NOT NULL,
  rel_type character varying(246) NOT NULL,
  direction character varying(1) NOT NULL,
  creation_date timestamp with time zone NOT NULL,
  last_update timestamp with time zone NOT NULL,
  CONSTRAINT relations_relation_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Remove contact and link
ALTER TABLE komoo_resource_resource DROP COLUMN contact;
ALTER TABLE organization_organization DROP COLUMN contact;
ALTER TABLE organization_organization DROP COLUMN link;
ALTER TABLE komoo_project_project DROP COLUMN contact;


