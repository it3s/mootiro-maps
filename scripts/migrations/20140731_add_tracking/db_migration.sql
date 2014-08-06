BEGIN;
CREATE TABLE "tracking_tracking" (
    "id" serial NOT NULL PRIMARY KEY,
    "url" varchar(200) NOT NULL,
    "ip_address" inet,
    "visitor_id" integer REFERENCES "authentication_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "visited_date" timestamp with time zone NOT NULL
)
;
CREATE INDEX "tracking_tracking_url" ON "tracking_tracking" ("url");
CREATE INDEX "tracking_tracking_url_like" ON "tracking_tracking" ("url" varchar_pattern_ops);
CREATE INDEX "tracking_tracking_visitor_id" ON "tracking_tracking" ("visitor_id");
CREATE INDEX "tracking_tracking_visited_date" ON "tracking_tracking" ("visited_date");
COMMIT;

