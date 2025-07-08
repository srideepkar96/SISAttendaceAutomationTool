# SIS Attendance Automation Tool

A modern, user-friendly web app for updating daily attendance for students in PowerSchool SIS.

---

## Features

- **Beautiful, centered UI** with SafeArrival branding
- **Authentication sidebar** for endpoint, client ID, and secret
- **Attendance code and school selection**
- **CSV upload** for student IDs
- **Downloadable sample CSV** (just below the upload box, only "sample CSV" is a clickable link)
- **Styled log window** (light gray, monospaced, scrollable) shows results after execution
- **Download logs as .txt** (Notepad) after execution completes
- **Logs include attendance code and all actions**

---

## Quickstart

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   streamlit run app.py
   ```

3. **Open the app**
   - The app will open in your browser (usually at [http://localhost:8501](http://localhost:8501))

---

## How to Use

1. **Authenticate**
   - Enter your Server Name, Client ID, and Client Secret in the sidebar
   - Click "Authenticate"

2. **Select Attendance Details**
   - Pick the attendance date, school, and attendance code

3. **Upload Students CSV**
   - Click "Upload Students CSV" and select your file
   - **Need a template?** Just below the upload box, click the light gray "sample CSV" link to download a reference file

4. **Submit Attendance**
   - Choose how many students to update
   - Click "Submit Attendance"

5. **View and Download Logs**
   - After execution, results appear in a light gray, scrollable log window
   - Click "Download Logs as Notepad File" to save the log as a `.txt` file

---

## Sample CSV Format

The CSV must have the following header:

```
STUDENTS.ID
```

Example:
```
STUDENTS.ID
12345
67890
```

You can download a sample file from the app by clicking the "sample CSV" link under the upload box.

---

## Support
For questions or help, contact the SafeArrival Team. 