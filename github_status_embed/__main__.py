import argparse

from .types import Workflow, Webhook, PullRequest
from .webhook import send_webhook

parser = argparse.ArgumentParser(
    description="Send a custom GitHub Actions Status Embed to a Discord webhook.",
    epilog="Note: Make sure to keep your webhook token private!",
)

# pseudo-group: workflow
parser.add_argument("workflow_name")
parser.add_argument("run_id")
parser.add_argument("run_number")
parser.add_argument("status")
parser.add_argument("repository")
parser.add_argument("actor")
parser.add_argument("ref")
parser.add_argument("sha")

# pseudo-group: webhook
parser.add_argument("webhook_id")
parser.add_argument("webhook_token")

# pseudo-group: pull_request
parser.add_argument("pr_author_login")
parser.add_argument("pr_number")
parser.add_argument("pr_title")
parser.add_argument("pr_source")


if __name__ == "__main__":
    arguments = vars(parser.parse_args())

    # Extract Action arguments by creating dataclasses
    workflow = Workflow.from_arguments(arguments)
    webhook = Webhook.from_arguments(arguments)
    pull_request = PullRequest.from_arguments(arguments)

    send_webhook(workflow, webhook, pull_request)
