-- Table: model_versioning_modelversion

-- DROP TABLE model_versioning_modelversion;

CREATE TABLE model_versioning_modelversion
(
  id serial NOT NULL,
  table_ref character varying(256) NOT NULL,
  object_id integer NOT NULL,
  creator_id integer NOT NULL,
  creation_date timestamp with time zone NOT NULL,
  data text NOT NULL,
  CONSTRAINT model_versioning_modelversion_pkey PRIMARY KEY (id ),
  CONSTRAINT model_versioning_modelversion_creator_id_fkey FOREIGN KEY (creator_id)
      REFERENCES authentication_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);

-- Index: model_versioning_modelversion_creator_id

-- DROP INDEX model_versioning_modelversion_creator_id;

CREATE INDEX model_versioning_modelversion_creator_id
  ON model_versioning_modelversion
  USING btree
  (creator_id );

