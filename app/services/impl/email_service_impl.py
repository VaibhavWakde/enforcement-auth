from app.services.interfaces.email_service import EmailService


class EmailServiceImpl(EmailService):

    def send_login_otp(
        self,
        email: str,
        otp: str
    ):

        print(f"Sending OTP {otp} to {email}")

    def send_forgot_password_otp(
        self,
        email: str,
        otp: str
    ):

        print(f"Sending Forgot Password OTP {otp} to {email}")