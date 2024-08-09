import json
import requests
from django.http import JsonResponse

def send_email_via_api(to_email, subject, message):
    url = "https://cashfreeapi.snssystem.com/api/v1/send-message"
    token = "a1JfX6rUsKcjnvEopok8"

    body = {
        'token': token,
        'to': to_email,
        'subject': subject,
        'message': message,
        # Add attachments if required
        # 'attachments[]': ('path_to_attachment')
    }
    try:
        response = requests.post(url, data=body)
        response.raise_for_status()
        return {"success":True}
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None  # Return None if there's an error or no response


def send_test_email(request):
    to_email = "piyush.jain@snssystem.com"
    subject = "sns subject12"
    message = "This is for testing1"
    attachments = []  # List of file paths
    # Call the function to send the email
    response = send_email_via_api(to_email, subject, message, attachments)
    # Return the API response as a JSON response
    return JsonResponse(response)

def upload_file_to_s3(file_path, file_type="public"):
    url = "https://cashfreeapi.snssystem.com/api/v1/file-upload"
    token = "Hj5p6dGJpMTkzNX4PMfAxW"

    # Prepare the payload for the POST request
    payload = {
        'token': token,
        'type': file_type
    }

    # Prepare the file to be uploaded
    files = {
        'attachments': open(file_path, 'rb')
    }

    # Perform the POST request
    response = requests.post(url, data=payload, files=files)

    # Close the opened file handle
    files['attachments'].close()

    # Return the response from the API
    return response.json()  # Assuming the response is JSON, adjust accordingly
