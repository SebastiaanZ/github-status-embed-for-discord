import logging
import sys
import typing


class MaskingFormatter(logging.Formatter):
    """A logging formatter that masks given values."""

    def __init__(self, *args, masked_values: typing.Sequence[str], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._masked_values = masked_values

    def format(self, record: logging.LogRecord) -> str:
        """Emit a logging record after masking certain values."""
        message = super().format(record)
        for masked_value in self._masked_values:
            message = message.replace(masked_value, "<masked value>")

        return message


def setup_logging(level: int, masked_values: typing.Sequence[str]) -> None:
    """Set up the logging utilities and make sure to mask sensitive data."""
    root = logging.getLogger()
    root.setLevel(level)

    logging.addLevelName(logging.DEBUG, 'debug')
    logging.addLevelName(logging.INFO, 'debug')  # GitHub Actions does not have an "info" message
    logging.addLevelName(logging.WARNING, 'warning')
    logging.addLevelName(logging.ERROR, 'error')

    handler = logging.StreamHandler(sys.stdout)
    formatter = MaskingFormatter(
        '::%(levelname)s::%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        masked_values=masked_values,
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
