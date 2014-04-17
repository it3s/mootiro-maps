CREATE TABLE "komoo_project_layer" (
    "id" serial NOT NULL PRIMARY KEY,
    "project_id" integer NOT NULL,
    "name" varchar(1024) NOT NULL,
    "position" smallint CHECK ("position" >= 0),
    "visible" boolean,
    "rule" text NOT NULL,
    "fillColor" varchar(10) NOT NULL,
    "strokeColor" varchar(10) NOT NULL
)
;

ALTER TABLE "komoo_project_layer" ADD CONSTRAINT "project_id_refs_id_46da478f" FOREIGN KEY ("project_id") REFERENCES "komoo_project_project" ("id") DEFERRABLE INITIALLY DEFERRED;
