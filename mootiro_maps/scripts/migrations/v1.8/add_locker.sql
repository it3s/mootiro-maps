-- Table: locker_locker

CREATE TABLE locker_locker
(
  id serial NOT NULL,
  key character varying(32) NOT NULL,
  data text NOT NULL,
  expiration_date timestamp with time zone,
  CONSTRAINT locker_locker_pkey PRIMARY KEY (id )
)
