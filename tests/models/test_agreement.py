from datetime import datetime, timezone, UTC

import pytest
from pydantic import ValidationError, PositiveInt
from rich import inspect

from nordigen_cli.models.agreement import Agreement


example_data = """
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created": "2024-11-15T10:03:39.385Z",
  "institution_id": "string",
  "max_historical_days": 90,
  "access_valid_for_days": 90,
  "access_scope": [
    "balances",
    "details",
    "transactions"
  ],
  "accepted": "2024-11-15T10:03:39.385Z"
}
"""


class TestAgreement:

    def test_from_json(self):
        agreement = Agreement.model_validate_json(example_data)
        assert agreement.id == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        assert agreement.institution_id == "string"
        assert agreement.max_historical_days == 90
        assert agreement.access_valid_for_days == 90
        assert agreement.access_scope == ["balances", "details", "transactions"]
        assert isinstance(agreement.accepted, datetime)

    def test_valid_agreement(self):
        agreement = Agreement(
            id="123",
            created=datetime.now(tz=UTC),
            institution_id="456",
            max_historical_days=30,
            access_valid_for_days=90,
            access_scope=["accounts", "transactions"],
            accepted=None,
        )
        assert agreement.id == "123"
        assert agreement.institution_id == "456"
        assert agreement.max_historical_days == 30
        assert agreement.access_valid_for_days == 90
        assert agreement.access_scope == ["accounts", "transactions"]
        assert agreement.accepted is None

    def test_invalid_id(self):
        with pytest.raises(ValidationError):
            Agreement(
                id=123,  # Invalid type
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days=30,
                access_valid_for_days=90,
                access_scope=["accounts"],
                accepted=None,
            )

    def test_invalid_created(self):
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created="not a datetime",  # Invalid type
                institution_id="456",
                max_historical_days=30,
                access_valid_for_days=90,
                access_scope=["accounts"],
                accepted=None,
            )

    def test_invalid_institution_id(self):
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id=456,  # Invalid type
                max_historical_days=30,
                access_valid_for_days=90,
                access_scope=["accounts"],
                accepted=None,
            )

    def test_invalid_max_historical_days(self):
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days=-1,  # Invalid value
                access_valid_for_days=90,
                access_scope=["accounts"],
                accepted=None,
            )
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days="thirty",  # Invalid type
                access_valid_for_days=90,
                access_scope=["accounts"],
                accepted=None,
            )

    def test_invalid_access_valid_for_days(self):
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days=30,
                access_valid_for_days=-1,  # Invalid value
                access_scope=["accounts"],
                accepted=None,
            )

        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days=30,
                access_valid_for_days="90.5",  # Invalid type
                access_scope=["accounts"],
                accepted=None,
            )

    def test_invalid_access_scope(self):
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days=30,
                access_valid_for_days=90,
                access_scope="accounts",  # Invalid type
                accepted=None,
            )

    def test_invalid_accepted(self):
        with pytest.raises(ValidationError):
            Agreement(
                id="123",
                created=datetime.now(tz=UTC),
                institution_id="456",
                max_historical_days=30,
                access_valid_for_days=90,
                access_scope=["accounts"],
                accepted="This-should-be-a-date-or-none",  # Invalid type
            )
