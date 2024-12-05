import factory
from factory.fuzzy import FuzzyChoice, FuzzyText
from faker.providers.python import Provider
from limepepper_utils.factory.banking import rand_bankish_name, rand_sort_code
from limepepper_utils.slugs import slugify

from nordigen_cli.models.model import (
    Account,
    AccountBalance,
    AccountDetail,
    AccountSchema,
    AccountTransactions,
    BalanceAmountSchema,
    BalanceSchema,
    BankTransaction,
    CurrencyExchangeSchema,
    DetailSchema,
    EndUserAgreement,
    Integration,
    IntegrationRetrieve,
    OwnerAddressStructuredSchema,
    PaginatedEndUserAgreementList,
    PaginatedRequisitionList,
    Requisition,
    SpectacularRequisition,
    TransactionAmountSchema,
    TransactionSchema,
)


# @factory.Faker.override_default_locale("en_US")
class StringAmountProvider(Provider):
    def string_amount(self, *args, **kwargs):
        return str(self.pydecimal(left_digits=3, right_digits=2, positive=True))


factory.Faker.add_provider(StringAmountProvider)


class IntegrationFactory(factory.Factory):
    class Meta:
        model = Integration

    id = factory.LazyAttribute(lambda o: slugify(o.name))
    name = factory.LazyFunction(rand_bankish_name)
    logo = factory.Faker("image_url")
    countries = factory.List([factory.Faker("country_code") for _ in range(5)])


class IntegrationRetrieveFactory(IntegrationFactory):
    class Meta:
        model = IntegrationRetrieve

    supported_payments = {
        "single-payment": [
            "SCT",
            "ISCT",
        ]
    }
    supported_features = [
        "card_accounts",
        "business_accounts",
    ]
    identification_codes = []


class EndUserAgreementFactory(factory.Factory):
    class Meta:
        model = EndUserAgreement

    id = factory.Faker("uuid4")
    created = factory.Faker("date_time")
    institution_id = factory.Faker("uuid4")
    max_historical_days = 90
    access_valid_for_days = 90
    access_scope = ["balances", "details", "transactions"]
    accepted = factory.Faker(
        "date_between",
        start_date="-1y",
        end_date="today",
    )
    mymeta = {"generator": "factory_boy"}


class PaginatedEndUserAgreementListFactory(factory.Factory):
    class Meta:
        model = PaginatedEndUserAgreementList
        exclude = (
            "base_url",
            "sequence_number",
        )

    count = factory.Faker("random_int")
    base_url = factory.Faker("url")
    sequence_number = factory.Sequence(lambda n: n if n < 10 else None)
    next = factory.LazyAttribute(lambda o: f"{o.base_url}?offset={o.sequence_number}")
    previous = factory.Faker("url")
    results = factory.List([EndUserAgreementFactory() for _ in range(5)])


class RequisitionFactory(factory.Factory):
    class Meta:
        model = Requisition

    id = factory.Faker("uuid4")
    created = factory.Faker("date_time")
    redirect = factory.Faker("url")
    status = "CR"
    institution_id = factory.Faker("uuid4")
    agreement = factory.Faker("uuid4")
    reference = factory.Faker("uuid4")
    accounts = factory.List([factory.Faker("uuid4") for _ in range(5)])
    user_language = factory.Faker("language_code")
    link = factory.Faker("url")
    ssn = factory.Faker("ssn")
    account_selection = factory.Faker("boolean")
    redirect_immediate = factory.Faker("boolean")


class PaginatedRequisitionListFactory(factory.Factory):
    class Meta:
        model = PaginatedRequisitionList
        exclude = (
            "base_url",
            "sequence_number",
        )

    count = factory.Faker("random_int")
    base_url = factory.Faker("url")
    sequence_number = factory.Sequence(lambda n: n if n < 10 else None)
    next = factory.LazyAttribute(lambda o: f"{o.base_url}?offset={o.sequence_number}")
    previous = factory.Faker("url")
    results = factory.List([RequisitionFactory() for _ in range(5)])


