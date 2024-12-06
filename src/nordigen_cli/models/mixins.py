import contextvars
from contextlib import contextmanager
from typing import Annotated, Any, Optional, Union

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_serializers import model_serializer
from pydantic_core.core_schema import SerializationInfo
from rich.repr import RichReprResult


class MetaMixin(BaseModel):
    messages: Annotated[
        dict[str, Any], Field(..., description="messages from unit tests")
    ]


class BaseMixin(BaseModel):
    id: str
    metadata: Annotated[
        dict[str, Any], Field(..., description="messages from unit tests")
    ]

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


# class UpperAttrMetaclass(type):
#     def __new__(cls, name, bases, dct):
#         attrs = ((name, value) for name, value in
#         dct.items() if not name.startswith('__'))
#         uppercase_attrs = dict((name.upper(), value) for name, value in attrs)
#         return super(UpperAttrMetaclass, cls).__new


class ReprAdapter(BaseModel):
    @classmethod
    def from_model(
        cls, model: BaseModel
    ) -> Union["ReprAdapter", list["ReprAdapter"], list["BaseModel"], dict[str, Any]]:
        pass


class ReprMgr:
    mappings: dict[type[BaseModel], type[ReprAdapter]] = {}

    @classmethod
    def register(cls, model: type[BaseModel], formatter: type[ReprAdapter]):
        # print(f"Registering {model} with {formatter}")
        cls.mappings.update({model: formatter})

    @classmethod
    def adapt(cls, data: Union[BaseModel, Any]):
        if type(data) in cls.mappings:
            logger.debug(f"===> Adapting {type(data)}")
            adapted = cls.mappings[type(data)].from_model(data)
            logger.debug(f"<=== adapted to {type(adapted)}")
            return adapted
        else:
            # logger.debug(f"not adapter type {type(data)} in {cls.mappings}")
            return data


class OmitIfNone:
    pass


serializer_mode = contextvars.ContextVar("serializer_mode", default=False)


class NoSerializeNoneModel(BaseModel):
    @contextmanager
    def serialize_as(self, simplified_type: Optional[bool] = False):
        token = serializer_mode.set(simplified_type)
        try:
            yield self
        finally:
            serializer_mode.reset(token)

    @model_serializer(mode="wrap")
    def _serialize(self, handler, info: SerializationInfo):
        # print(f"serialising type {type(self)}")
        logger.trace(f"serialising info {info}")
        context = info.context or {}
        if context.get("simplified_type"):
            instance = ReprMgr.adapt(self)
            inner = instance.model_dump(mode="json", exclude_none=True)
        else:
            inner = handler(instance := self)
        logger.trace(f"keys are {instance.model_fields.keys()}")
        for k, v in instance.model_fields.items():
            if k in inner:
                if (
                    any(isinstance(m, OmitIfNone) for m in v.metadata)
                    and inner[k] is None
                ):
                    del inner[k]
        return inner


class DisplayField:
    pass


class BaseRootMixin(NoSerializeNoneModel):
    mymeta: Annotated[Optional[dict[str, Any]], OmitIfNone()] = None

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    def accept(self, visitor, /, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)

    # def __rich__(self) -> str:
    #     return "[bold cyan]MyObject()"

    # __repr_name__ = _repr.Representation.__repr_name__
    # __repr_str__ = _repr.Representation.__repr_str__
    # __pretty__ = _repr.Representation.__pretty__
    # __rich_repr__ = _repr.Representation.__rich_repr__

    def __rich_repr__(self) -> RichReprResult:
        if self.__class__.__name__ == "TransactionSchema":
            yield "Transaction", {}
            # yield "Amount", self.amount
            for name, field_repr in self.__repr_args__():
                # print(f"{name!r}= {field_repr!r}")
                # print(f"{type(name)} = {type(field_repr)}")
                if name is None:
                    yield field_repr

                if field_repr is not None:
                    yield name, field_repr
                else:
                    yield name, field_repr, None
        else:
            yield from super().__rich_repr__()
