from nexpose.models.failure import Failure


class NetworkError(Exception):
    def __init__(self, failure: Failure) -> None:
        super().__init__(repr(failure))
        self.failure = failure
