# Attendance SMS Sender 2026

This project integrates the **Africa's Talking API** to send automated SMS alerts to parents regarding their children's school attendance.

## Features
- Batch process attendance from CSV files.
- Automatic message formatting for 'Absent' vs 'Late' statuses.
- Full logging of API responses and delivery statuses.
- Environment variable support for secure API key management.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your credentials:
   ```env
   AT_USERNAME=your_username
   AT_API_KEY=your_api_key
   AT_SENDER_ID=your_sender_id_optional
   ```
3. Prepare an `attendance.csv` file with the following headers:
   `student_name,parent_phone,status`

## Usage
Run the script directly:
```bash
python sms.py
```

## CSV Example
```csv
student_name,parent_phone,status
Jane Smith,+254711223344,absent
John Doe,+254722334455,present
```