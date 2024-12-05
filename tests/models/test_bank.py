import pytest
from pydantic import ValidationError

from nordigen_cli.models.model import Integration, IntegrationRetrieve


class TestBankModel:  # Test class for Bank model
    def test_valid_bank_data(self):
        bank_data = {
            "id": "bank_id_123",
            "name": "Test Bank",
            "bic": "TESTBICXX",
            "transaction_total_days": "30",
            "countries": ["US", "CA"],
            "logo": "logo_url",
            "max_access_valid_for_days": "90",
        }
        bank = Integration(**bank_data)
        # assert bank.model_dump_json() == json.dumps(bank_data)
        assert bank.id == "bank_id_123"
        assert bank.name == "Test Bank"
        assert bank.bic == "TESTBICXX"
        assert bank.transaction_total_days == "30"
        assert bank.countries == ["US", "CA"]
        assert bank.logo == "logo_url"
        assert bank.max_access_valid_for_days == "90"

    def test_invalid_transaction_total_days(self):
        with pytest.raises(ValidationError):
            IntegrationRetrieve(
                id="bank_id_123",
                name="Test Bank",
                bic="TESTBICXX",
                transaction_total_days=-1,  # Invalid: Negative value
                countries=["US", "CA"],
                logo="logo_url",
                max_access_valid_for_days=90,
            )

    def test_invalid_countries(self):
        with pytest.raises(ValidationError):
            IntegrationRetrieve(
                id="bank_id_123",
                name="Test Bank",
                bic="TESTBICXX",
                transaction_total_days=30,
                countries="US",  # Invalid: Should be a list
                logo="logo_url",
                max_access_valid_for_days=90,
            )

    def test_invalid_max_access_valid_for_days(self):
        with pytest.raises(ValidationError):
            IntegrationRetrieve(
                id="bank_id_123",
                name="Test Bank",
                bic="TESTBICXX",
                transaction_total_days=30,
                countries=["US", "CA"],
                logo="logo_url",
                max_access_valid_for_days=-5,  # Invalid: Negative value
            )

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            IntegrationRetrieve(
                name="Test Bank",
                bic="TESTBICXX",
                transaction_total_days=30,
                countries=["US", "CA"],
                logo="logo_url",
                max_access_valid_for_days=90,  # Missing 'id'
            )
