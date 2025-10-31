-- ShowMojo Webhook System Database Initialization Script
-- PostgreSQL Database Schema

-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS showings CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS listings CASCADE;
DROP TABLE IF EXISTS prospects CASCADE;

-- Create events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(100),
    team_member_name VARCHAR(255),
    team_member_uid VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    raw_payload JSONB NOT NULL
);

-- Create indexes for events table
CREATE INDEX idx_events_event_id ON events(event_id);
CREATE INDEX idx_events_action ON events(action);
CREATE INDEX idx_events_created_at ON events(created_at);

-- Create showings table
CREATE TABLE showings (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(100) UNIQUE NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    showtime TIMESTAMP WITH TIME ZONE,
    showing_time_zone VARCHAR(100),
    showing_time_zone_utc_offset INTEGER,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    notes TEXT,
    listing_uid VARCHAR(100),
    listing_full_address TEXT,
    is_self_show BOOLEAN,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    self_show_code_distributed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

-- Create indexes for showings table
CREATE INDEX idx_showings_uid ON showings(uid);
CREATE INDEX idx_showings_listing_uid ON showings(listing_uid);
CREATE INDEX idx_showings_email ON showings(email);
CREATE INDEX idx_showings_showtime ON showings(showtime);
CREATE INDEX idx_showings_created_at ON showings(created_at);

-- Create listings table
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(100) UNIQUE NOT NULL,
    full_address TEXT NOT NULL,
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_showings INTEGER DEFAULT 0
);

-- Create indexes for listings table
CREATE INDEX idx_listings_uid ON listings(uid);
CREATE INDEX idx_listings_full_address ON listings(full_address);

-- Create prospects table
CREATE TABLE prospects (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    first_contact_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_contact_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_showings INTEGER DEFAULT 0
);

-- Create indexes for prospects table
CREATE INDEX idx_prospects_email ON prospects(email);
CREATE INDEX idx_prospects_phone ON prospects(phone);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at in showings table
CREATE TRIGGER update_showings_updated_at BEFORE UPDATE ON showings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your deployment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'ShowMojo Webhook System database schema created successfully!';
END $$;
