# GitHub Actions Status Embed for Discord
_Send enhanced and informational GitHub Actions status embeds to Discord webhooks._

## Why?

The default status embeds GitHub delivers for workflow runs are very basic: They contain the name of repository, the result of the workflow run (but not the name!), and the branch that served as the context for the workflow run. If the workflow was triggered by a pull request from a fork, the embed does not even differentatiate between branches on the fork and the base repository: The "master" branch in the example below actually refers to the "master" branch of a fork!

Another problem occurs when multiple workflows are chained: Github will send an embed to your webhook for each individual run result. While this is sometimes what you want, if you chain multiple workflows, the number of embeds you receive may flood your log channel or trigger Discord ratelimiting. Unfortunately, there's no finetuning either: With the standard GitHub webhook events, it's all or nothing.

## Solution

As a solution to this problem, I decided to write a new action that sends an enhanced embed containing a lot more information about the workflow run. The design was inspired by both the status embed sent by Azure as well as the embeds GitHub sends for issue/pull request updates. Here's an example:

<p align="center">
  <img src="https://raw.githubusercontent.com/SebastiaanZ/github-status-embed-for-discord/main/img/embed_comparison.png" title="Embed Comparison">
  Comparison between a standard and an enhanced embed as provided by this action.
</p>

As you can see, the standard embeds on the left don't contain a lot of information, while the embed on the right shows the information you'd typically want for a check run on a pull request. While it would be possible to include even more information, there's also obviously a trade-off between the amount of information and the vertical space required to display the embed in Discord.

Having a custom action also lets you deliver embeds to webhooks when you want to. If you want, you can only send embeds for failing jobs or only at the end of your sequence of chained workflows.

## General Workflow Runs & PRs

When a workflow is triggered for a Pull Request, it's natural to include a bit of information about the Pull Request in the embed to give context to the result. However, when a workflow is triggered for another event, there's no Pull Request involved, which also means we can't include information about that non-existant PR in the embed. That's why the Action automatically tailores the embed towards a PR if PR information is provided and tailors it towards a general workflow run if not.

Spot the difference:

<p align="center">
  <img src="https://raw.githubusercontent.com/SebastiaanZ/github-status-embed-for-discord/main/img/type_comparison.png" title="Type Comparison">
</p>

## Usage

To use the workflow, simply add it to your workflow and provide the appropriate arguments.

### Example workflow file

```yaml
on:
  push:
    branches:
      - main
  pull_request:

jobs:
  send_embed:
    runs-on: ubuntu-latest
    name: Send an embed to Discord

    steps:
    - name: Run the GitHub Actions Status Embed Action
      uses: SebastiaanZ/github-status-embed-for-discord@main
      with:
        # Discord webhook
        webhook_id: '1234567890'  # Has to be provided as a string
        webhook_token: ${{ secrets.webhook_token }}

        # Optional arguments for PR-related events
        # Note: There's no harm in including these lines for non-PR
        # events, as non-existing paths in objects will evaluate to
        # `null` silently and the github status embed action will
        # treat them as absent.
        pr_author_login: ${{ github.event.pull_request.user.login }}
        pr_number: ${{ github.event.pull_request.number }}
        pr_title: ${{ github.event.pull_request.title }}
        pr_source: ${{ github.event.pull_request.head.label }}
```

### Command specification

**Note:** The default values assume that the workflow you want to report the status of is also the workflow that is running this action. If this is not possible (e.g., because you don't have access to secrets in a `pull_request`-triggered workflow), you could use a `workflow_run` triggered workflow that reports the status of the workflow that triggered it. See the recipes section below for an example.

| Argument | Description | Default |
| --- | --- | :---: |
| status | Status for the embed; one of ["succes", "failure", "cancelled"] | (required) |
| webhook_id | ID of the Discord webhook (use a string) | (required) |
| webhook_token | Token of the Discord webhook | (required) |
| workflow_name | Name of the workflow | github.workflow |
| run_id | Run ID of the workflow | github.run_id |
| run_number | Run number of the workflow  | github.run_number |
| actor | Actor who requested the workflow | github.actor |
| repository | Repository; has to be in form `owner/repo` | github.repository |
| ref | Branch or tag ref that triggered the workflow run | github.ref |
| sha | Full commit SHA that triggered the workflow run. | github.sha |
| pr_author_login | **Login** of the Pull Request author | (optional)¹ |
| pr_number | Pull Request number | (optional)¹ |
| pr_title | Title of the Pull Request | (optional)¹ |
| pr_source | Source branch for the Pull Request | (optional)¹ |
| debug | set to "true" to turn on debug logging | false |
| dry_run | set to "true" to not send the webhook request | false |
| pull_request_payload | PR payload in JSON format² **(deprecated)** | (deprecated)³ |

1) The Action will determine whether to send an embed tailored towards a Pull Request Check Run or towards a general workflow run based on the presence of non-null values for the four pull request arguments. This means that you either have to provide **all** of them or **none** of them.

    Do note that you can typically keep the arguments in the argument list even if your workflow is triggered for non-PR events, as GitHub's object notation (`name.name.name`) will silently return `null` if a name is unset. In the workflow example above, a `push` event would send an embed tailored to a general workflow run, as all the PR-related arguments would all be `null`.

