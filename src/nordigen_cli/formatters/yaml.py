from typing import Union

from limepepper_utils.serialization import serialize_to_dict
from limepepper_utils.yaml_importing import yaml
from loguru import logger
from pydantic import BaseModel

from nordigen_cli.format_output import OutputFormatter


class YamlFormatter(OutputFormatter):
    """Format output as YAML"""

    def format(self, data: Union[BaseModel, list[BaseModel], dict, list[dict]]) -> str:
        logger.debug(f"formatting {data.__class__} type({type(data)})")
        if isinstance(data, BaseModel):
            return self.dump_item(self.format_item(data))
        elif isinstance(data, (list, tuple)) and all(
            isinstance(x, BaseModel) for x in data
        ):
            return self.dump_item([self.format_item(item) for item in data])
        else:
            return self.dump_item(data)

    def format_item(
        self, data: BaseModel
    ) -> Union[BaseModel, list[BaseModel], dict, list[dict]]:
        serialized = data.model_dump(context={"simplified_type": True})
        return serialized

    def dump_item(self, data: BaseModel | dict | list) -> str:
        logger.debug(f"dumping item {data.__class__} type({type(data)})")
        return yaml.safe_dump(
            serialize_to_dict(data),
            sort_keys=False,
        )
