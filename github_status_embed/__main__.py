import argparse
import importlib.resources
import logging
import pathlib
import sys

import yaml

from github_status_embed.webhook import send_webhook
from .log import setup_logging
from .types import MissingActionFile, PullRequest, Webhook, Workflow


log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Send an enhanced GitHub Actions Status Embed to a Discord webhook.",
    epilog="Note: Make sure to keep your webhook token private!",
)

# Auto-generate arguments from `action.yaml` to ensure they are in
# synchronization with each other. This also takes the description
# of each input argument and adds it as a `help` hint.
#
# The `action.yaml` file may be located in two different places,
# depending on whether the application is run in distributed form
# or directly from the git repository.
try:
    # Distributed package location using `importlib`
    action_specs = importlib.resources.read_text('github_status_embed', 'action.yaml')
except FileNotFoundError:
    # The GitHub Actions marketplace requires it to be located in the
    # root of the repository, so if we're running a non-distributed
    # version, we haven't packaged the filed inside of the package
    # directly yet and we have to read it from the repo root.
    action_file = pathlib.Path(__file__).parent.parent / "action.yaml"
    try:
        action_specs = action_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise MissingActionFile("the `action.yaml` can't be found!") from None

# Now that we've loaded the specifications of our action, extract the inputs
# and their description to register CLI arguments.
action_specs = yaml.safe_load(action_specs)
for argument, configuration in action_specs["inputs"].items():
    parser.add_argument(argument, help=configuration["description"])


if __name__ == "__main__":
    arguments = vars(parser.parse_args())
    debug = arguments.pop('debug') not in ('', '0', 'false')
    dry_run = arguments.pop('dry_run') not in ('', '0', 'false')

    # Set up logging and make sure to mask the webhook_token in log records
    level = logging.DEBUG if debug else logging.WARNING
    setup_logging(level, masked_values=[arguments['webhook_token']])

    # If debug logging is requested, enable it for our application only
    if debug:
        output = "\n".join(f"  {k}={v!r}" for k, v in arguments.items())
        log.debug("Received the following arguments from the CLI:\n%s", output)

    # Extract Action arguments by creating dataclasses
    workflow = Workflow.from_arguments(arguments)
    webhook = Webhook.from_arguments(arguments)
    if arguments.get("pull_request_payload", False):
        log.warning("The use of `pull_request_payload` is deprecated and will be removed in v1.0.0")
        pull_request = PullRequest.from_payload(arguments)
    else:
        pull_request = PullRequest.from_arguments(arguments)

    # Send webhook
    success = send_webhook(workflow, webhook, pull_request, dry_run)

    if not success:
        log.debug("Exiting with status code 1")
        sys.exit(1)