2) The pull request payload may be nested within an array, `[{...}]`. If the array contains multiple PR payloads, only the first one will be picked.

3) Providing a JSON payload will take precedence over the individual pr arguments. If a JSON payload is present, it will be used and the individual pr arguments will be ignored, unless parsing the JSON fails.

## Recipes

### Reporting the status of a `pull_request`-triggered workflow

One complication with `pull_request`-triggered workflows is that your secrets won't be available if the workflow is triggered for a pull request made from a fork. As you'd typically provide the webhook token as a secret, this makes using this action in such a workflow slightly more complicated.

However, GitHub has provided an additional workflow trigger specifically for this situation: [`workflow_run`](https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows#workflow_run). You can use this event to start a workflow whenever another workflow is being run or has just finished. As workflows triggered by `workflow_run` always run in the base repository, it has full access to your secrets.

To give your `workflow_run`-triggered workflow access to all the information we need to build a Pull Request status embed, you'll need to share some details from the original workflow in some way. One way to do that is by uploading an artifact. To do that, add these two steps to the end of your `pull_request`-triggered workflow:

```yaml
name: Lint & Test

on:
  pull_request:


jobs:
  lint-test:
    runs-on: ubuntu-latest

    steps:
      # Your regular steps here

      # -------------------------------------------------------------------------------

      # Prepare the Pull Request Payload artifact. If this fails, we
      # we fail silently using the `continue-on-error` option. It's
      # nice if this succeeds, but if it fails for any reason, it
      # does not mean that our lint-test checks failed.
      - name: Prepare Pull Request Payload artifact
        id: prepare-artifact
        if: always() && github.event_name == 'pull_request'
        continue-on-error: true
        run: cat $GITHUB_EVENT_PATH | jq '.pull_request' > pull_request_payload.json

      # This only makes sense if the previous step succeeded. To
      # get the original outcome of the previous step before the
      # `continue-on-error` conclusion is applied, we use the
      # `.outcome` value. This step also fails silently.
      - name: Upload a Build Artifact
        if: always() && steps.prepare-artifact.outcome == 'success'
        continue-on-error: true
        uses: actions/upload-artifact@v2
        with:
          name: pull-request-payload
          path: pull_request_payload.json
```

Then, add a new workflow that is triggered whenever the workflow above is run:

```yaml
name: Status Embed

on:
  workflow_run:
    workflows:
      - Lint & Test
    types:
      - completed

jobs:
  status_embed:
    name:  Send Status Embed to Discord
    runs-on: ubuntu-latest

    steps:
      # Process the artifact uploaded in the `pull_request`-triggered workflow:
      - name: Get Pull Request Information
        id: pr_info
        if: github.event.workflow_run.event == 'pull_request'
        run: |
          curl -s -H "Authorization: token $GITHUB_TOKEN" ${{ github.event.workflow_run.artifacts_url }} > artifacts.json
          DOWNLOAD_URL=$(cat artifacts.json | jq -r '.artifacts[] | select(.name == "pull-request-payload") | .archive_download_url')
          [ -z "$DOWNLOAD_URL" ] && exit 1
          wget --quiet --header="Authorization: token $GITHUB_TOKEN" -O pull_request_payload.zip $DOWNLOAD_URL || exit 2
          unzip -p pull_request_payload.zip > pull_request_payload.json
          [ -s pull_request_payload.json ] || exit 3
          echo "::set-output name=pr_author_login::$(jq -r '.user.login // empty' pull_request_payload.json)"
          echo "::set-output name=pr_number::$(jq -r '.number // empty' pull_request_payload.json)"
          echo "::set-output name=pr_title::$(jq -r '.title // empty' pull_request_payload.json)"
          echo "::set-output name=pr_source::$(jq -r '.head.label // empty' pull_request_payload.json)"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # Send an informational status embed to Discord instead of the
      # standard embeds that Discord sends. This embed will contain
      # more information and we can fine tune when we actually want
      # to send an embed.
      - name: GitHub Actions Status Embed for Discord
        uses: SebastiaanZ/github-status-embed-for-discord@v0.2.1
        with:
          # Webhook token
          webhook_id: '1234567'
          webhook_token: ${{ secrets.webhook_token }}

          # We need to provide the information of the workflow that
          # triggered this workflow instead of this workflow.
          workflow_name: ${{ github.event.workflow_run.name }}
          run_id: ${{ github.event.workflow_run.id }}
          run_number: ${{ github.event.workflow_run.run_number }}
          status: ${{ github.event.workflow_run.conclusion }}
          sha: ${{ github.event.workflow_run.head_sha }}

          # Now we can use the information extracted in the previous step:
          pr_author_login: ${{ steps.pr_info.outputs.pr_author_login }}
          pr_number: ${{ steps.pr_info.outputs.pr_number }}
          pr_title: ${{ steps.pr_info.outputs.pr_title }}
          pr_source: ${{ steps.pr_info.outputs.pr_source }}
```
