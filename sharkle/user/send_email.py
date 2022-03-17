import json
import logging

from rest_framework.decorators import action

from user.models import VerificationCode
import boto3
from botocore.exceptions import ClientError, WaiterError
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

# ref: aws-doc-sdk-examples/python/example_code/ses/ses_email.py
class SesMailSender:
    def __init__(self, ses_client):
        self.ses_client = ses_client

    def to_service_format(self, destination):
        """
        :return: The destination data in the format expected by Amazon SES.
        """
        return {"ToAddresses": [destination]}

    def send_email(self, source, destination, subject, text, html, reply_tos=None):
        """
        Sends an email.
        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified. 저희.. aws 한테 리젝당해서 아직 sandbox ㅠㅠ
        :param source: The source email account.
        :param destination: The destination email account.
        :param subject: The subject of the email.
        :param text: The plain text version of the body of the email.
        :param html: The HTML version of the body of the email.
        :param reply_tos: Email accounts that will receive a reply if the recipient
                          replies to the message.
        :return: The ID of the message, assigned by Amazon SES.
        """

        send_args = {
            "Source": source,
            "Destination": self.to_service_format(destination),
            "Message": {
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
            },
        }
        if reply_tos is not None:
            send_args["ReplyToAddresses"] = reply_tos
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response["MessageId"]
            logger.info("Sent mail %s from %s to %s.", message_id, source, destination)
        except ClientError:
            logger.exception("Couldn't send mail from %s to %s.", source, destination)
            raise
        else:
            return message_id


class EmailSendView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # TODO Validation
        destination_email = request.data.get("email")
        verification_code = VerificationCode(email=destination_email)
        verification_code.save(update_fields=["code"])
        code = verification_code.code

        ses_client = boto3.client("ses")
        ses_mail_sender = SesMailSender(ses_client)
        service_email = "sharkle.snu@gmail.com"
        message_text = "안녕하세요. sharkle 회원가입을 위한 이메일 인증을 완료해주세요."
        message_html = f"<p>인증번호는 <b>{code}</b>입니다.</p>"

        try:
            ses_mail_sender.send_email(
                service_email,
                destination_email,
                "[샤클] 회원가입 인증번호 메일입니다. ",
                message_text,
                message_html,
            )
        except ClientError:
            return Response(
                status=status.HTTP_409_CONFLICT, data={"detail": "메일 발송에 실패했습니다."}
            )

        return Response({"message": "email sent to user"}, status=status.HTTP_200_OK)


class EmailViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    # POST /email/send/
    @action(detail=False, methods=["post"])
    def send(self, request):
        # TODO Validation
        destination_email = request.data.get("email")
        verification_code = VerificationCode(email=destination_email)
        verification_code.save(update_fields=["code"])
        code = verification_code.code

        ses_client = boto3.client("ses")
        ses_mail_sender = SesMailSender(ses_client)
        service_email = "sharkle.snu@gmail.com"
        message_text = "안녕하세요. sharkle 회원가입을 위한 이메일 인증을 완료해주세요."
        message_html = f"<p>인증번호는 <b>{code}</b>입니다.</p>"

        try:
            ses_mail_sender.send_email(
                service_email,
                destination_email,
                "[샤클] 회원가입 인증번호 메일입니다. ",
                message_text,
                message_html,
            )
        except ClientError:
            return Response(
                status=status.HTTP_409_CONFLICT, data={"detail": "메일 발송에 실패했습니다."}
            )
        return Response({"message": "email sent to user"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def verify(self, request):
        # TODO validation
        email = request.data.get("email")
        code = request.data.get("code")
        is_verified = VerificationCode.check_email_code(email, code)
        # TODO integrate signup logic
        return Response({"verified": is_verified}, status=status.HTTP_200_OK)
