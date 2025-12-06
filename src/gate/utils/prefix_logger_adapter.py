import logging

class PrefixAdapter(logging.LoggerAdapter):
    def __init__(self, logger, prefix: str):
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        return f"<{self.prefix}> {msg}", kwargs
