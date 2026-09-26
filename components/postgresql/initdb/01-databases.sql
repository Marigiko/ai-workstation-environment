-- Create databases required by the AWE ecosystem.
-- The default database (awe) is created by the postgres image itself.
CREATE DATABASE ai_workstation_gateway;
ALTER DATABASE ai_workstation_gateway OWNER TO awe;
