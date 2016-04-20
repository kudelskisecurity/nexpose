from typing import Optional, Tuple, Mapping

from nexpose.modules.extra import Extra
from nexpose.modules.report import Report
from nexpose.modules.scan import Scan
from nexpose.modules.session import Session
from nexpose.modules.site import Site


class Nexpose:
    def __init__(self, host: str, port: int = 3780,
                 sessions_id: Optional[Mapping[Tuple[int, int], str]] = None) -> None:
        kwargs = dict(host=host, port=port, sessions_id=sessions_id)

        self.session = Session(**kwargs)
        self.site = Site(**kwargs)
        self.scan = Scan(**kwargs)
        self.report = Report(**kwargs)

        self.extra = Extra(**kwargs)
