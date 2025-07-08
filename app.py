# NOTE: The backend file 'InsertAtdSISR&DTry.py' should be renamed to 'InsertAtdSISR_and_DTry.py' for valid Python imports.
import streamlit as st
import pandas as pd
from datetime import datetime
from InsertAtdSISR_and_DTry import authenticate, fetch_attendance_codes, fetch_student_ids, submit_attendance
import io

st.set_page_config(page_title="SIS Attendance Automation Tool", layout="centered")

# Centered heading and subtitle
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0.2em;'>SIS Attendance Automation Tool</h1>
    <div style='text-align: center; color: #888; font-size: 1.1em; margin-bottom: 2em;'>Created with ❤️ By SafeArrival Team.</div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
This tool allows you to update daily attendance for students in PowerSchool SIS with a user-friendly interface.
""")

# Sidebar for authentication
def get_auth():
    st.sidebar.header("Authentication")
    endpoint = st.sidebar.text_input("Server Name", value="sisintstage11")
    clientid = st.sidebar.text_input("Client ID", value="83b8d802-a514-4c8e-8fa8-3d5f31b77850")
    clientsecret = st.sidebar.text_input("Client Secret", value="35d2e648-7614-4779-9509-daef4c206438", type="password")
    endpoint_url = f"https://{endpoint}.powerschool.com/" if not endpoint.startswith("http") else endpoint
    if st.sidebar.button("Authenticate"):
        try:
            access_token = authenticate(endpoint_url, clientid, clientsecret)
            st.session_state["access_token"] = access_token
            st.session_state["endpoint_url"] = endpoint_url
            st.sidebar.success("Authenticated successfully!")
        except Exception as e:
            st.sidebar.error(f"Authentication failed: {e}")

get_auth()

if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]
    endpoint_url = st.session_state["endpoint_url"]

    st.header("Attendance Details")
    att_date = st.date_input("Attendance Date", value=datetime.today()).strftime("%Y-%m-%d")

    # School selection (hardcoded for now, can be dynamic)
    schools = ["899020"]
    schoolid = st.selectbox("Select School", schools)

    # Fetch attendance codes
    if st.button("Fetch Attendance Codes") or "attendance_codes" not in st.session_state:
        try:
            yearid, attendance_codeList = fetch_attendance_codes(access_token, endpoint_url, schoolid, att_date)
            st.session_state["yearid"] = yearid
            st.session_state["attendance_codeList"] = attendance_codeList
            st.success("Attendance codes loaded.")
        except Exception as e:
            st.error(f"Failed to fetch attendance codes: {e}")

    if "attendance_codeList" in st.session_state:
        att_codes = list(st.session_state["attendance_codeList"].items())
        att_code_labels = [f"{code} (ID: {aid})" for code, aid in att_codes]
        selected_code_idx = st.selectbox("Select Attendance Code", range(len(att_codes)), format_func=lambda i: att_code_labels[i])
        attendance_codeid = att_codes[selected_code_idx][1]
        attendance_code_str = att_codes[selected_code_idx][0]
        yearid = st.session_state["yearid"]
    else:
        st.warning("Please fetch attendance codes.")
        st.stop()

    att_comment = st.text_area("Attendance Comment", value="**SM=SafeArrival: 2025-06-18 11:00 Change A to V (Vacation). FD reported by test@gmail.com on 2024-10-08 10:00 (Web02)**")

    st.header("Student Selection")
    uploaded_file = st.file_uploader("Upload Students CSV", type=["csv"])
    # Add a styled text link for sample CSV under the uploader
    sample_csv = "STUDENTS.ID\n12345\n67890\n"
    st.markdown(
        f"<span style='font-size: 0.9em; color: #aaa;'>* here is the </span>"
        f"<a href='data:text/csv;charset=utf-8,{sample_csv}' download='sample_students.csv' style='font-size: 0.9em; color: #aaa; text-decoration: underline;'>sample CSV</a>",
        unsafe_allow_html=True
    )
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        student_ids = df['STUDENTS.ID'].tolist()
        total_students = len(student_ids)
        options = list(range(0, min(100, total_students), 10))
        if total_students not in options:
            options.append(total_students)
        selected_count = st.selectbox("Number of students to update", options, format_func=lambda x: "All Students" if x == total_students else str(x))
        if selected_count == 0:
            st.warning("Please select at least one student.")
            st.stop()
        if selected_count == total_students:
            selected_students = student_ids
        else:
            selected_students = student_ids[:selected_count]
        st.write(f"Selected {len(selected_students)} students.")

        # Log string to collect output
        log_lines = []
        log_lines.append(f"Attendance Date: {att_date}\n")
        log_lines.append(f"School ID: {schoolid}\n")
        log_lines.append(f"Attendance Code: {attendance_code_str} (ID: {attendance_codeid})\n")
        log_lines.append(f"Attendance Comment: {att_comment}\n")
        log_lines.append(f"Total Students Selected: {len(selected_students)}\n")

        execution_complete = False
        results = None

        if st.button("Submit Attendance"):
            with st.spinner("Submitting attendance records..."):
                results = submit_attendance(
                    access_token,
                    endpoint_url,
                    att_date,
                    schoolid,
                    yearid,
                    attendance_codeid,
                    att_comment,
                    selected_students
                )
            st.success("Attendance submission complete!")
            execution_complete = True
            for res in results:
                if res["status"] == "success":
                    log_lines.append(f"✅ Student ID {res['studentid']}: {res['insert_count']} record(s) inserted.\n")
                    for detail in res.get("details", []):
                        log_lines.append(f"    - ID: {detail['id']}, Status: {detail['status']}\n")
                else:
                    log_lines.append(f"❌ Student ID {res['studentid']}: {res.get('reason', 'Unknown error')}\n")

            # Show logs in a light gray, scrollable box
            log_text = "".join(log_lines)
            st.markdown(
                f"""
                <div style='background-color: #f5f5f5; color: #222; border-radius: 8px; padding: 1em; margin-top: 1em; font-family: monospace; max-height: 350px; overflow-y: auto; border: 1px solid #ddd;'>
                <pre style='margin: 0; font-size: 1em;'>{log_text}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Download button for logs
            st.download_button(
                label="Download Logs as Notepad File",
                data=log_text,
                file_name="attendance_log.txt",
                mime="text/plain"
            )
    else:
        st.info("Please upload a Students_export.csv file.")
else:
    st.info("Please authenticate in the sidebar to begin.") 