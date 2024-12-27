# 2ID UMT Event Management Automation
![image](https://github.com/user-attachments/assets/ce5bdaf9-8b52-45ed-bd94-658262507918)

## Overview
A web application for the 2ID HHBN UMT Office.

## Problem Statement
The manual process of hand-registering participants on paper rosters and sending emails to event participants was time-consuming, prone to errors, and inefficient. Coordinating communications for large groups required significant effort and often led to delays. There was a clear need for a streamlined solution to improve the efficiency and timeliness of our communication processes.

## Solution
This web application was designed to automate the process of managing event rosters, sending mass emails to event participants all in one page. It uses Flask for WSGI application, Google API for fetching participant data, SMTP library for email communication. The application was deployed on AWS EC2 instance with Nginx serving as a reverse proxy to forward requests to Gunicorn WSGI server, where the application runs.

## Benefits
- **Increased Efficiency**: Automating the email sending process significantly reduces the time and effort required to communicate with event participants.
- **Error Reduction**: Automated data fetching and validation reduce the likelihood of errors in email communication.
- **Timeliness**: Ensures timely dissemination of information, improving communication effectiveness.

-----

# Steps to Run on a Local Environment
1. Install dependencies:
> pip install requirements.txt
2. Set environment variables: Create a .env file in the root directory and include the necessary credentials, such as:
```
GOOGLE_SHEET_URL=<your_google_sheet_url>
ENDER_EMAIL=<your_sender_email>
SENDER_PASSWORD=<your_sender_email_password>
```
3. Configure OAuth credentials: Place your service account JSON key file (<u>service_account.json</u>) in the root directory.
4. Run the Flask app:
> python app.py
5. Access the web application: Open your web browser and go to http://127.0.0.1:5000/ or simply use localhost



