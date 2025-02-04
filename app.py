from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import smtplib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from decouple import config

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def fetch_google_sheet():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
        client = gspread.authorize(credentials)
        worksheet = client.open_by_url(config('GOOGLE_SHEET_URL')).get_worksheet(0)
        values = worksheet.get_all_values()
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        print("Error fetching Google Sheet:", e)
        return None
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_key = request.form.get('security_key')
        if entered_key == config('SECURITY_KEY'):
            session['authenticated'] = True  # Mark user as authenticated
            return redirect(url_for('index'))
        else:
            flash('Invalid security key.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')



@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    df = fetch_google_sheet()
    if df is None:
        flash('Error fetching Google Sheet.', 'danger')
        # Pass an empty default message if fetching fails
        return render_template('index.html', events=[], default_message='')
    
    events = df["Which event are you signing up for?"].unique().tolist()

    # Define the default email message with HTML formatting
    default_message = """
    <p>Greetings Team,</p>

    <p>We are excited to confirm your participation in the upcoming [Event Name] at [Event Location]. This event promises a day of [describe purpose or key experience], fostering [key takeaways such as teamwork, resilience, or skill development].</p>

    <p>Please review the finalized event details and itinerary below:</p>

    <p><strong>Event Details</strong><br>
    Event Location: [Event Location]<br>
    Date: [Event Date]<br>
    Transportation: [Mode of Transportation]<br>
    Dress Code: [Appropriate attire based on event type]</p>

    <p><strong>Itinerary</strong><br>
    [Time]: Accountability and load buses ([Location])<br>
    [Time]: Departure from [Starting Point]<br>
    [Time]: Rest stop (if applicable)<br>
    [Time]: Arrival at [Event Location]<br>
    [Time]: [Activity 1 - e.g., Training, briefing, free time]<br>
    [Time]: [Activity 2 - e.g., Lunch, guided session, group challenge]<br>
    [Time]: Departure from [Event Location]<br>
    [Time]: Rest stop (if applicable)<br>
    [Time]: Return to Camp Humphreys</p>

    <p><strong>Important Information</strong><br>
    Please bring sufficient [currency] for any additional costs such as [list examples like food purchases, etc].</p>

    <p>If you have any questions or concerns leading up to the event, feel free to contact us directly.</p>

    <p>Lastly, please follow us on Instagram(@2id_hhbn_umt) for future events and photos!

    <p>Thank you for your participation. We look forward to an engaging and memorable experience together!</p>

    <p>Warm Regards,<br>
    2ID HHBN UMT Office</p>

    <p><strong>Point of Contact:</strong><br>
    Battalion Chaplain: CH (CPT) Lee - jinsup.lee.mil@army.mil / 010-9573-9298<br>
    Religious Affairs NCOIC: SGT Cohen- stacey.d.cohen2.mil@army.mil / +1 (843) 480-2643<br>
    Religious Affairs KATUSA: SGT Lee - junseong.lee5.fm@army.mil / 010-7916-4165</p>
    """

    return render_template('index.html', events=events, default_message=default_message)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/send_emails', methods=['POST'])
def send_emails():
    event_name = request.form['event_name']
    participant_limit = int(request.form['participant_limit'])
    sender_email = config('SENDER_EMAIL')
    sender_password = config('SENDER_PASSWORD')
    subject = request.form['subject']
    message = request.form['message']
    file_path = request.files['file_path']

    df = fetch_google_sheet()
    if df is None:
        flash('Error fetching Google Sheet.', 'danger')
        return redirect(url_for('index'))

    df = df[df["Which event are you signing up for?"] == event_name]
    email_addresses = df['Email Address'].tolist()
    email_addresses = email_addresses[:participant_limit]

    for recipient_email in email_addresses:
        send_email(sender_email, sender_password, recipient_email, subject, message, file_path)
        print(f"Email sent to {recipient_email}")

    flash(f'Emails sent to {len(email_addresses)} participants.', 'success')
    return redirect(url_for('index'))

def send_email(sender_email, sender_password, recipient_email, subject, message, file_path):
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_name = "2ID HHBN UMT Office"

    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))

    if file_path:
        filename = file_path.filename
        file_path.save(f'./attachments/{filename}')
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(part)

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

@app.route('/data')
def data():
    if not session.get('authenticated'):
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    df = fetch_google_sheet()
    if df is None:
        flash('Error fetching Google Sheet.', 'danger')
        return render_template('data.html', data=[])
    return render_template('data.html', data=df.to_dict('records'))

@app.route('/edit/<int:row_id>', methods=['POST'])
def edit_row(row_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    new_data = request.form.to_dict()
    df = fetch_google_sheet()
    
    for col, val in new_data.items():
        df.at[row_id, col] = val
    
    save_to_google_sheet(df)  
    flash('Data edited successfully', 'success')
    return redirect(url_for('data'))

@app.route('/delete/<int:row_id>', methods=['POST'])
def delete_row(row_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    df = fetch_google_sheet()
    df.drop(row_id, inplace=True)
    
    save_to_google_sheet(df)  
    flash('Data deleted successfully', 'success')
    return redirect(url_for('data'))

def save_to_google_sheet(df):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
        client = gspread.authorize(credentials)
        worksheet = client.open_by_url(config('GOOGLE_SHEET_URL')).get_worksheet(0)  # Get the sheet (index starts from 0)
        worksheet.clear()  # Clear the current data
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())  # Update with new data
    except Exception as e:
        print("Error saving to Google Sheet:", e)


if __name__ == "__main__":
    app.run(debug=True)
