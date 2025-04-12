from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.views import exception_handler
from django.shortcuts import render
import requests
import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from article39_backend.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from weasyprint import HTML


# This function is used to send HTML emails with optional attachments.
class EmailThread(threading.Thread):
    def __init__(
        self, subject, html_content, recipient_list, sender, images=None, pdfs=None
    ):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        self.images = images
        self.pdfs = pdfs
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, None, self.sender, self.recipient_list)

        # Attaching images
        if self.images is not None:
            for image in self.images:
                if isinstance(image, tuple):
                    attachment_name, attachment_content, attachment_mime_type = image
                    msg.attach(
                        attachment_name, attachment_content, attachment_mime_type
                    )

        # Attaching PDFs
        if self.pdfs is not None:
            for pdf in self.pdfs:
                pdf_data = HTML(string=pdf["content"]).write_pdf()
                msg.attach(pdf["name"], pdf_data, "application/pdf")

        msg.content_subtype = "html"
        msg.body = self.html_content
        msg.send()
        print("Email sent successfully!")


def send_html_mail(
    subject, html_content, recipient_list, sender, images=None, pdfs=None
):
    EmailThread(subject, html_content, recipient_list, sender, images, pdfs).start()


def send_login_credentials(
    username,
    email,
    password,
):
    html_content = render_to_string(
        "artists_emails/login_credentials.html",
        {
            "user_name": username,
            "user_email": email,
            "user_password": password,
        },
    )
    subject = "Your login credentials - 1972 Art. 39"

    EmailThread(
        subject,
        html_content,
        [email],
        EMAIL_HOST_USER,
    ).start()


def send_song_status_update(
    song_title: str,
    user_name: str,
    status: str,
    email: str,
):
    html_content = render_to_string(
        "artists_emails/song_status_update.html",
        {
            "song_title": song_title,
            "user_name": user_name,
            "song_status": status,
        },
    )
    subject = f"Song Status Update - {song_title}"

    EmailThread(
        subject,
        html_content,
        [email],
        EMAIL_HOST_USER,
    ).start()


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        # Extract all error messages into a plain string
        plain_errors = []
        for field, messages in response.data.items():
            if isinstance(messages, list):
                for message in messages:
                    plain_errors.append(f"({field}) " + str(message))
            else:
                plain_errors.append(f"({field}) " + str(messages))

        response.data = {"success": False, "message": "\n".join(plain_errors)}

    return response


# file upload
class UploadFile(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"success": False, "message": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = "https://transfer.ongshak.com/upload/"
        params = {
            "key": settings.TRANSFER_ONGSHAK_API_KEY,
            "path": "article39",
        }

        # if file size exceeds 20MB, return error
        if file.size > 20 * 1024 * 1024:
            return Response(
                {"success": False, "message": "File size exceeds 20MB"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # if file size is an image, and greater than 2MB, set compression level to 50
        if file.size > 2 * 1024 * 1024 and file.name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            params["compression_level"] = "50"

        response = requests.post(url, params=params, files={"file": file})
        return Response(
            {
                "success": True,
                **response.json(),
            },
            status=status.HTTP_201_CREATED,
        )