class SpectacularRequisitionFactory(factory.Factory):
    class Meta:
        model = SpectacularRequisition

    id = factory.Faker("uuid4")
    created = factory.Faker("date_time")
    redirect = factory.Faker("url")
    status = "CR"
    institution_id = factory.Faker("uuid4")
    agreement = factory.Faker("uuid4")
    reference = factory.Faker("uuid4")
    accounts = factory.List([factory.Faker("uuid4") for _ in range(5)])
    user_language = factory.Faker("language_code")
    link = factory.Faker("url")
    ssn = factory.Faker("ssn")
    account_selection = factory.Faker("boolean")
    redirect_immediate = factory.Faker("boolean")


class OwnerAddressStructuredSchemaFactory(factory.Factory):
    class Meta:
        model = OwnerAddressStructuredSchema

    streetName = factory.Faker("street_name")
    buildingNumber = factory.Faker("building_number")
    townName = factory.Faker("city")
    postCode = factory.Faker("postcode")
    country = factory.Faker("country")


class DetailSchemaFactory(factory.Factory):
    class Meta:
        model = DetailSchema

    resourceId = factory.Faker("uuid4")
    iban = FuzzyText(length=34, prefix="GB")
    bban = FuzzyText(length=22)
    scan = factory.LazyAttribute(rand_sort_code)
    msisdn = FuzzyText(length=15)

    currency = FuzzyChoice(["GBP", "EUR", "USD"])
    ownerName = factory.Faker("name")
    name = factory.Faker("company")
    displayName = factory.Faker("company")
    product = factory.Faker("company")
    cashAccountType = FuzzyChoice(["CACC", "SVGS"])
    status = FuzzyChoice(["enabled", "disabled"])
    bic = FuzzyText(length=11)
    # this is a string, but looks like it should be a list
    linkedAccounts = factory.Faker("uuid4")
    maskedPan = FuzzyText(length=19)
    details = factory.Faker("text")
    ownerAddressUnstructured = factory.List(
        [factory.Faker("address") for _ in range(3)]
    )
    ownerAddressStructured = factory.SubFactory(OwnerAddressStructuredSchemaFactory)


