import argparse
import pprint

parser = argparse.ArgumentParser(
    description="Send a custom GitHub Actions Status Embed to a Discord webhook.",
    epilog="Note: Make sure to keep your webhook token private!",
)

# pseudo-group: workflow
parser.add_argument("workflow_name")
parser.add_argument("run_id")
parser.add_argument("run_number")
parser.add_argument("status")
parser.add_argument("actor")

# pseudo-group: webhook
parser.add_argument("webhook_id")
parser.add_argument("webhook_token")

# pseudo-group: repository
parser.add_argument("repository_owner")
parser.add_argument("repository_name")

# pseudo-group: head_commit
parser.add_argument("short_sha")
parser.add_argument("branch")

# pseudo-group: pull_request
parser.add_argument("pr_author_login")
parser.add_argument("pr_number")
parser.add_argument("pr_title")
parser.add_argument("pr_source")


if __name__ == "__main__":
    args = parser.parse_args()
    pprint.pprint(vars(args), sort_dicts=False)
