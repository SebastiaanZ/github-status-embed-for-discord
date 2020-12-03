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
    embeds: typing.List[EmbedField]
    payload_json: str
    allowed_mentions: AllowedMentions
