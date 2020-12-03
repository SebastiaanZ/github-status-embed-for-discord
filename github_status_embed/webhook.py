from .types import WebhookPayload

json = """{
  "content": null,
  "embeds": [
    {
      "title": "[python-discord/sir-lancebot] Checks Successful on PR: #535 Refactor Advent of Code background tasks to account for deseasonification",
      "description": "Github Actions run [394929631](https://github.com/python-discord/sir-lancebot/actions/runs/394929631) succeeded.",
      "url": "https://github.com/python-discord/sir-lancebot/pull/535",
      "color": 2479397,
      "fields": [
        {
          "name": "PR Author",
          "value": "[Sebastiaan Zeeff](https://github.com/sebastiaanz)",
          "inline": true
        },
        {
          "name": "Workflow Run",
          "value": "[Lint #71](https://github.com/python-discord/sir-lancebot/actions/runs/394929631)",
          "inline": true
        },
        {
          "name": "Commit",
          "value": "[d9e98c3](https://github.com/python-discord/sir-lancebot/commit/d4c8c0f7184e5d494136cc2b7fc670e8ab7a8f93)",
          "inline": true
        }
      ]
    }
  ],
  "username": "Github Actions",
  "avatar_url": "https://raw.githubusercontent.com/github/explore/2c7e603b797535e5ad8b4beb575ab3b7354666e1/topics/actions/actions.png"
}"""


def create_webhook_payload(*args) -> WebhookPayload:
    """Create a webhook payload from the arguments provided."""
