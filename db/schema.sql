CREATE TABLE IF NOT EXISTS production_units (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  renewable_source TEXT,
  current_output NUMERIC(18,6),
  max_capacity NUMERIC(18,6),
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS storage_tanks (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  pressure DOUBLE PRECISION,
  temperature DOUBLE PRECISION,
  capacity NUMERIC(18,6),
  current_level NUMERIC(18,6),
  leakage_detected BOOLEAN,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS transport_fleet (
  id BIGSERIAL PRIMARY KEY,
  vehicle_id TEXT NOT NULL,
  mode TEXT NOT NULL,
  location TEXT,
  status TEXT,
  hydrogen_load NUMERIC(18,6),
  destination TEXT
);

CREATE TABLE IF NOT EXISTS demand_logs (
  id BIGSERIAL PRIMARY KEY,
  region TEXT NOT NULL,
  demand_value NUMERIC(18,6) NOT NULL,
  timestamp TIMESTAMPTZ
);