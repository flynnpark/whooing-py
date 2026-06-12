from __future__ import annotations

from enum import IntEnum
from typing import Annotated, Generic, Literal, TypeAlias, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

T = TypeVar("T")


class WhooingModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApiCode(IntEnum):
    OK = 200
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    API_LIMIT_EXCEEDED = 402
    AUTH_EXPIRED = 405
    INTERNAL_ERROR = 500


class ErrorParameters(WhooingModel):
    field: Annotated[
        str | None,
        Field(title="오류 필드", description="오류가 발생한 요청 필드 이름입니다."),
    ] = None
    parameter: Annotated[
        str | None,
        Field(title="오류 파라미터", description="오류가 발생한 API 파라미터 이름입니다."),
    ] = None
    reason: Annotated[
        str | None,
        Field(title="오류 사유", description="후잉 API가 반환한 파라미터 오류 사유입니다."),
    ] = None
    expected: Annotated[
        str | int | float | bool | None,
        Field(title="기대값", description="API가 기대한 값 또는 형식입니다."),
    ] = None
    actual: Annotated[
        str | int | float | bool | None,
        Field(title="실제값", description="요청에서 전달된 실제 값입니다."),
    ] = None


def _normalize_error_parameters(value: object) -> object:
    if value is None:
        return {}
    if isinstance(value, list) and len(value) == 0:
        return {}
    return value


class WhooingResponseMetadata(WhooingModel):
    message: Annotated[
        str,
        Field(title="응답 메시지", description="후잉 API가 반환한 응답 메시지입니다."),
    ] = ""
    error_parameters: Annotated[
        ErrorParameters,
        Field(
            default_factory=ErrorParameters,
            title="오류 파라미터",
            description="오류 응답일 때 포함되는 세부 파라미터 정보입니다.",
        ),
    ]
    rest_of_api: Annotated[
        int | None,
        Field(
            title="남은 API 호출 수",
            description="후잉 API 제한 기준에서 남은 호출 가능 횟수입니다.",
        ),
    ] = None

    @field_validator("error_parameters", mode="before")
    @classmethod
    def normalize_error_parameters(cls, value: object) -> object:
        return _normalize_error_parameters(value)


class WhooingEnvelope(WhooingResponseMetadata):
    code: Annotated[
        ApiCode | int | None,
        Field(title="응답 코드", description="후잉 API의 논리 응답 코드입니다."),
    ] = None


class WhooingAPIResponse(WhooingResponseMetadata, Generic[T]):
    code: Annotated[
        ApiCode | int | None,
        Field(title="응답 코드", description="후잉 API의 논리 응답 코드입니다."),
    ] = None
    results: Annotated[
        T | None,
        Field(title="응답 결과", description="API별 실제 응답 데이터입니다."),
    ] = None


class WhooingSuccessResponse(WhooingResponseMetadata, Generic[T]):
    code: Annotated[
        Literal[ApiCode.OK, 200],
        Field(title="성공 응답 코드", description="성공 응답을 나타내는 후잉 API 코드입니다."),
    ] = ApiCode.OK
    results: Annotated[
        T, Field(title="성공 응답 결과", description="성공한 API의 실제 응답 데이터입니다.")
    ]


class WhooingNoContentResponse(WhooingResponseMetadata):
    code: Annotated[
        Literal[ApiCode.NO_CONTENT, 204],
        Field(title="내용 없음 응답 코드", description="결과 본문이 없는 성공 응답 코드입니다."),
    ] = ApiCode.NO_CONTENT
    results: Annotated[
        None,
        Field(title="응답 결과", description="204 응답에서는 결과 데이터가 없습니다."),
    ] = None

    @model_validator(mode="after")
    def validate_no_content_message(self) -> WhooingNoContentResponse:
        if self.message and self.message.lower() not in {"", "no content"}:
            return self
        return self


class WhooingErrorResponse(WhooingResponseMetadata):
    code: Annotated[
        Literal[
            ApiCode.BAD_REQUEST,
            ApiCode.UNAUTHORIZED,
            ApiCode.API_LIMIT_EXCEEDED,
            ApiCode.AUTH_EXPIRED,
            ApiCode.INTERNAL_ERROR,
            400,
            401,
            402,
            405,
            500,
        ],
        Field(title="오류 응답 코드", description="후잉 API 오류를 나타내는 논리 응답 코드입니다."),
    ]
    results: Annotated[
        None,
        Field(title="응답 결과", description="오류 응답에서는 결과 데이터가 없습니다."),
    ] = None


class HttpRateLimitResponse(WhooingModel):
    status_code: Annotated[
        Literal[429],
        Field(title="HTTP 상태 코드", description="HTTP 레벨 요청 제한 상태 코드입니다."),
    ] = 429
    retry_after: Annotated[
        float | None,
        Field(
            title="재시도 대기 시간", description="다음 요청까지 대기해야 하는 초 단위 시간입니다."
        ),
    ] = None


WhooingStrictResponse: TypeAlias = (
    WhooingSuccessResponse[T] | WhooingNoContentResponse | WhooingErrorResponse
)
