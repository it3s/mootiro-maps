ALTER TABLE authentication_user ADD COLUMN about_me text;
-- ALTER TABLE authentication_user ADD COLUMN contact text;
ALTER TABLE authentication_user DROP COLUMN verification_key;

UPDATE authentication_user
  SET
    about_me = concat(authentication_user.about_me, authentication_user.contact),
    contact  = ''
;
