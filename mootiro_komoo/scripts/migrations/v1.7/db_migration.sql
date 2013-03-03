ALTER TABLE organization_organization ADD COLUMN lines geometry;
ALTER TABLE organization_organization ADD COLUMN points geometry;
ALTER TABLE organization_organization ADD COLUMN polys geometry;
ALTER TABLE organization_organization ADD COLUMN geometry geometry;

ALTER TABLE organization_organization ADD CONSTRAINT enforce_dims_geometry CHECK (st_ndims(geometry) = 2);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_dims_lines CHECK (st_ndims(lines) = 2);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_dims_points CHECK (st_ndims(points) = 2);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_dims_polys CHECK (st_ndims(polys) = 2);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_geotype_geometry CHECK (geometrytype(geometry) = 'GEOMETRYCOLLECTION'::text OR geometry IS NULL);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_geotype_lines CHECK (geometrytype(lines) = 'MULTILINESTRING'::text OR lines IS NULL);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_geotype_points CHECK (geometrytype(points) = 'MULTIPOINT'::text OR points IS NULL);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_geotype_polys CHECK (geometrytype(polys) = 'MULTIPOLYGON'::text OR polys IS NULL);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_srid_geometry CHECK (st_srid(geometry) = 4326);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_srid_lines CHECK (st_srid(lines) = 4326);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_srid_points CHECK (st_srid(points) = 4326);
ALTER TABLE organization_organization ADD CONSTRAINT enforce_srid_polys CHECK (st_srid(polys) = 4326);

CREATE INDEX organization_organization_geometry_id
  ON organization_organization
  USING gist
  (geometry );

CREATE INDEX organization_organization_lines_id
  ON organization_organization
  USING gist
  (lines );

CREATE INDEX organization_organization_points_id
  ON organization_organization
  USING gist
  (points );

CREATE INDEX organization_organization_polys_id
  ON organization_organization
  USING gist
  (polys );

UPDATE organization_organization
  SET
    geometry = organization_organizationbranch.geometry,
    points   = organization_organizationbranch.points,
    lines    = organization_organizationbranch.lines,
    polys    = organization_organizationbranch.polys
  FROM organization_organizationbranch
  WHERE organization_organization.id = organization_organizationbranch.organization_id;

DROP TABLE organization_organizationbranch_community;
DROP TABLE organization_organizationbranch;
