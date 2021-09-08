from datetime import datetime, timezone

from energytt_platform.models.auth import MeteringPointDelegate
from energytt_platform.bus import \
    MessageDispatcher, messages as m, topics as t

from auth_shared.db import db
from auth_shared.bus import broker
from auth_shared.models import DbMeteringPointOwner
from auth_shared.queries import MeteringPointOwnerQuery


# -- Message handlers --------------------------------------------------------


@db.atomic()
def on_meteringpoint_owner_update(
        msg: m.MeteringPointOwnerUpdate,
        session: db.Session,
):
    """
    TODO
    """

    # TODO Move to a Controller class

    current_owner = MeteringPointOwnerQuery(session) \
        .has_gsrn(msg.gsrn) \
        .is_current_owner() \
        .one_or_none()

    if current_owner is not None:
        current_owner.set_ends_now()

        broker.publish(
            topic=t.AUTH,
            msg=m.MeteringPointDelegateRevoked(
                delegate=MeteringPointDelegate(
                    subject=current_owner.subject,
                    gsrn=msg.gsrn,
                )
            )
        )

    if msg.subject is not None:
        session.add(DbMeteringPointOwner(
            subject=msg.subject,
            gsrn=msg.gsrn,
            begin=datetime.now(tz=timezone.utc),
        ))

        broker.publish(
            topic=t.AUTH,
            msg=m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=msg.subject,
                    gsrn=msg.gsrn,
                )
            )
        )


# -- Dispatcher --------------------------------------------------------------


dispatcher = MessageDispatcher({
    m.MeteringPointOwnerUpdate: on_meteringpoint_owner_update,
})
