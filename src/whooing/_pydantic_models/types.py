from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import Field

AccountGroupValue: TypeAlias = Annotated[
    Literal["assets", "liabilities", "capital", "income", "expenses"],
    Field(
        title="계정 분류 값",
        description="후잉 계정 분류 값입니다. 자산, 부채, 자본, 수입, 비용 중 하나입니다.",
    ),
]

DateValue: TypeAlias = Annotated[
    int | str,
    Field(
        title="날짜 값",
        description=(
            "후잉 API에서 사용하는 날짜 값입니다. "
            "일반적으로 YYYYMMDD 또는 YYYYMM 형식입니다."
        ),
    ),
]

TimestampValue: TypeAlias = Annotated[
    int,
    Field(title="Unix timestamp", description="초 단위 Unix timestamp 값입니다.", ge=0),
]

MoneyValue: TypeAlias = Annotated[
    int | float,
    Field(title="금액 값", description="후잉 가계부의 금액 또는 집계 금액입니다."),
]

IdentifierValue: TypeAlias = Annotated[
    int | str,
    Field(title="식별자", description="후잉 API 리소스를 식별하는 ID 값입니다."),
]

YnFlag: TypeAlias = Annotated[
    Literal["y", "n"],
    Field(title="Y/N 플래그", description="후잉 API에서 사용하는 y 또는 n 상태 값입니다."),
]
