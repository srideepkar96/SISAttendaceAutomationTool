import requests
import pandas as pd
import json
from datetime import datetime

class Authorise:
    def __init__(self, endpoint, clientid, clientsecret):
        self.clientid = clientid
        self.clientsecret = clientsecret
        self.endpoint = endpoint

    def get_access_token(self):
        url = self.endpoint + "/oauth/access_token"
        headers = {"Accept": "*/*"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.clientid,
            "client_secret": self.clientsecret
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

class PowerQuery:
    def __init__(self, access_token, endpoint):
        self.access_token = access_token
        self.endpoint = endpoint

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_student_ids(self, csv_file):
        df = pd.read_csv(csv_file)
        return df['STUDENTS.ID'].tolist()

    def get_payload(self, att_date, schoolid, yearid, attendance_codeid, att_comment, studentid):
        return {
            "name": "Attendance",
            "record": [{
                "name": "attendance",
                "tables": {
                    "attendance": {
                        "att_mode_code": str("ATT_ModeDaily"),
                        "att_date": str(att_date),
                        "schoolid": str(schoolid),
                        "studentid": str(studentid),
                        "yearid": str(yearid),
                        "att_comment": str(att_comment),
                        "attendance_codeid": str(attendance_codeid)
                    }
                }
            }]
        }

    def get_schoolid(self):
        url = self.endpoint + "/ws/v1/school"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response.json()[0]["schoolid"]
    
    def get_attendance_codes(self, schoolid, att_date):
        url = self.endpoint + "ws/schema/query/com.pearson.core.attendance.attendance_code_by_school_date"
        headers = self.get_headers()
        payload = {
            "schoolid": schoolid,
            "att_date": att_date
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch attendance codes. Status code: {response.status_code}, Response: {response.text}")
        data = response.json()
        if not data.get("record"):
            raise ValueError("No attendance code records found.")
        yearid = data["record"][0]["tables"]["attendance_code"]["yearid"]
        att_code_dict = {
            rec["tables"]["attendance_code"]["att_code"]: rec["tables"]["attendance_code"]["attendance_codeid"]
            for rec in data["record"]
        }
        return yearid, att_code_dict

# --- Refactored functions for UI integration ---
def authenticate(endpoint, clientid, clientsecret):
    auth = Authorise(endpoint, clientid, clientsecret)
    access_token = auth.get_access_token()
    return access_token

def fetch_attendance_codes(access_token, endpoint, schoolid, att_date):
    ps = PowerQuery(access_token, endpoint)
    yearid, attendance_codeList = ps.get_attendance_codes(schoolid, att_date)
    return yearid, attendance_codeList

def fetch_student_ids(csv_file):
    df = pd.read_csv(csv_file)
    return df['STUDENTS.ID'].tolist()

def submit_attendance(access_token, endpoint, att_date, schoolid, yearid, attendance_codeid, att_comment, student_ids):
    ps = PowerQuery(access_token, endpoint)
    headers = ps.get_headers()
    endpoint_url = endpoint + "ws/attendance/daily_time"
    results = []
    for studentid in student_ids:
        payload = ps.get_payload(att_date, schoolid, yearid, attendance_codeid, att_comment, studentid)
        try:
            response = requests.post(endpoint_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            insert_count = data.get("insert_count", 0)
            update_count = data.get("update_count", 0)
            if insert_count > 0 or update_count > 0:
                action = "inserted" if insert_count > 0 else "updated"
                result = {
                    "studentid": studentid,
                    "status": "success",
                    "action": action,
                    "insert_count": insert_count,
                    "update_count": update_count,
                    "details": [
                        {"id": item['success_message'].get('id'), "status": item['status']} for item in data.get("result", [])
                    ]
                }
            else:
                result = {"studentid": studentid, "status": "failed", "reason": "No records inserted or updated"}
        except requests.RequestException as e:
            result = {"studentid": studentid, "status": "failed", "reason": str(e)}
        except Exception as ex:
            result = {"studentid": studentid, "status": "failed", "reason": str(ex)}
        results.append(result)
    return results

# The main() function and CLI code is removed for UI integration.
