from energytt_platform.bus import get_default_broker

from .config import EVENT_BUS_SERVERS


broker = get_default_broker(
    group='auth',
    servers=EVENT_BUS_SERVERS,
)
