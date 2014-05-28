ALTER TABLE komoo_project_project ADD COLUMN bounds_cache geometry;
ALTER TABLE komoo_project_project ADD COLUMN custom_bounds geometry;
ALTER TABLE komoo_project_project ADD COLUMN maptype varchar(32);

ALTER TABLE komoo_project_project ADD CONSTRAINT enforce_dims_bounds_cache CHECK (st_ndims(bounds_cache) = 2);
ALTER TABLE komoo_project_project ADD CONSTRAINT enforce_dims_custom_bounds CHECK (st_ndims(custom_bounds) = 2);

ALTER TABLE komoo_project_project ADD CONSTRAINT enforce_geotype_bounds_cache CHECK (geometrytype(bounds_cache) = 'POLYGON'::text OR bounds_cache IS NULL);
ALTER TABLE komoo_project_project ADD CONSTRAINT enforce_geotype_custom_bounds CHECK (geometrytype(custom_bounds) = 'POLYGON'::text OR custom_bounds IS NULL);

ALTER TABLE komoo_project_project ADD CONSTRAINT enforce_srid_bounds_cache CHECK (st_srid(bounds_cache) = 4326);
ALTER TABLE komoo_project_project ADD CONSTRAINT enforce_srid_custom_bounds CHECK (st_srid(custom_bounds) = 4326);

CREATE INDEX komoo_project_project_bounds_cache_id
  ON komoo_project_project
  USING gist
  (bounds_cache );

CREATE INDEX komoo_project_project_custom_bounds_id
  ON komoo_project_project
  USING gist
  (custom_bounds );
