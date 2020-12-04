import logging
import sys
import typing


class MaskingFormatter(logging.Formatter):
    """A logging formatter that masks given values."""

    def __init__(self, *args, masked_values: typing.Sequence[str], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._masked_values = masked_values

    def format(self, record: logging.LogRecord) -> None:
        """Emit a logging record after masking certain values."""
        message = super().format(record)
        for masked_value in self._masked_values:
            message = message.replace(masked_value, "<masked value>")

        return message


def setup_logging(level: int, masked_values: typing.Sequence[str]) -> None:
    """Set up the logging utilities and make sure to mask sensitive data."""
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = MaskingFormatter(
        '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        masked_values=masked_values,
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
