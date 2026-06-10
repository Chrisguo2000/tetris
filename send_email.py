import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage


REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "MAIL_FROM",
    "MAIL_TO",
]


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_message() -> EmailMessage:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    repository = os.getenv("GITHUB_REPOSITORY", "unknown repository")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server_url}/{repository}/actions/runs/{run_id}" if run_id else ""

    subject = os.getenv("EMAIL_SUBJECT", "GitHub Actions weekly email")
    body = os.getenv(
        "EMAIL_BODY",
        (
            "每周定时邮件已发送成功。\n\n"
            f"运行时间: {now}\n"
            f"仓库: {repository}\n"
            f"运行链接: {run_url}\n"
        ),
    )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = require_env("MAIL_FROM")
    message["To"] = require_env("MAIL_TO")
    message.set_content(body)
    return message


def send_email(message: EmailMessage) -> None:
    host = require_env("SMTP_HOST")
    port = int(require_env("SMTP_PORT"))
    username = require_env("SMTP_USERNAME")
    password = require_env("SMTP_PASSWORD")

    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(username, password)
            server.send_message(message)


def main() -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

    send_email(build_message())
    print("Weekly email sent successfully.")


if __name__ == "__main__":
    main()
