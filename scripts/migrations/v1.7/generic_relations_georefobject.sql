-- Removing unused tables + Adding generic relations and georefobj

DROP TABLE main_relations;
DROP TABLE main_relationtypetranslations;
DROP TABLE main_relationtype;
-- DROP INDEX main_relations_obj1_id;
-- DROP INDEX main_relations_obj2_id;
-- DROP INDEX main_relations_relation_type_from_1_to_2_id;
-- DROP INDEX main_relations_relation_type_from_2_to_1_id;
-- DROP INDEX main_relationtypetranslations_relation_type_id;

-- Table: main_genericref

-- DROP TABLE main_genericref;

CREATE TABLE main_genericref
(
  id serial NOT NULL,
  obj_table character varying(1024) NOT NULL,
  obj_id integer NOT NULL,
  CONSTRAINT main_genericref_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);


CREATE TABLE main_genericrelation
(
  id serial NOT NULL,
  obj1_id integer NOT NULL,
  obj2_id integer NOT NULL,
  relation_type character varying(1024),
  creation_date timestamp with time zone NOT NULL,
  CONSTRAINT main_genericrelation_pkey PRIMARY KEY (id ),
  CONSTRAINT main_genericrelation_obj1_id_fkey FOREIGN KEY (obj1_id)
      REFERENCES main_genericref (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT main_genericrelation_obj2_id_fkey FOREIGN KEY (obj2_id)
      REFERENCES main_genericref (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);

CREATE INDEX main_genericrelation_obj1_id
  ON main_genericrelation
  USING btree
  (obj1_id );

CREATE INDEX main_genericrelation_obj2_id
  ON main_genericrelation
  USING btree
  (obj2_id );

CREATE TABLE main_georefobject
(
  id serial NOT NULL,
  name character varying(512) NOT NULL,
  description text NOT NULL,
  otype character varying(512) NOT NULL,
  creator_id integer,
  creation_date timestamp with time zone NOT NULL,
  last_editor_id integer,
  last_update timestamp with time zone NOT NULL,
  extra_data text,
  contact text,
  points geometry,
  lines geometry,
  polys geometry,
  geometry geometry,
  CONSTRAINT main_georefobject_pkey PRIMARY KEY (id ),
  CONSTRAINT creator_id_refs_id_26a1efbc FOREIGN KEY (creator_id)
      REFERENCES authentication_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT last_editor_id_refs_id_26a1efbc FOREIGN KEY (last_editor_id)
      REFERENCES authentication_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT enforce_dims_geometry CHECK (st_ndims(geometry) = 2),
  CONSTRAINT enforce_dims_lines CHECK (st_ndims(lines) = 2),
  CONSTRAINT enforce_dims_points CHECK (st_ndims(points) = 2),
  CONSTRAINT enforce_dims_polys CHECK (st_ndims(polys) = 2),
  CONSTRAINT enforce_geotype_geometry CHECK (geometrytype(geometry) = 'GEOMETRYCOLLECTION'::text OR geometry IS NULL),
  CONSTRAINT enforce_geotype_lines CHECK (geometrytype(lines) = 'MULTILINESTRING'::text OR lines IS NULL),
  CONSTRAINT enforce_geotype_points CHECK (geometrytype(points) = 'MULTIPOINT'::text OR points IS NULL),
  CONSTRAINT enforce_geotype_polys CHECK (geometrytype(polys) = 'MULTIPOLYGON'::text OR polys IS NULL),
  CONSTRAINT enforce_srid_geometry CHECK (st_srid(geometry) = 4326),
  CONSTRAINT enforce_srid_lines CHECK (st_srid(lines) = 4326),
  CONSTRAINT enforce_srid_points CHECK (st_srid(points) = 4326),
  CONSTRAINT enforce_srid_polys CHECK (st_srid(polys) = 4326)
)
WITH (
  OIDS=FALSE
);

CREATE INDEX main_georefobject_creator_id
  ON main_georefobject
  USING btree
  (creator_id );

CREATE INDEX main_georefobject_geometry_id
  ON main_georefobject
  USING gist
  (geometry );

CREATE INDEX main_georefobject_last_editor_id
  ON main_georefobject
  USING btree
  (last_editor_id );

CREATE INDEX main_georefobject_lines_id
  ON main_georefobject
  USING gist
  (lines );

CREATE INDEX main_georefobject_points_id
  ON main_georefobject
  USING gist
  (points );

CREATE INDEX main_georefobject_polys_id
  ON main_georefobject
  USING gist
  (polys );

