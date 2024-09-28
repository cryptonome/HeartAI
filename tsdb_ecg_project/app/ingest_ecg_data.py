import wfdb
import os
import numpy as np
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from utils import connect_to_db

def insert_hospital(cursor, hospital_code, hospital_name, location):
    cursor.execute("""
        INSERT INTO ecg_data.hospitals (hospital_code, hospital_name, location)
        VALUES (%s, %s, %s)
        ON CONFLICT (hospital_code) DO UPDATE SET
            hospital_name = EXCLUDED.hospital_name,
            location = EXCLUDED.location
        RETURNING hospital_id;
    """, (hospital_code, hospital_name, location))
    hospital_id = cursor.fetchone()[0]
    return hospital_id

def insert_patient(cursor, patient_code, age, gender, hospital_id):
    cursor.execute("""
        INSERT INTO ecg_data.patients (patient_code, age, gender, hospital_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (patient_code) DO UPDATE SET
            age = EXCLUDED.age,
            gender = EXCLUDED.gender,
            hospital_id = EXCLUDED.hospital_id
        RETURNING patient_id;
    """, (patient_code, age, gender, hospital_id))
    patient_id = cursor.fetchone()[0]
    return patient_id

def insert_recording(cursor, patient_id, recording_code, recording_start_time, sampling_frequency, num_leads):
    cursor.execute("""
        INSERT INTO ecg_data.recordings (patient_id, recording_code, recording_start_time, sampling_frequency, num_leads)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (recording_code) DO UPDATE SET recording_start_time = EXCLUDED.recording_start_time
        RETURNING recording_id;
    """, (patient_id, recording_code, recording_start_time, sampling_frequency, num_leads))
    recording_id = cursor.fetchone()[0]
    return recording_id

def insert_ecg_signals(cursor, recording_id, recording_start_time, sample_frequency, signal_names, signals):
    data = []
    num_samples = signals.shape[0]
    num_leads = len(signal_names)
    time_increment = timedelta(seconds=1.0 / sample_frequency)

    for i in range(num_samples):
        current_time = recording_start_time + i * time_increment
        for lead_idx in range(num_leads):
            lead_name = signal_names[lead_idx]
            lead_value = float(signals[i, lead_idx])
            data.append((current_time, recording_id, lead_name, lead_value))

        if i % 10000 == 0 and i > 0:
            query = """
                INSERT INTO ecg_data.ecg_signals (time, recording_id, lead_name, lead_value)
                VALUES %s
                ON CONFLICT (time, recording_id, lead_name) DO NOTHING;
            """
            execute_values(cursor, query, data, page_size=10000)
            data.clear()

    if data:
        query = """
            INSERT INTO ecg_data.ecg_signals (time, recording_id, lead_name, lead_value)
            VALUES %s
            ON CONFLICT (time, recording_id, lead_name) DO NOTHING;
        """
        execute_values(cursor, query, data, page_size=10000)
        data.clear()

def insert_annotations(cursor, recording_id, recording_start_time, annotations, sample_frequency):
    data = []
    for i, ann_sample in enumerate(annotations.sample):
        annotation_time = recording_start_time + timedelta(seconds=ann_sample / sample_frequency)
        annotation_type = annotations.symbol[i]
        annotation_description = annotations.aux_note[i] if annotations.aux_note else None

        # For rhythm annotations, calculate end_time
        if i + 1 < len(annotations.sample):
            next_sample = annotations.sample[i + 1]
            end_time = recording_start_time + timedelta(seconds=next_sample / sample_frequency)
        else:
            end_time = annotation_time

        data.append((
            recording_id,
            None,
            annotation_type,
            annotation_description,
            ann_sample,
            annotation_time,
            end_time
        ))

    query = """
        INSERT INTO ecg_data.annotations (
            recording_id,
            lead_name,
            annotation_type,
            annotation_description,
            annotation_sample,
            annotation_time,
            end_time
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cursor, query, data)

def process_and_store_ecg_data(record_path, connection, hospital_info, patient_info):
    record = wfdb.rdrecord(record_path)
    annotation = None
    annotation_path = record_path
    if os.path.exists(annotation_path + '.atr') or os.path.exists(annotation_path + '.xml'):
        try:
            annotation = wfdb.rdann(annotation_path, 'atr')
        except:
            print(f"No annotation file found for {record_path}")

    signal_names = record.sig_name
    sample_frequency = record.fs
    recording_start_time = record.base_datetime if record.base_datetime else datetime.now()
    signals = record.p_signal

    with connection.cursor() as cursor:
        # Insert hospital
        hospital_id = insert_hospital(
            cursor,
            hospital_info['hospital_code'],
            hospital_info.get('hospital_name'),
            hospital_info.get('location')
        )

        # Insert patient
        patient_id = insert_patient(
            cursor,
            patient_info['patient_code'],
            patient_info.get('age'),
            patient_info.get('gender'),
            hospital_id
        )

        # Insert recording
        recording_code = record.record_name
        recording_id = insert_recording(
            cursor,
            patient_id,
            recording_code,
            recording_start_time,
            sample_frequency,
            len(signal_names)
        )

        # Insert ECG signals
        insert_ecg_signals(
            cursor,
            recording_id,
            recording_start_time,
            sample_frequency,
            signal_names,
            signals
        )

        # Insert annotations if available
        if annotation:
            insert_annotations(
                cursor,
                recording_id,
                recording_start_time,
                annotation,
                sample_frequency
            )

    connection.commit()
    print(f"Data from {record_path} has been inserted into TimescaleDB.")

def process_physionet_database(database_path, connection, hospital_info):
    record_list = wfdb.get_record_list(database_path)
    for record_name in record_list:
        record_path = os.path.join('physionet_databases', database_path, record_name)
        # Placeholder patient info
        patient_info = {
            'patient_code': 'Patient_' + record_name.split('/')[0],
            'age': None,
            'gender': None
        }
        process_and_store_ecg_data(record_path, connection, hospital_info, patient_info)

if __name__ == "__main__":
    conn = connect_to_db()

    # Hospital information
    hospital_info = {
        'hospital_code': 'H001',
        'hospital_name': 'PhysioNet Hospital',
        'location': 'Unknown'
    }

    # List of PhysioNet databases to process
    database_list = ['mitdb']  # Add more databases as needed

    for database_name in database_list:
        # Download the database if not already downloaded
        wfdb.dl_database(database_name, dl_dir='physionet_databases/' + database_name)
        # Process and store ECG data
        process_physionet_database(database_name, conn, hospital_info)

    conn.close()
