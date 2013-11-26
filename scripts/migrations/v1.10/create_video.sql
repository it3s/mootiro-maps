BEGIN;
CREATE TABLE "video_video" (
    "id" serial NOT NULL PRIMARY KEY,
    "title" text,
    "description" text,
    "video_url" varchar(200) NOT NULL,
    "video_id" varchar(100) NOT NULL,
    "thumbnail_url" varchar(200),
    "service" varchar(2) NOT NULL,
    "content_type_id" integer REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0)
)
;
CREATE INDEX "video_video_content_type_id" ON "video_video" ("content_type_id");
COMMIT;
