import json
from abc import ABC, abstractmethod
from typing import Union

from limepepper_utils.serialization import serialize_to_dict
from loguru import logger
from pydantic import BaseModel
from pydantic.json import pydantic_encoder
from rich.console import Console
from rich.table import Table

from nordigen_cli.models.renderable import ReprMgr

console = Console()


def strip_meta_fields(fields: list[str]):
    return [field for field in fields if field not in ["mymeta"]]


class OutputFormatter(ABC):
    """Base class for output formatters"""

    @abstractmethod
    def format(self, data: Union[BaseModel, list[BaseModel], dict, list[dict]]) -> str:
        """Format the data according to the specific formatter's rules"""
        pass


class JsonFormatter(OutputFormatter):
    """[green]Format[/green] output as JSON"""

    def format(self, data: Union[BaseModel, list[BaseModel], dict, list[dict]]) -> str:
        if isinstance(data, (list, tuple)) and all(
            isinstance(x, BaseModel) for x in data
        ):
            return json.dumps(
                [item.model_dump(mode="json") for item in data],
                indent=2,
                default=pydantic_encoder,
            )
            # return [item.model_dump_json(indent=2) for item in data]
        elif isinstance(data, BaseModel):
            return data.model_dump_json(indent=2)
        else:
            return json.dumps(data, indent=2)


class TableFormatter(OutputFormatter):
    """Format output as a Rich table"""

    def format(self, data: Union[BaseModel, list[BaseModel], dict, list[dict]]) -> None:
        if isinstance(data, (list, tuple)):
            self.format_list_like(data)
        else:
            self.format_item_like(data)

        if not data:
            console.print("[yellow]No data to display[/yellow]")
            return

    def format_item_like(self, data: BaseModel | dict) -> None:
        if isinstance(data, BaseModel):
            fields = data.model_fields.keys()
        else:
            fields = data.keys()

        table = Table(
            show_header=True,
            header_style="bold magenta",
            row_styles=["dim", ""],
        )
        for field in ["Name", "Value"]:
            table.add_column(str(field))

        if isinstance(data, BaseModel):
            for field in fields:
                row = [field, self.format_field(getattr(data, field))]
                table.add_row(*row)
        else:
            for field in fields:
                row = [field, self.format_field(data.get(field, ""))]
                table.add_row(*row)

        console.print(table)

    def format_list_like(self, data: list[BaseModel] | list[dict]) -> None:
        # Get fields from first item
        first_item = data[0]
        if isinstance(first_item, BaseModel):
            fields = first_item.model_fields.keys()
        else:
            fields = first_item.keys()

        # Create table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            row_styles=["dim", ""],
        )
        for field in fields:
            table.add_column(str(field))

        # Add rows
        for item in data:
            if isinstance(item, BaseModel):
                row = [self.format_field(getattr(item, field)) for field in fields]
            else:
                row = [self.format_field(item.get(field, "")) for field in fields]
            table.add_row(*row)

        console.print(table)

    def format_field(self, field):
        if isinstance(field, BaseModel):
            # print(f"format_field: {type(field)} as BaseModel")
            return field.model_dump_json(context={"simplified_type": True})
        elif isinstance(field, list):
            # print(f"format_field: {type(field)} as list")
            return "\n".join([self.format_field(item) for item in field])
        elif isinstance(field, dict):
            # print(f"format_field: {type(field)} as list")
            return json.dumps(serialize_to_dict(field), indent=2)
        else:
            # print(f"format_field: {type(field)} as other")
            return str(field)


class FormattingManager:
    """Manages available formatters and handles formatting requests"""

    def __init__(self):
        self.formatters: dict[str, OutputFormatter] = {
            "json": JsonFormatter(),
            "rich": TableFormatter(),
        }

        try:
            import yaml  # noqa: F401

            from nordigen_cli.formatters.yaml import YamlFormatter

            self.formatters["yaml"] = YamlFormatter()
        except ImportError:
            logger.trace("PyYAML not installed, YAML output not available")

    def get_available_formats(self) -> list[str]:
        """Return list of available format names"""
        return list(self.formatters.keys())

    def format_output(
        self,
        data: Union[BaseModel, list[BaseModel], dict, list[dict]],
        format_type: str,
    ) -> None:
        """Format and output the data using the specified formatter"""
        formatter = self.formatters.get(format_type)
        if not formatter:
            console.print(
                f"[red]Unknown format '{format_type}'. Available "
                f"formats: {', '.join(self.get_available_formats())}[/red]"
            )
            return

        # if type has repr adapter, adapt it
        data = ReprMgr.adapt(data)

        result = formatter.format(data)
        if result:  # Some formatters (like TableFormatter) handle their own output
            console.print(result)


class Formatter:
    def pr_account(self):
        pass

    def pr_banks(self, banks, format):
        logger.trace(type(banks))

        if format == "text":
            for bank in banks:
                # print("name: {:35}  id: {}".format(bank["name"], bank["id"]))
                logger.trace(f"{bank.name:35}  {bank.id=}")
                # print("")
        elif format == "json":
            logger.trace(json.dumps([bank.model_dump() for bank in banks], indent=4))

    """
    {
    "bankTransactionCode": "PMNT",
    "bookingDate": "2021-06-28",
    "remittanceInformationUnstructured": "PAYMENT Alderaan Coffe",
    "transactionAmount": {
        "amount": "-15.00",
        "currency": "EUR"
    },
    "transactionId": "2021062802749502-1",
    "valueDate": "2021-06-28"
    }
    """

    def pr_transactions(self, transactions, format):
        if format == "text":
            for tx in transactions["transactions"]["booked"]:
                # if(format == "text"):

                amount = tx["transactionAmount"]["amount"]
                info = tx["remittanceInformationUnstructured"]

                if "transactionId" in tx:
                    trn_id = tx["transactionId"]
                else:
                    trn_id = f"{tx['bookingDate']}-{amount}-{info}"

                logger.trace(
                    '{}: {:>7} {} : "{}" {}'.format(
                        tx["bookingDate"],
                        tx["transactionAmount"]["amount"],
                        tx["transactionAmount"]["currency"],
                        trn_id,
                        tx["remittanceInformationUnstructured"],
                    )
                )

                # print("remit infos: \"{}\"".format(
                # )
                #     # print("")
                # elif(format == "json"):
        elif format == "json":
            logger.trace(json.dumps(transactions["transactions"], indent=4))


formatter = Formatter()
