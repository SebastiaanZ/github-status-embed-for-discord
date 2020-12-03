import json
import typing

from github_status_embed import types

EMBED_DESCRIPTION = "GitHub Actions run {run_id} {status_verb}."
PULL_REQUEST_URL = "https://github.com/{repository}/pull/{number}"
WEBHOOK_USERNAME = "GitHub Actions"
WEBHOOK_AVATAR_URL = (
    "https://raw.githubusercontent.com/"
    "SebastiaanZ/github-status-embed-for-discord/master/"
    "github_actions_avatar.png"
)


def get_payload_pull_request(
        workflow: types.Workflow, pull_request: types.PullRequest
) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a Pull Request."""
    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[
            types.Embed(
                title=(
                    f"[{workflow.repository}] Checks {workflow.status.adjective} on PR: "
                    f"#{pull_request.number} {pull_request.title}"
                ),
                description=EMBED_DESCRIPTION.format(
                    run_id=workflow.id, status_verb=workflow.status.verb
                ),
                url=PULL_REQUEST_URL.format(
                    repository=workflow.repository, number=pull_request.number
                ),
                color=workflow.status.color,
                fields=[
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
                ],
            )
        ]
    )
    return webhook_payload


def get_payload(workflow: types.Workflow) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a generic Workflow run."""
    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[
            types.Embed(
                title=(
                    f"[{workflow.repository}] Workflow Run {workflow.status.adjective}: "
                    f"{workflow.name} #{workflow.number}"
                ),
                description=EMBED_DESCRIPTION.format(
                    run_id=workflow.id, status_verb=workflow.status.verb
                ),
                url=workflow.url,
                color=workflow.status.color,
                fields=[
                    types.EmbedField(
                        name="Actor",
                        value=f"[{workflow.actor}]({workflow.actor})",
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
                ],
            )
        ]
    )
    return webhook_payload


def send_webhook(
    workflow: types.Workflow,
    webhook: types.Webhook,
    pull_request: typing.Optional[types.PullRequest],
) -> None:
    """Send a GitHub Status Embed to a Discord webhook."""

    if pull_request:
        payload = get_payload_pull_request(workflow, pull_request)
    else:
        payload = get_payload(workflow)

    print(json.dumps(payload, indent=4))
