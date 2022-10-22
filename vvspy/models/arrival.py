from datetime import datetime

from loguru import logger

from vvspy.models.line_operator import LineOperator
from vvspy.models.serving_line import ServingLine


class Arrival:
    """Arrival object from a arrival request of one station.

    Attributes
    -----------
    raw :class:`dict`
        Raw dict received by the API.
    stop_id :class:`str`
        Station_id of the arrival.
    x :class:`str`
        Coordinates of the station.
    y :class:`str`
        Coordinates of the station.
    map_name :class:`str`
        Map name the API works on.
    area :class:`str`
        The area of the station (unsure atm)
    platform :class:`str`
        Platform / track of the arrival.
    platform_name :class:`str`
        name of the platform.
    stop_name :class:`str`
        name of the station.
    name_wo :class:`str`
        name of the station.
    countdown :class:`int`
        minutes until arrival.
    datetime :class:`datetime.datetime`
        Planned arrival datetime.
    real_datetime :class:`datetime.datetime`
        Estimated arrival datetime (equal to ``self.datetime`` if no realtime data is available).
    delay :class:`int`
        Delay of arrival in minutes.
    serving_line :class:`ServingLine`
        line of the incoming arrival.
    operator :class:`LineOperator`
        Operator of the incoming arrival.
    stop_infos Optional[:class:`dict`]
        All related info to the station (e.g. maintenance work).
    line_infos Optional[:class:`dict`]
        All related info to the station (e.g. maintenance work).
    """

    def __init__(self, **kwargs):
        self.stop_id = kwargs.get("stopID")
        self.x = kwargs.get("x")
        self.y = kwargs.get("y")
        self.map_name = kwargs.get("mapName")
        self.area = kwargs.get("area")
        self.platform = kwargs.get("platform")
        self.platform_name = kwargs.get("platformName")
        self.stop_name = kwargs.get("stopName")
        self.name_wo = kwargs.get("nameWO")
        self.point_type = kwargs.get("pointType")
        self.countdown = int(kwargs.get("countdown", "0"))

        # TODO: Correct default value and type
        self.datetime: datetime | None = None
        self.real_datetime = self.datetime
        dt = kwargs.get("dateTime")
        if dt:
            try:
                self.datetime = datetime(
                    year=int(dt.get("year", datetime.now().year)),
                    month=int(dt.get("month", datetime.now().month)),
                    day=int(dt.get("day", datetime.now().day)),
                    hour=int(dt.get("hour", datetime.now().hour)),
                    minute=int(dt.get("minute", datetime.now().minute)),
                )
            except ValueError:
                logger.debug("Could not parse datetime")
                self.datetime = None
        r_dt = kwargs.get("realDateTime")
        if r_dt:
            try:
                self.real_datetime = datetime(
                    year=int(r_dt.get("year", datetime.now().year)),
                    month=int(r_dt.get("month", datetime.now().month)),
                    day=int(r_dt.get("day", datetime.now().day)),
                    hour=int(r_dt.get("hour", datetime.now().hour)),
                    minute=int(r_dt.get("minute", datetime.now().minute)),
                )
            except ValueError:
                logger.debug("Could not parse real datetime")
                self.real_datetime = self.datetime
        self.delay = 0
        if self.datetime and self.real_datetime:
            self.delay = int((self.real_datetime - self.datetime).total_seconds() / 60)

        self.serving_line = ServingLine(**kwargs.get("servingLine", {}))
        self.operator = LineOperator(**kwargs.get("operator", {}))

        # inserted raw
        self.raw = kwargs
        self.stop_infos = kwargs.get("stopInfos")
        self.line_infos = kwargs.get("lineInfos")

    def __str__(self):
        pre = "[Delayed] " if self.delay > 0 else ""

        if self.real_datetime:
            if self.real_datetime.date() == datetime.now().date():
                return f"{pre}[{str(self.real_datetime.strftime('%H:%M'))}] {self.serving_line}"
            return f"{pre}[{str(self.real_datetime)}] {self.serving_line}"

        logger.debug("No real datetime available")
        return f"{pre}[N/A] {self.serving_line}"
