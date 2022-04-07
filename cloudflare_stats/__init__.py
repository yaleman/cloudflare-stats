""" cloudflare stats things """

import json
import sys
from typing import Any, Dict, List, Optional

from loguru import logger

def k2v(
    data: List[Dict[str, Any]],
    key: str="key",
    delete_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
    """ turns a list of json objects into a ... something less hard to deal with

    """

    if delete_fields is None:
        delete_fields = []

    result: Dict[str, Any] = {}
    for element in data:
        if key not in element:
            raise ValueError(f"Couldn't find {key} in {json.dumps(element, default=str)}")
        element_key = element[key]
        for fieldname in delete_fields:
            del element[fieldname]
        result[element_key] = element
    return result


def setup_logging(debug_mode: bool) -> None:
    """ sets up logging """
    logger.remove()
    if debug_mode:
        logger.add(sink=sys.stderr, level="DEBUG")
    else:
        logger.add(sink=sys.stderr, level="INFO")
