-- Removing unused tables

DROP TABLE main_genericref;

DROP TABLE main_genericrelation;
DROP INDEX main_genericrelation_obj1_id;
DROP INDEX main_genericrelation_obj2_id;

DROP TABLE main_georefobject;
DROP INDEX main_georefobject_creator_id;
DROP INDEX main_georefobject_geometry_id;
DROP INDEX main_georefobject_last_editor_id;
DROP INDEX main_georefobject_lines_id;
DROP INDEX main_georefobject_points_id;
DROP INDEX main_georefobject_polys_id;