class AccountDetailFactory(factory.Factory):
    class Meta:
        model = AccountDetail

    account = factory.SubFactory(DetailSchemaFactory)


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    id = factory.Faker("uuid4")
    created = factory.LazyAttribute(
        lambda x: factory.Faker("date_time")
        .evaluate(None, None, {"locale": None})
        .strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    last_accessed = factory.LazyAttribute(
        lambda x: factory.Faker("date_time")
        .evaluate(None, None, {"locale": None})
        .strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )

    iban = FuzzyText(length=34, prefix="GB")
    bban = FuzzyText(length=22)
    status = FuzzyChoice(["enabled", "disabled"])
    institution_id = factory.Faker("uuid4")
    owner_name = factory.Faker("name")


class AccountSchemaFactory(factory.Factory):
    class Meta:
        model = AccountSchema

    iban = FuzzyText(length=34, prefix="GB")
    bban = FuzzyText(length=22)
    pan = FuzzyText(length=19)
    maskedPan = FuzzyText(length=19)
    msisdn = FuzzyText(length=15)
    currency = FuzzyChoice(["GBP", "EUR", "USD"])


class BalanceAmountSchemaFactory(factory.Factory):
    class Meta:
        model = BalanceAmountSchema

    amount = factory.Faker(
        "string_amount",
        left_digits=3,
        right_digits=2,
        positive=True,
    )
    currency = FuzzyChoice(["GBP", "EUR", "USD"])


class BalanceSchemaFactory(factory.Factory):
    class Meta:
        model = BalanceSchema

    balanceAmount = factory.SubFactory(BalanceAmountSchemaFactory)
    balanceType = FuzzyChoice(
        [
            "closingBooked",
            "expected",
            "authorised",
            "interimAvailable",
            "openingBooked",
            "forwardAvailable",
        ]
    )
    creditLimitIncluded = factory.Faker("boolean")
    lastChangeDateTime = factory.LazyAttribute(
        lambda x: factory.Faker("date_time")
        .evaluate(None, None, {"locale": None})
        .strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    referenceDate = factory.Faker("date")
    lastCommittedTransaction = FuzzyText()


class AccountBalanceFactory(factory.Factory):
    class Meta:
        model = AccountBalance

    balances = factory.List([BalanceSchemaFactory() for _ in range(5)])


class CurrencyExchangeSchemaFactory(factory.Factory):
    class Meta:
        model = CurrencyExchangeSchema

    sourceCurrency = FuzzyChoice(["GBP", "EUR", "USD"])
    exchangeRate = FuzzyText(length=10)
    unitCurrency = FuzzyChoice(["GBP", "EUR", "USD"])
    targetCurrency = FuzzyChoice(["GBP", "EUR", "USD"])
    quotationDate = factory.Faker("date")
    contractIdentification = FuzzyText()


class TransactionAmountSchemaFactory(factory.Factory):
    class Meta:
        model = TransactionAmountSchema

    amount = factory.Faker(
        "string_amount", left_digits=3, right_digits=2, positive=True
    )
    currency = FuzzyChoice(["GBP", "EUR", "USD"])


class TransactionSchemaFactory(factory.Factory):
    class Meta:
        model = TransactionSchema

    transactionId = FuzzyText()
    entryReference = FuzzyText()
    endToEndId = FuzzyText()
    mandateId = FuzzyText()
    checkId = FuzzyText()
    creditorId = FuzzyText()
    bookingDate = factory.Faker("date")
    valueDate = factory.Faker("date")
    # bookingDateTime = factory.Faker("date_time")
    bookingDateTime = factory.LazyAttribute(
        lambda x: factory.Faker("date_time")
        .evaluate(None, None, {"locale": None})
        .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    valueDateTime = factory.LazyAttribute(
        lambda x: factory.Faker("date_time")
        .evaluate(None, None, {"locale": None})
        .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    transactionAmount = factory.SubFactory(TransactionAmountSchemaFactory)
    currencyExchange = factory.List(
        [factory.SubFactory(CurrencyExchangeSchemaFactory) for _ in range(2)]
    )
    creditorName = factory.Faker("company")
    creditorAccount = factory.SubFactory(AccountSchemaFactory)
    ultimateCreditor = factory.Faker("name")
    debtorName = factory.Faker("name")
    debtorAccount = factory.SubFactory(AccountSchemaFactory)
    ultimateDebtor = factory.Faker("name")
    remittanceInformationUnstructured = FuzzyText()
    remittanceInformationUnstructuredArray = factory.List(
        [FuzzyText() for _ in range(2)]
    )
    remittanceInformationStructured = FuzzyText()
    remittanceInformationStructuredArray = factory.List([FuzzyText() for _ in range(2)])
    additionalInformation = FuzzyText()
    purposeCode = FuzzyText()
    bankTransactionCode = FuzzyText()
    proprietaryBankTransactionCode = FuzzyText()
    internalTransactionId = FuzzyText()


class BankTransactionFactory(factory.Factory):
    class Meta:
        model = BankTransaction

    booked = factory.List([TransactionSchemaFactory() for _ in range(5)])
    pending = factory.List([TransactionSchemaFactory() for _ in range(1)])


class AccountTransactionsFactory(factory.Factory):
    class Meta:
        model = AccountTransactions

    transactions = factory.SubFactory(BankTransactionFactory)


# import sys
# import inspect
# from pydantic import BaseModel
#
#
# current_module = sys.modules[__name__]
#
# models = [
#     obj
#     for name, obj in inspect.getmembers(current_module)
#     if inspect.isclass(obj) and issubclass(obj, factory.Factory)
# ]
#
# for model in models:
#     print(model)
# #    register(model)
#
# register(AccountTransactionsFactory)
