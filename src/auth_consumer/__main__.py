from energytt_platform.bus import topics as t

from auth_shared.bus import broker

from .handlers import dispatcher


broker.listen(
    topics=[t.AUTH],
    handler=dispatcher,
)
