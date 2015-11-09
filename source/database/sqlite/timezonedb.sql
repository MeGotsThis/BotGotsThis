DROP TABLE IF EXISTS "updated";
CREATE TABLE "updated" (
    "updated" DATE NOT NULL
);

DROP TABLE IF EXISTS "zone";
CREATE TABLE "zone" (
    "zone_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "country_code" CHAR(2) NOT NULL,
    "zone_name" VARCHAR(35) NOT NULL
);
CREATE INDEX "idx_zone_name" ON "zone" ("zone_name");

DROP TABLE IF EXISTS "timezone";
CREATE TABLE "timezone" (
    "zone_id" INTEGER NOT NULL,
    "abbreviation" VARCHAR(6) NOT NULL,
    "time_start" INT NOT NULL,
    "gmt_offset" INT NOT NULL,
    "dst" CHAR(1) NOT NULL
);
CREATE INDEX "idx_zone_id" ON "timezone" ("zone_id");
CREATE INDEX "idx_time_start" ON "timezone" ("time_start");

DROP TABLE IF EXISTS "country";
CREATE TABLE "country" (
    "country_code" CHAR(2) NULL,
    "country_name" VARCHAR(45) NULL
);
CREATE INDEX "idx_country_code" ON "country" ("country_code");
