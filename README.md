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

        # Information about the current workflow
        workflow_name: ${{ github.workflow }}
        run_id: ${{ github.run_id }}
        run_number: ${{ github.run_number }}
        status: ${{ job.status }}
        actor: ${{ github.actor }}
        repository:  ${{ github.repository }}
        ref: ${{ github.ref }}
        sha: ${{ github.sha }}

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

**Note:** The example step above contains the typical way of providing the arguments.

| Argument | Description | Required |
| --- | --- | :---: |
| webhook_id | ID of the Discord webhook (use a string) | yes |
| webhook_token | Token of the Discord webhook | yes |
| workflow_name | Name of the workflow | yes |
| run_id | Run ID of the workflow | yes |
| run_number | Run number of the workflow  | yes |
| status | Status for the embed; one of ["succes", "failure", "cancelled"] | yes |
| actor | Actor who requested the workflow | yes |
| repository | Repository; has to be in form `owner/repo` | yes |
| ref | Branch or tag ref that triggered the workflow run | yes |
| sha | Full commit SHA that triggered the workflow run. | yes |
| pr_author_login | **Login** of the Pull Request author | no¹ |
| pr_number | Pull Request number | no¹ |
| pr_title | Title of the Pull Request | no¹ |
| pr_source | Source branch for the Pull Request | no¹ |

1) The Action will determine whether to send an embed tailored towards a Pull Request Check Run or towards a general workflow run based on the presence of non-null values for the four pull request arguments. This means that you either have to provide **all** of them or **none** of them.

    Do note that you can typically keep the arguments in the argument list even if your workflow is triggered for non-PR events, as GitHub's object notation (`name.name.name`) will silently return `null` if a name is unset. In the workflow example above, a `push` event would send an embed tailored to a general workflow run, as all the PR-related arguments would all be `null`.

## Recipes

To be added.
