BEGIN;
ALTER TABLE authentication_user ADD COLUMN country VARCHAR(2);
ALTER TABLE authentication_user ADD COLUMN organization VARCHAR(256);
COMMIT;

