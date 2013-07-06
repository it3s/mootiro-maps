-- TAGS

CREATE TABLE tags_tagnamespace
(
  id serial NOT NULL,
  name character varying(128) NOT NULL,
  CONSTRAINT tags_tagnamespace_pkey PRIMARY KEY (id ),
  CONSTRAINT tags_tagnamespace_name_key UNIQUE (name )
)
WITH (
  OIDS=FALSE
);

CREATE TABLE tags_tag
(
  id serial NOT NULL,
  name character varying(128) NOT NULL,
  namespace_id integer NOT NULL,
  CONSTRAINT tags_tag_pkey PRIMARY KEY (id ),
  CONSTRAINT tags_tag_namespace_id_fkey FOREIGN KEY (namespace_id)
      REFERENCES tags_tagnamespace (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);

CREATE INDEX tags_tag_namespace_id
  ON tags_tag
  USING btree
  (namespace_id );

CREATE TABLE tags_taggedobject
(
  id serial NOT NULL,
  tag_id integer NOT NULL,
  object_id integer NOT NULL,
  object_table character varying(512) NOT NULL,
  CONSTRAINT tags_taggedobject_pkey PRIMARY KEY (id ),
  CONSTRAINT tags_taggedobject_tag_id_fkey FOREIGN KEY (tag_id)
      REFERENCES tags_tag (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);

CREATE INDEX tags_taggedobject_tag_id
  ON tags_taggedobject
  USING btree
  (tag_id );




