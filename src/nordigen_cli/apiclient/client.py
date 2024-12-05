import importlib
from typing import Optional
from uuid import UUID

from apiclient.paginators import paginated
from loguru import logger
from pydantic import AnyUrl, validate_call

from nordigen_cli.apiclient.base import NordigenClientBase
from nordigen_cli.apiclient.paginator import next_page_by_url
from nordigen_cli.models.model import (
    Account,
    AccountBalance,
    AccountDetail,
    AccountTransactions,
    EnduserAcceptanceDetailsRequest,
    EndUserAgreement,
    EndUserAgreementRequest,
    Integration,
    IntegrationRetrieve,
    Requisition,
    RequisitionRequest,
    SpectacularRequisition,
)

# inject the requests_debugger module
requests_debugger = importlib.import_module("requests_debugger")


class NordigenClient(NordigenClientBase):
    # Banks endpoints
    @validate_call
    def list_banks(self, code: str, /, **kwargs) -> list[Integration]:
        response = self.get(self.endpoints.banks.format(code=code), **kwargs)
        if isinstance(response, list):
            return [Integration.model_validate(bank) for bank in response]
        return []

    @validate_call
    def show_bank(self, bank_id: str, /, **kwargs) -> IntegrationRetrieve:
        response = self.get(self.endpoints.bank.format(id=bank_id), **kwargs)
        return IntegrationRetrieve.model_validate(response)

    # Account endpoints

    @validate_call
    def show_account_metadata(self, account_id: UUID):
        return Account.model_validate(
            self.get(self.endpoints.account_metadata.format(id=account_id))
        )

    @validate_call
    def show_account_details(self, account_id: UUID):
        return AccountDetail.model_validate(
            self.get(self.endpoints.account_details.format(id=account_id))
        )

    @validate_call
    def show_account_balances(self, account_id: UUID):
        return AccountBalance.model_validate(
            self.get(self.endpoints.account_balances.format(id=account_id))
        )

    @validate_call
    def list_account_transactions(self, account_id: UUID) -> AccountTransactions:
        response = self.get(self.endpoints.transactions.format(id=account_id))
        return AccountTransactions.model_validate(response)

    # Agreement endpoints

    @validate_call
    def create_end_user_agreement(
        self,
        institution_id: str,
        access_valid_for_days: int = 90,
        max_historical_days: int = 90,
    ) -> EndUserAgreement:
        eua_request = EndUserAgreementRequest.model_validate(
            {
                "institution_id": institution_id,
                "max_historical_days": max_historical_days,
                "access_valid_for_days": access_valid_for_days,
                "access_scope": [
                    "balances",
                    "details",
                    "transactions",
                ],
            }
        )
        return EndUserAgreement.model_validate(
            self.post(
                self.endpoints.agreements,
                data=eua_request.model_dump(
                    mode="json",
                    exclude_none=True,
                ),
            )
        )

    @validate_call
    def delete_agreement(
        self,
        agreement_id,
    ):
        logger.debug(f"deleting agreement with id: {agreement_id}")
        return self.delete(self.endpoints.agreement.format(id=agreement_id))

    @paginated(by_url=next_page_by_url)
    @validate_call
    def list_agreements(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EndUserAgreement]:
        responses = self.get(self.endpoints.agreements)
        results = [
            EndUserAgreement.model_validate(result)
            for res in responses
            for result in res["results"]
        ]
        return results

    @validate_call
    def show_agreement(self, agreement_id: UUID) -> EndUserAgreement:
        return EndUserAgreement.model_validate(
            self.get(self.endpoints.agreement.format(id=agreement_id))
        )

    @validate_call
    def accept_agreement(
        self,
        agreement_id: UUID,
        user_agent: Optional[str],
        ip_address: Optional[str],
    ) -> EndUserAgreement:
        url = self.endpoints.agreement_accept.format(id=agreement_id)
        data = EnduserAcceptanceDetailsRequest.model_validate(
            {
                "user_agent": user_agent if user_agent else "Nordigen CLI",
                "ip_address": ip_address if ip_address else "127.0.0.1",
            }
        )
        return EndUserAgreement.model_validate(
            self.put(
                url,
                data=data.model_dump(
                    mode="json",
                    exclude_none=True,
                ),
            ),
        )

    # Requisition endpoints
    @paginated(by_url=next_page_by_url)
    @validate_call
    def list_requisitions(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Requisition]:
        responses = self.get(self.endpoints.requisitions)
        results = [
            Requisition.model_validate(result)
            for res in responses
            for result in res["results"]
        ]
        return results

    @validate_call
    def delete_requisition(
        self,
        requisition_id: UUID,
    ):
        return self.delete(self.endpoints.requisition.format(id=requisition_id))

    def create_requisition(
        self,
        /,
        *,
        redirect: str,
        institution_id,
        agreement: UUID = None,
        reference: str = None,
        user_language="EN",
        ssn: Optional[str],
        account_selection: Optional[bool] = False,
        redirect_immediate: Optional[bool] = False,
    ) -> SpectacularRequisition:
        url = self.endpoints.requisitions
        logger.trace(f"creating requisition with reference: {reference}")
        logger.trace(f"ssn is: {ssn}")
        logger.trace(f"user_language is: {user_language}")

        request = RequisitionRequest(
            redirect=AnyUrl(redirect),
            institution_id=institution_id,
            agreement=agreement,
            reference=reference,
            user_language=user_language,
            ssn=ssn,
            account_selection=account_selection,
            redirect_immediate=redirect_immediate,
        )
        return SpectacularRequisition.model_validate(
            self.post(
                url,
                data=request.model_dump(
                    mode="json",
                    exclude_none=True,
                ),
            )
        )

    @validate_call
    def show_requisition(self, requisition_id):
        return Requisition.model_validate(
            self.get(self.endpoints.requisition.format(id=requisition_id))
        )
