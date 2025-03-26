CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    number INTEGER,
    result INTEGER,
    message_timestamp TIMESTAMP WITH TIME ZONE,
    processed_timestamp TIMESTAMP WITH TIME ZONE
);