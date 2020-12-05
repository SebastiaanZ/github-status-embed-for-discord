import json
import logging
import typing

import requests

from github_status_embed import types


log = logging.getLogger(__name__)

EMBED_DESCRIPTION = "GitHub Actions run [{run_id}]({run_url}) {status_verb}."
PULL_REQUEST_URL = "https://github.com/{repository}/pull/{number}"
WEBHOOK_USERNAME = "GitHub Actions"
WEBHOOK_AVATAR_URL = (
    "https://raw.githubusercontent.com/"
    "SebastiaanZ/github-status-embed-for-discord/main/"
    "github_actions_avatar.png"
)


def get_payload_pull_request(
        workflow: types.Workflow, pull_request: types.PullRequest
) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a Pull Request."""
    fields = [
        types.EmbedField(
            name="PR Author",
            value=f"[{pull_request.pr_author_login}]({pull_request.author_url})",
            inline=True,
        ),
        types.EmbedField(
            name="Workflow Run",
            value=f"[{workflow.name} #{workflow.number}]({workflow.url})",
            inline=True,
        ),
        types.EmbedField(
            name="Source Branch",
            value=pull_request.source,
            inline=True,
        ),
    ]

    embed = types.Embed(
        title=(
            f"[{workflow.repository}] Checks {workflow.status.adjective} on PR: "
            f"#{pull_request.number} {pull_request.title}"
        ),
        description=EMBED_DESCRIPTION.format(
            run_id=workflow.id, run_url=workflow.url, status_verb=workflow.status.verb,
        ),
        url=PULL_REQUEST_URL.format(
            repository=workflow.repository, number=pull_request.number
        ),
        color=workflow.status.color,
        fields=fields,
    )

    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[embed]
    )
    return webhook_payload


def get_payload(workflow: types.Workflow) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a generic Workflow run."""
    embed_fields = [
        types.EmbedField(
            name="Actor",
            value=f"[{workflow.actor}]({workflow.actor_url})",
            inline=True,
        ),
        types.EmbedField(
            name="Workflow Run",
            value=f"[{workflow.name} #{workflow.number}]({workflow.url})",
            inline=True,
        ),
        types.EmbedField(
            name="Commit",
            value=f"[{workflow.short_sha}]({workflow.commit_url})",
            inline=True,
        ),
    ]

    embed = types.Embed(
        title=f"[{workflow.repository}] Workflow {workflow.status.adjective}",
        description=EMBED_DESCRIPTION.format(
            run_id=workflow.id, run_url=workflow.url, status_verb=workflow.status.verb,
        ),
        url=workflow.url,
        color=workflow.status.color,
        fields=embed_fields,
    )

    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[embed]
    )

    return webhook_payload


def send_webhook(
        workflow: types.Workflow,
        webhook: types.Webhook,
        pull_request: typing.Optional[types.PullRequest],
) -> bool:
    """Send an embed to specified webhook."""
    if pull_request is None:
        log.debug("Creating payload for non-Pull Request event")
        payload = get_payload(workflow)
    else:
        log.debug("Creating payload for Pull Request Check")
        payload = get_payload_pull_request(workflow, pull_request)

    log.debug("Generated payload:\n%s", json.dumps(payload, indent=4))

    response = requests.post(webhook.url, json=payload)

    log.debug(f"Response: [{response.status_code}] {response.reason}")
    if response.ok:
        print(f"[status: {response.status_code}] Successfully delivered webhook payload!")
    else:
        # Output an error message using the GitHub Actions error command format
        print(
            "::error::Discord webhook delivery failed! "
            f"(status: {response.status_code}; reason: {response.reason})"
        )

    return response.ok
