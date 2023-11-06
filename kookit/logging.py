try:
    from loguru import logger
except ModuleNotFoundError:
    from unittest.mock import Mock

    logger = Mock(
        trace=print,
        debug=print,
        info=print,
        warning=print,
        error=print,
    )
