from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock

from energytt_platform.bus import messages as m, topics as t
from energytt_platform.models.auth import MeteringPointDelegate

from auth_shared.db import db
from auth_shared.queries import MeteringPointOwnerQuery
from auth_consumer.handlers import dispatcher
from auth_api.controller import controller


GSRN = 'GSRN1'
SUBJECT1 = 'SUBJECT1'
SUBJECT2 = 'SUBJECT2'


class TestMeteringPointOwnerUpdate:
    """
    Tests handler for MeteringPointOwnerUpdate messages.
    """

    @patch('auth_consumer.handlers.broker')
    def test__on_meteringpoint_owner_update__no_current_owner_for_gsrn__should_create_owner(
            self,
            broker_mock: MagicMock,
            session: db.Session,
            client: FlaskClient,
    ):
        """
        - A MeteringPoint does not have an owner
        - Send message MeteringPointOwnerUpdate to set owner of MeteringPoint
        - Subject should be registered as owner of MeteringPoint
        """

        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        dispatcher(m.MeteringPointOwnerUpdate(
            gsrn=GSRN,
            subject=SUBJECT1,
        ))

        # -- Assert ----------------------------------------------------------

        assert controller.is_current_owner(
            session=session,
            subject=SUBJECT1,
            gsrn=GSRN,
        )

        broker_mock.publish.assert_called_once_with(
            topic=t.AUTH,
            msg=m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=SUBJECT1,
                    gsrn=GSRN,
                ),
            ),
        )

    @patch('auth_consumer.handlers.broker')
    def test__on_meteringpoint_owner_update__no_current_owner_for_gsrn__should_create_owner2(
            self,
            broker_mock: MagicMock,
            session: db.Session,
            client: FlaskClient,
    ):
        """
        - A MeteringPoint does not have an owner
        - Send message MeteringPointOwnerUpdate to set owner of MeteringPoint
        - Subject should be registered as owner of MeteringPoint
        """

        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        dispatcher(m.MeteringPointOwnerUpdate(
            gsrn=GSRN,
            subject=SUBJECT1,
        ))

        # -- Assert ----------------------------------------------------------

        assert controller.is_current_owner(
            session=session,
            subject=SUBJECT1,
            gsrn=GSRN,
        )

        broker_mock.publish.assert_called_once_with(
            topic=t.AUTH,
            msg=m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=SUBJECT1,
                    gsrn=GSRN,
                ),
            ),
        )

    # @patch('auth_consumer.handlers.broker')
    # def test__on_meteringpoint_owner_update__gsrn_has_owner__should_overwrite_current_owner(
    #         self,
    #         broker_mock: MagicMock,
    #         session: db.Session,
    #         client: FlaskClient,
    # ):
    #
    #     # -- Arrange ---------------------------------------------------------
    #
    #     # -- Act -------------------------------------------------------------
    #
    #     dispatcher(m.MeteringPointOwnerUpdate(
    #         gsrn=GSRN,
    #         subject=SUBJECT1,
    #     ))
    #
    #     # -- Assert ----------------------------------------------------------
    #
    #     broker_mock.publish.assert_called_once_with(
    #         topic=t.AUTH,
    #         msg=m.MeteringPointDelegateGranted(
    #             delegate=MeteringPointDelegate(
    #                 subject=SUBJECT1,
    #                 gsrn=GSRN,
    #             ),
    #         ),
    #     )
    #
    #     assert controller.is_current_owner(
    #         session=session,
    #         subject=SUBJECT1,
    #         gsrn=GSRN,
    #     )
