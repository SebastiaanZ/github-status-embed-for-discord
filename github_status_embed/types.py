from __future__ import annotations

import abc
import dataclasses
import enum
import typing


class AllowedMentions(typing.TypedDict, total=False):
    parse: typing.List[str]
    users: typing.List[str]
    roles: typing.List[str]
    replied_user: bool


class EmbedField(typing.TypedDict, total=False):
    name: str
    value: str
    inline: bool


class EmbedFooter(typing.TypedDict, total=False):
    text: str
    icon_url: str
    proxy_icon_url: str


class EmbedThumbnail(typing.TypedDict, total=False):
    url: str
    proxy_url: str
    height: str
    width: str


class EmbedProvider(typing.TypedDict, total=False):
    name: str
    url: str


class EmbedAuthor(typing.TypedDict, total=False):
    name: str
    url: str
    icon_url: str
    proxy_icon_url: str


class EmbedVideo(typing.TypedDict, total=False):
    url: str
    height: str
    width: str


class EmbedImage(typing.TypedDict, total=False):
    url: str
    proxy_url: str
    height: str
    width: str


class Embed(typing.TypedDict, total=False):
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
    content: str
    username: str
    avatar_url: str
    tts: bool
    file: bytes
    embeds: typing.List[Embed]
    payload_json: str
    allowed_mentions: AllowedMentions


class InvalidArgument(ValueError):
    """Raised when an argument is of the wrong type."""


class MissingArgument(TypeError):
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
            except (ValueError, KeyError):
                raise InvalidArgument(f"invalid value for `{attribute}`: {value}") from None
            else:
                kwargs[attribute] = value

        return cls(**kwargs)


class WorkflowStatus(enum.Enum):
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
        return self.name

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
        return f"https://github.com/{self.repository}/commits/{self.sha}"


@dataclasses.dataclass(frozen=True)
class Webhook(TypedDataclass):
    webhook_id: int
    webhook_token: str


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
        """Return the `pr_number`."""
        return self.pr_title

    @property
    def source(self) -> str:
        """Return the `pr_number`."""
        return f"{self.pr_source:25.25}..." if len(self.pr_source) > 28 else self.pr_source
