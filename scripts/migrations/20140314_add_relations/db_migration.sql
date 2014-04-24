
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

CREATE TABLE relations_relationmetadata
(
  id serial NOT NULL,
  value double precision,
  start_date date,
  end_date date,
  description text,
  relation_id integer,
  CONSTRAINT relations_relationmetadata_pkey PRIMARY KEY (id ),
  CONSTRAINT relations_relationmetadata_relation_id_fkey FOREIGN KEY (relation_id)
      REFERENCES relations_relation (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);

CREATE INDEX relations_relationmetadata_relation_id
  ON relations_relationmetadata
  USING btree
  (relation_id );


CREATE INDEX relations_relation_oid_1
  ON relations_relation
  USING btree
  (oid_1 );

CREATE INDEX relations_relation_oid_2
  ON relations_relation
  USING btree
  (oid_2 );

-- Remove contact and link
ALTER TABLE komoo_resource_resource DROP COLUMN contact;
ALTER TABLE organization_organization DROP COLUMN contact;
ALTER TABLE organization_organization DROP COLUMN link;
ALTER TABLE komoo_project_project DROP COLUMN contact;


