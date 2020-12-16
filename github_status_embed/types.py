from __future__ import annotations

import collections
import dataclasses
import enum
import json
import logging
import typing

log = logging.getLogger(__name__)

MIN_EMBED_FIELD_LENGTH = 20


class MissingActionFile(FileNotFoundError):
    """Raised when the Action file can't be located."""


class InvalidArgument(TypeError):
    """Raised when an argument is of the wrong type."""


class MissingArgument(TypeError):
    """Raised when a required argument was missing from the inputs."""

    def __init__(self, arg_name: str) -> None:
        msg = "\n\n".join((
            f"missing non-null value for argument `{arg_name}`",
            "Hint: incorrect context paths like `github.non_existent` return `null` silently.",
        ))
        super().__init__(msg)


class TypedDataclass:
    """Convert the dataclass arguments to the annotated types."""

    optional = False

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def __init_subclass__(cls, optional: bool = False, **kwargs) -> None:
        """Keep track of whether or not this class is optional."""
        super().__init_subclass__(**kwargs)
        cls.optional = optional

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> typing.Optional[TypedDataclass]:
        """Convert the attributes to their annotated types."""
        typed_attributes = typing.get_type_hints(cls)

        # If we have an optional dataclass and none of the values were provided,
        # return `None`. The reason is that optional classes should either be
        # fully initialized, with all values, or not at all. If we observe at
        # least one value, we assume that the intention was to provide them
        # all.
        if cls.optional and all(arguments.get(attr, "") == "" for attr in typed_attributes):
            return None

        # Extract and convert the keyword arguments needed for this data type.
        kwargs = {}
        for attribute, _type in typed_attributes.items():
            value = arguments.pop(attribute, None)

            # At this point, we should not have any missing arguments any more.
            if value is None:
                raise MissingArgument(attribute)

            try:
                if issubclass(_type, enum.Enum):
                    value = _type[value.upper()]
                else:
                    value = _type(value)
                    if isinstance(value, collections.Sized) and len(value) == 0:
                        raise ValueError
            except (ValueError, KeyError):
                raise InvalidArgument(f"invalid value for `{attribute}`: {value}") from None
            else:
                kwargs[attribute] = value

        return cls(**kwargs)


class WorkflowStatus(enum.Enum):
    """An Enum subclass that represents the workflow status."""

    SUCCESS = {"verb": "succeeded", "adjective": "Successful", "color": 38912}
    FAILURE = {"verb": "failed", "adjective": "Failed", "color": 16525609}
    CANCELLED = {"verb": "was cancelled", "adjective": "Cancelled", "color": 6702148}

    @property
    def verb(self) -> str:
        """Return the verb associated with the status."""
        return self.value["verb"]

    @property
    def color(self) -> int:
        """Return the color associated with the status."""
        return self.value["color"]

    @property
    def adjective(self) -> str:
        """Return the adjective associated with the status."""
        return self.value["adjective"]


@dataclasses.dataclass(frozen=True)
class Workflow(TypedDataclass):
    """A dataclass to hold information about the executed workflow."""

    workflow_name: str
    run_id: int
    run_number: int
    status: WorkflowStatus
    repository: str
    actor: str
    ref: str
    sha: str

    @property
    def name(self) -> str:
        """A convenience getter for the Workflow name."""
        return self.workflow_name

    @property
    def id(self) -> int:
        """A convenience getter for the Workflow id."""
        return self.run_id

    @property
    def number(self) -> int:
        """A convenience getter for the Workflow number."""
        return self.run_number

    @property
    def url(self) -> str:
        """Get the url to the Workflow run result."""
        return f"https://github.com/{self.repository}/actions/runs/{self.run_id}"

    @property
    def actor_url(self) -> str:
        """Get the url to the Workflow run result."""
        return f"https://github.com/{self.actor}"

    @property
    def short_sha(self) -> str:
        """Return the short commit sha."""
        return self.sha[:7]

    @property
    def commit_url(self) -> str:
        """Return the short commit sha."""
        return f"https://github.com/{self.repository}/commit/{self.sha}"

    @property
    def repository_owner(self) -> str:
        """Extract and return the repository owner from the repository field."""
        owner, _, _name = self.repository.partition("/")
        return owner

    @property
    def repository_name(self) -> str:
        """Extract and return the repository owner from the repository field."""
        _owner, _, name = self.repository.partition("/")
        return name


@dataclasses.dataclass(frozen=True)
class Webhook(TypedDataclass):
    """A simple dataclass to hold information about the target webhook."""

    webhook_id: int
    webhook_token: str

    @property
    def id(self) -> int:
        """Return the snowflake ID of the webhook."""
        return self.webhook_id

    @property
    def token(self) -> str:
        """Return the token of the webhook."""
        return self.webhook_token

    @property
    def url(self) -> str:
        """Return the endpoint to execute this webhook."""
        return f"https://canary.discord.com/api/webhooks/{self.id}/{self.token}"


