import os
from utils import connect_to_db

def get_ecg_data(connection, recording_code, start_time=None, end_time=None, lead_name=None):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT recording_id, sampling_frequency FROM ecg_data.recordings WHERE recording_code = %s;
        """, (recording_code,))
        result = cursor.fetchone()
        if result is None:
            print(f"No recording found with code {recording_code}")
            return None
        recording_id, sampling_frequency = result

        query = """
            SELECT time, lead_value FROM ecg_data.ecg_signals
            WHERE recording_id = %s
        """
        params = [recording_id]

        if start_time:
            query += " AND time >= %s"
            params.append(start_time)
        if end_time:
            query += " AND time <= %s"
            params.append(end_time)
        if lead_name:
            query += " AND lead_name = %s"
            params.append(lead_name)

        query += " ORDER BY time ASC"

        cursor.execute(query, params)
        ecg_data = cursor.fetchall()

        cursor.execute("""
            SELECT annotation_time, annotation_type, annotation_description FROM ecg_data.annotations
            WHERE recording_id = %s
        """, (recording_id,))
        annotations = cursor.fetchall()

    return {
        'ecg_data': ecg_data,
        'annotations': annotations,
        'sampling_frequency': sampling_frequency
    }

if __name__ == "__main__":
    conn = connect_to_db()

    recording_code = '100'  # Replace with actual recording code
    lead_name = 'MLII'      # Replace with desired lead name

    data = get_ecg_data(conn, recording_code, lead_name=lead_name)

    if data:
        ecg_data = data['ecg_data']
        annotations = data['annotations']
        sampling_frequency = data['sampling_frequency']

        # Process ECG data
        times = [row[0] for row in ecg_data]
        values = [row[1] for row in ecg_data]

        # Plotting the ECG signal
        import matplotlib.pyplot as plt

        plt.figure(figsize=(15, 5))
        plt.plot(times, values)
        plt.title(f"ECG Signal - Recording {recording_code} - Lead {lead_name}")
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.show()

    conn.close()
