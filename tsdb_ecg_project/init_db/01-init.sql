-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create the ecg_data schema
CREATE SCHEMA IF NOT EXISTS ecg_data;

-- Set the search path
SET search_path TO ecg_data, public;

-- Patients Table
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    patient_code VARCHAR(50) UNIQUE NOT NULL,
    age INT,
    gender VARCHAR(10),
    hospital_id INT
);

-- Hospitals Table
CREATE TABLE hospitals (
    hospital_id SERIAL PRIMARY KEY,
    hospital_code VARCHAR(50) UNIQUE NOT NULL,
    hospital_name VARCHAR(255),
    location VARCHAR(255)
);

-- Update Patients Table to Reference Hospitals
ALTER TABLE patients
ADD FOREIGN KEY (hospital_id)
REFERENCES hospitals(hospital_id);

-- Recordings Table
CREATE TABLE recordings (
    recording_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    recording_code VARCHAR(50) UNIQUE NOT NULL,
    recording_start_time TIMESTAMPTZ NOT NULL,
    sampling_frequency FLOAT NOT NULL,
    num_leads INT NOT NULL
);

-- ECG Signals Table
CREATE TABLE ecg_signals (
    time TIMESTAMPTZ NOT NULL,
    recording_id INT REFERENCES recordings(recording_id),
    lead_name VARCHAR(20) NOT NULL,
    lead_value FLOAT NOT NULL,
    PRIMARY KEY (time, recording_id, lead_name)
);

-- Convert ecg_signals into a hypertable
SELECT create_hypertable('ecg_signals', 'time');

-- Annotations Table
CREATE TABLE annotations (
    annotation_id SERIAL PRIMARY KEY,
    recording_id INT REFERENCES recordings(recording_id),
    lead_name VARCHAR(20),
    annotation_type VARCHAR(50) NOT NULL,
    annotation_description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL
);

-- Indexes for Performance
CREATE INDEX idx_annotations_recording_id ON annotations(recording_id);
CREATE INDEX idx_annotations_annotation_type ON annotations(annotation_type);
CREATE INDEX idx_ecg_signals_recording_id ON ecg_signals(recording_id);

-- Set Default Search Path
ALTER ROLE your_username SET search_path TO ecg_data, public;

