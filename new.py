import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import pytz
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import uuid
from datetime import datetime, time

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1taMCHQRCV7YLn7VSEQyTKr4qeKhO8HEl-b9KpB0VXRM"
SHEET_NAME = "classroom"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

def header2(url): 
    st.markdown(f'<p style="color:#1261A0;font-size:40px;border-radius:2%;"><center><strong>{url}</strong></center></p>', unsafe_allow_html=True)

def get_data(gsheet_connector,date, email) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:F",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]

    df["Date"] = pd.to_datetime(df["Date"])  # Assuming your date column is named "Date"
    df = df[(df["Date"].dt.date == date)  & (df["Woxsen mail id"] == email)]

    return df


def add_row_to_gsheet(gsheet_connector, row, date_selected) -> None:
    row_with_date = [date_selected] + row[0] 
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:F",
            body=dict(values=[row_with_date]),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )

@st.cache_resource()
def connect_to_gsheet():
    cred = {
  "type": "service_account",
  "project_id": "classroomproject-407309",
  "private_key_id": "d3004078af14524bbc903cef774dc7ec4822c3d2",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDkA+7KDM402yeD\nvL3g8FvXXIhFYOjOYvx8viURWB3p+JCRtqLNei1GZCB0Xf8jvlrCZMLs4pgpYCCs\neG4wZI8LYQk9av8izalbMjLC181rTrgB5QE/jJZ9+44+XxYDzDFW8VexBZOwtrNI\nHy+NQd69YM/ZDXvZcnQo2XIDHLJV+cKsygvzfJqgreXbjOxlv2xLLPylvH9IUmcY\nL2R5i76oa/+PUBth4k1iSqkvTX8QJwdYPg3gGUvPnlGGyDIdC5MsygnkQ8Vg240A\nSGy2wU37pWq0FEt67deOWJ9MCDWKciaTjYbJecpxbW8GiRmkmAOnu8IzZcpwYZnu\n0H3Eq0ydAgMBAAECggEARO37bhFY9RmbZHPWYv3GheBvQan+NwYtlfhVdFzTDjwa\nWDKCHOPmc/Uo6oTP8JpHDaUwWDRYE4n/1qPBi9eadrIq/OovnvHVVMBkIArlCp+N\neOUl73QsuoEliy1rllJQSBxFijpJX46bvB3RXj6fe1ic/Nzap+21t/OkR9SRBPQe\nFB/ChomZm2gjckW9U8OpAwTEkzyxd8lOCK2ERhWrJhDDH285rgIxOWZXvrr7qLdT\nGQ8D3yCJNTfEpSmggxpNBtuHOGAMVO9Y8c+vydJd7MoMI5+wNqNtdZXaVeXqF+zp\n7K1BT8IMfb+88ZugK74sTQQhypwnKPafy62+QcX6cQKBgQD0Op6jOhSX74bQJjaA\nI7JfbvRkrCJDthRXUfYbTWrN3WghzGtJnQU0Q3O+SN4wJuR1p6HKQSYZ/gMuQugR\nrW34NlkV2Psf9bgjUjKcUifEuW5taqyypsXmP55W6ynfZ4iIjAgfsZHdFjRZQMbm\nQ3da+a0Tuw1L5L8nXroRs6kJDwKBgQDvAUOQVm0gI9IuBW9xqmRWbSAMUd2R+9o7\nlArpTN9V16Cqb0mXqH1ixy+Yf8BfWeWJd4WdHPRuRL/cwO0Gylby9/wQk28KJDrA\nIq4pyjzrHGGRCPRkLrbaS1NGG4C7x1aMEucQMkYlsk+Imd61U2aJoI/O5LSt0tWo\ni3e4uQlXkwKBgQDwCV05WDA9VDHQCn6uWmdJ3Kde+r+ChUZgvDGCjAhY5S8faOZZ\np3Yh89miP8QA13jbGjKtsnJcQYemxCOKnEXlGqVcD7JhqwOb04Himex0MTwTVjD+\nNWNz9TsOenrhE8ThT5/8Zm3SOayhvETAs7ZvN82gAswCt4QYkcWW+Fk+iQKBgCUH\nwxoX6exy4Fu1B+FKjyU83xxJitTVeqiEdXRULr40HHaLq5FNz6+AQQWVtY6QdRnp\nZNBE7jIvgLKJSbAlpXcbqPhAf5HIrzmZpfZfmTSsPwmjo4nqGvaTeSGBnV56shQd\n0aMWxvuMNvppLLJXa6mjMOTTVpMf+W6VvUTnlmT1AoGBAMyL1ZC6tZpcvN80Xtd+\nIl22PEVJaIndeUfYPcwlZQW/5mqZGSfo4BF0GoQSum2luAg/lKGEFgju2db8ovKs\nxG5VsOzp0tFJfpDKhATSHTxnJvhCrntjgXz4SXF5I/+PDw2SJxqizIMQZgN8OKtS\nXyI/nyxs5U3Cvhj179fPMdch\n-----END PRIVATE KEY-----\n",
  "client_email": "classroom@classroomproject-407309.iam.gserviceaccount.com",
  "client_id": "107858984435990495551",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/classroom%40classroomproject-407309.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(cred,
        scopes=[SCOPE],
    )

    service = build("sheets", "v4", credentials=credentials)
    gsheet_connector = service.spreadsheets()
    return gsheet_connector





def send_email_notification(name, mail_id, sport_type, slot_time,sport_type1,slot_time1,Classroom):
 
   
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    smtp_username = "airesearchcentre@woxsen.edu.in"
    smtp_password = "Mar00265"
    recipient_email = "rizwan.zhad@woxsen.edu.in"

    # Email content
    
    

    subject = f"Slot Approval: {name} has booked a slot"
    body = f"Dear Subha Minz,\n\n{name} has booked a slot for {Classroom} at {slot_time} or {slot_time1}. Please review and approve the slot.\n\nBest regards,\nAI Reseach Centre Woxsen University"

    # Create MIMEText and MIMEMultipart objects
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
        
    # Connect to the SMTP server and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient_email, msg.as_string())
        st.success("Email notification sent successfully.")
        
    except Exception as e:
        st.error(f"Failed to send email notification: {e}")
    finally:
        server.quit()


def slot_main():
    col1, col2, col3 = st.columns([0.4, 1, 0.2])
    with col2:
        st.image("Logo.png", width=300)

    col1, col2, col3 = st.columns([0.2, 2, 0.2])
    with col2:
        st.title("BOOKINGS FOR SESSION")

    gsheet_connector = connect_to_gsheet()

    UTC = pytz.utc
    IST = pytz.timezone('Asia/Kolkata')

    current_time = datetime.now(IST).time()

    hr = str(datetime.now(IST).time())

    if int(hr[0:2]) == 22 or int(hr[0:2]) == 23:
        header2("Booking opens at 12AM")
    else:
        mail_id = st.text_input("Enter your woxsen Mail ID")

        if len(mail_id) == 0 or "woxsen.edu.in" in mail_id:
            name = st.text_input("Enter your Name")
            contact = st.text_input("Enter your contact")
            date = st.date_input("Select Date", datetime.now().date())
            date_today = datetime.now().date()

            if date < date_today:
                st.error("Please select a date starting from today.")
            else:
                time_df = None  # Initialize time_df

                if len(name) != 0 and len(contact) != 0 and len(mail_id) != 0:
                    games = ["Select Your Classroom", "LT1 (122 Seats)", "LT2 (102 Seats)", "LT3 (68 Seats)", "LT5 (68 Seats)",
                             "LT6 (40)", "19 (80 Seats)", "20 (80 Seats)", "21 (80 Seats)", "22 (80 Seats)", "118 (80 Seats)",
                             "119 (80 Seats)", "120 (80 Seats)", "121 (80 Seats)"]
                    Classroom = st.selectbox("Classroom", games)
                    if Classroom != "Select Your Classroom":
                        df_email = get_data(gsheet_connector, date, mail_id)

                        if len(df_email) < 2:  # Allowing maximum 2 bookings per email
                            df = get_data(gsheet_connector, date, mail_id)
                            time_df = df[df["Classroom"] == Classroom]

                        else:
                            st.error("Maximum booking limit reached for this email ID")
                            return

                if time_df is not None:  # Check if time_df has been assigned a value
                    booked = list(time_df["Slot Timing"])

                    all_slots = []

                    # Define the time intervals for different slots
                    time_intervals = [
                                        ("09:00 - 10:30", "09:00", "10:30"),
                                        ("10:45 - 12:15", "10:45", "12:15"),
                                        ("12:45 - 14:15", "12:45", "14:15"),
                                        ("15:00 - 16:30", "15:00", "16:30"),
                                        ("16:45 - 18:15", "16:45", "18:15"),
                                        ("18:30 - 20:00", "18:30", "20:00")
                                    ]
                    def convert_to_datetime(time_str):
                            return datetime.strptime(time_str, "%H:%M")

                    time_intervals = [(interval[0], convert_to_datetime(interval[1]), convert_to_datetime(interval[2])) for interval in time_intervals]

                        # Display formatted time intervals
                    for interval in time_intervals:
                            slot_time = "{} - {}".format(interval[1].strftime("%H:%M"), interval[2].strftime("%H:%M"))
                            print(f"Time Interval: {interval[0]}, Slot Time: {slot_time}")
                            IST = pytz.timezone('Asia/Kolkata')
                    hr = str(datetime.now(IST).time())

                    if int(hr[0:2]) == 23:
                        header2("Booking opens at 12AM")
                    else:
                        for interval in time_intervals:
                            slot_time = "{} - {}".format(interval[1].strftime("%H:%M"), interval[2].strftime("%H:%M"))

                            if slot_time not in booked:
                                all_slots.append(slot_time)

                        if len(all_slots) == 0:
                            header2("No Slots Available")
                        else:
                            # Fetch already booked slots for the selected date and classroom
                            booked_slots = list(time_df["Slot Timing"])

                            # Filter out already booked slots from available slots
                            available_slots = [slot for slot in all_slots if slot not in booked_slots]

                            slot_time1 = st.selectbox("Choose your time slot", ["Select Slot"] + available_slots)

                            if slot_time1 != "Select Slot":
                                if st.button("Submit"):
                                    add_row_to_gsheet(
                                        gsheet_connector, [[name, mail_id, contact, Classroom, slot_time1]],
                                        date.strftime("%Y-%m-%d")
                                    )
                                    header2("Your slot has been booked!")
                                    st.success(" **Take a Screenshot of the slot details** ")
                                    st.write("**Name:**", name)
                                    st.write("**Classroom:**", Classroom)
                                    st.write("**Slot Time:**", slot_time1)

                                    send_email_notification(name, mail_id, "", "", "", slot_time1, Classroom)

                        st.button("Refresh", key="Refresh_button")

        else:
            st.error("You are not allowed to book a slot. Please enter Woxsen mail ID")



if __name__ == "__main__":
    st.set_page_config(page_title="Classroom: Booking", layout="centered")
    slot_main()


