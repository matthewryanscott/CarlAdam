"""Interface to the Kroki and Niolesk services."""

import base64
import os
import zlib
from functools import lru_cache

DEFAULT_KROKI_BASE_URL = "https://kroki.io/"
DEFAULT_NIOLESK_BASE_URL = "https://niolesk.top/"
DEFAULT_NIOLESK_KROKI_URL = DEFAULT_KROKI_BASE_URL

KROKI_BASE_URL = os.getenv("CARLADAM_KROKI_BASE_URL", DEFAULT_KROKI_BASE_URL)
NIOLESK_BASE_URL = os.getenv("CARLADAM_NIOLESK_BASE_URL", DEFAULT_NIOLESK_BASE_URL)
NIOLESK_KROKI_URL = os.getenv("CARLADAM_NIOLESK_KROKI_URL", DEFAULT_NIOLESK_KROKI_URL)

KROKI_MARKDOWN_TEMPLATE = """\
![Diagram]({image_url})

[Edit this diagram]({niolesk_url}) [Pop out]({image_url})
"""


@lru_cache
def kroki_encoded(s: str) -> str:
    data = s.encode("utf8")
    return base64.urlsafe_b64encode(zlib.compress(data, 9)).decode("ascii")


@lru_cache
def kroki_image_url(
    diagram_source: str,
    diagram_type: str = "plantuml",
    image_format: str = "svg",
    base_url: str = KROKI_BASE_URL,
) -> str:
    encoded_source = kroki_encoded(diagram_source)
    return f"{base_url}{diagram_type}/{image_format}/{encoded_source}"


@lru_cache
def niolesk_edit_url(image_url: str) -> str:
    return f"{NIOLESK_BASE_URL}#{image_url}"
