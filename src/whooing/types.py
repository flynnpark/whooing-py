from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

RequestScalar: TypeAlias = str | int | float | bool | None
RequestValue: TypeAlias = RequestScalar | Sequence[RequestScalar]
RequestData: TypeAlias = Mapping[str, RequestValue]

Headers: TypeAlias = Mapping[str, str]