@dataclasses.dataclass(frozen=True)
class PullRequest(TypedDataclass, optional=True):
    """
    Dataclass to hold the PR-related arguments.

    The attributes names are equal to argument names in the GitHub Actions
    specification to allow for helpful error messages. To provide a convenient
    public API, property getters were used with less redundant information in
    the naming scheme.
    """

    pr_author_login: str
    pr_number: int
    pr_title: str
    pr_source: str

    @classmethod
    def from_payload(cls, arguments: typing.Dict[str, str]) -> typing.Optional[PullRequest]:
        """Create a Pull Request instance from Pull Request Payload JSON."""
        # Safe load the JSON Payload provided as a command line argument.
        raw_payload = arguments.pop('pull_request_payload').replace("\\", "\\\\")
        log.debug(f"Attempting to parse PR Payload JSON: {raw_payload!r}.")
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            log.debug("Failed to parse JSON, dropping down to empty payload")
            payload = {}
        else:
            log.debug("Successfully parsed parsed payload")

        # If the payload contains multiple PRs in a list, use the first one.
        if isinstance(payload, list):
            log.debug("The payload contained a list, extracting first PR.")
            payload = payload[0] if payload else {}

        if not payload:
            log.warning("PR payload could not be parsed, attempting regular pr arguments.")
            return cls.from_arguments(arguments)

        # Get the target arguments from the payload, yielding similar results
        # when keys are missing as to when their corresponding arguments are
        # missing.
        arguments["pr_author_login"] = payload.get('user', {}).get('login', '')
        arguments["pr_number"] = payload.get('number', '')
        arguments["pr_title"] = payload.get('title', '')
        arguments["pr_source"] = payload.get('head', {}).get('label', '')

        return cls.from_arguments(arguments)

    @property
    def author(self) -> str:
        """Return the `pr_author_login` field."""
        return self.pr_author_login

    @property
    def author_url(self) -> str:
        """Return a URL for the author's profile."""
        return f"https://github.com/{self.pr_author_login}"

    @property
    def number(self) -> int:
        """Return the `pr_number`."""
        return self.pr_number

    @property
    def title(self) -> str:
        """Return the title of the PR."""
        return self.pr_title

    def shortened_source(self, length: int, owner: typing.Optional[str] = None) -> str:
        """Returned a shortened representation of the source branch."""
        pr_source = self.pr_source

        # This removes the owner prefix in the source field if it matches
        # the current repository. This means that it will only be displayed
        # when the PR is made from a branch on a fork.
        if owner:
            pr_source = pr_source.removeprefix(f"{owner}:")

        # Truncate the `pr_source` if it's longer than the specified length
        length = length if length >= MIN_EMBED_FIELD_LENGTH else MIN_EMBED_FIELD_LENGTH
        if len(pr_source) > length:
            stop = length - 3
            pr_source = f"{pr_source[:stop]}..."

        return pr_source


class AllowedMentions(typing.TypedDict, total=False):
    """A TypedDict to represent the AllowedMentions in a webhook payload."""

    parse: typing.List[str]
    users: typing.List[str]
    roles: typing.List[str]
    replied_user: bool


class EmbedField(typing.TypedDict, total=False):
    """A TypedDict to represent an embed field in a webhook payload."""

    name: str
    value: str
    inline: bool


class EmbedFooter(typing.TypedDict, total=False):
    """A TypedDict to represent an embed footer in a webhook payload."""

    text: str
    icon_url: str
    proxy_icon_url: str


class EmbedThumbnail(typing.TypedDict, total=False):
    """A TypedDict to represent an embed thumbnail in a webhook payload."""

    url: str
    proxy_url: str
    height: str
    width: str


class EmbedProvider(typing.TypedDict, total=False):
    """A TypedDict to represent an embed provider in a webhook payload."""

    name: str
    url: str


class EmbedAuthor(typing.TypedDict, total=False):
    """A TypedDict to represent an embed author in a webhook payload."""

    name: str
    url: str
    icon_url: str
    proxy_icon_url: str


class EmbedVideo(typing.TypedDict, total=False):
    """A TypedDict to represent an embed video in a webhook payload."""

    url: str
    height: str
    width: str


class EmbedImage(typing.TypedDict, total=False):
    """A TypedDict to represent an embed image in a webhook payload."""

    url: str
    proxy_url: str
    height: str
    width: str


class Embed(typing.TypedDict, total=False):
    """A TypedDict to represent an embed in a webhook payload."""

    title: str
    type: str
    description: str
    url: str
    timestamp: str
    color: int
    footer: EmbedFooter
    image: EmbedImage
    thumbnail: EmbedThumbnail
    video: EmbedVideo
    provider: EmbedProvider
    author: EmbedAuthor
    fields: typing.List[EmbedField]


class WebhookPayload(typing.TypedDict, total=False):
    """A TypedDict to represent the webhook payload itself."""

    content: str
    username: str
    avatar_url: str
    tts: bool
    file: bytes
    embeds: typing.List[Embed]
    payload_json: str
    allowed_mentions: AllowedMentions
