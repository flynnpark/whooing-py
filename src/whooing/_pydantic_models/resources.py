from __future__ import annotations

from typing import Annotated

from pydantic import Field

from whooing._pydantic_models.base import WhooingModel
from whooing._pydantic_models.types import (
    AccountGroupValue,
    DateValue,
    IdentifierValue,
    MoneyValue,
    TimestampValue,
    YnFlag,
)


class User(WhooingModel):
    user_id: Annotated[
        IdentifierValue | None, Field(title="사용자 ID", description="후잉 사용자 식별자입니다.")
    ] = None
    username: Annotated[
        str | None,
        Field(title="사용자 이름", description="후잉에 표시되는 사용자 이름입니다."),
    ] = None
    email: Annotated[
        str | None,
        Field(title="이메일", description="후잉 계정에 등록된 이메일 주소입니다."),
    ] = None
    level: Annotated[
        str | int | None,
        Field(title="회원 등급", description="후잉 사용자 계정의 서비스 등급입니다."),
    ] = None
    last_ip: Annotated[
        str | None,
        Field(title="마지막 접속 IP", description="사용자의 마지막 로그인 IP 주소입니다."),
    ] = None
    last_login_timestamp: Annotated[
        TimestampValue | None,
        Field(title="마지막 로그인 시각", description="마지막 로그인 시각의 Unix timestamp입니다."),
    ] = None
    created_timestamp: Annotated[
        TimestampValue | None,
        Field(title="생성 시각", description="후잉 계정 생성 시각의 Unix timestamp입니다."),
    ] = None
    modified_timestamp: Annotated[
        TimestampValue | None,
        Field(
            title="수정 시각",
            description="후잉 계정 정보가 마지막으로 수정된 Unix timestamp입니다.",
        ),
    ] = None
    language: Annotated[
        str | None,
        Field(title="언어", description="사용자의 후잉 표시 언어 설정입니다."),
    ] = None
    expire: Annotated[
        TimestampValue | None,
        Field(
            title="서비스 만료 시각",
            description="유료 서비스 또는 계정 권한 만료 Unix timestamp입니다.",
        ),
    ] = None
    timezone: Annotated[
        str | None,
        Field(title="시간대", description="사용자 계정에 설정된 시간대입니다."),
    ] = None
    currency: Annotated[
        str | None,
        Field(title="기본 통화", description="사용자 계정의 기본 통화 코드입니다."),
    ] = None
    country: Annotated[
        str | None,
        Field(title="국가", description="사용자 계정의 국가 코드입니다."),
    ] = None
    image: Annotated[
        str | None,
        Field(title="프로필 이미지 키", description="후잉 내부 프로필 이미지 식별자입니다."),
    ] = None
    image_url: Annotated[
        str | None,
        Field(title="프로필 이미지 URL", description="프로필 이미지를 조회할 수 있는 URL입니다."),
    ] = None
    point: Annotated[
        str | MoneyValue | None,
        Field(title="포인트", description="사용자 계정에 표시되는 후잉 포인트 값입니다."),
    ] = None
    mileage: Annotated[
        MoneyValue | None,
        Field(title="마일리지", description="사용자 계정의 후잉 마일리지 값입니다."),
    ] = None
    sound: Annotated[
        YnFlag | str | None,
        Field(title="소리 설정", description="후잉 UI의 알림음 사용 여부 설정입니다."),
    ] = None


class UserLog(WhooingModel):
    id: Annotated[
        IdentifierValue | None, Field(title="로그 ID", description="사용자 로그 식별자입니다.")
    ] = None
    contents: Annotated[
        str | None,
        Field(title="로그 내용", description="사용자 활동 로그의 내용입니다."),
    ] = None
    datetime: Annotated[
        TimestampValue | None,
        Field(title="로그 시각", description="로그가 기록된 Unix timestamp입니다."),
    ] = None
    ip: Annotated[
        str | None, Field(title="IP 주소", description="로그와 연결된 IP 주소입니다.")
    ] = None
    segment0: Annotated[
        str | None,
        Field(title="로그 분류 1", description="후잉 내부 로그 분류 값입니다."),
    ] = None
    segment1: Annotated[
        str | None,
        Field(title="로그 분류 2", description="후잉 내부 로그 세부 분류 값입니다."),
    ] = None
    writer: Annotated[
        str | None,
        Field(title="작성자", description="로그를 생성한 주체입니다."),
    ] = None


class UserPointLog(WhooingModel):
    point_id: Annotated[
        IdentifierValue | None,
        Field(title="포인트 로그 ID", description="포인트 변동 로그 식별자입니다."),
    ] = None
    datetime: Annotated[
        TimestampValue | None,
        Field(title="포인트 변동 시각", description="포인트가 변동된 Unix timestamp입니다."),
    ] = None
    description: Annotated[
        str | None,
        Field(title="포인트 설명", description="포인트 변동 사유 설명입니다."),
    ] = None
    point: Annotated[
        MoneyValue | None,
        Field(title="포인트", description="변동된 포인트 값입니다."),
    ] = None
    remains: Annotated[
        str | MoneyValue | None,
        Field(title="잔여 포인트", description="포인트 변동 후 남은 포인트 값입니다."),
    ] = None
    owner: Annotated[
        IdentifierValue | None,
        Field(title="소유자 ID", description="포인트 로그와 연결된 사용자 식별자입니다."),
    ] = None
    etc: Annotated[
        str | None,
        Field(title="기타 정보", description="포인트 로그의 추가 정보입니다."),
    ] = None
    writer: Annotated[
        str | None,
        Field(title="작성자", description="포인트 로그를 생성한 주체입니다."),
    ] = None


class Section(WhooingModel):
    section_id: Annotated[
        str | None,
        Field(title="섹션 ID", description="후잉 가계부 섹션 식별자입니다."),
    ] = None
    title: Annotated[
        str | None, Field(title="섹션 이름", description="가계부 섹션 이름입니다.")
    ] = None
    memo: Annotated[
        str | None, Field(title="섹션 메모", description="가계부 섹션 설명 메모입니다.")
    ] = None
    color: Annotated[
        str | None,
        Field(title="섹션 색상", description="후잉 섹션에 설정된 색상 값입니다."),
    ] = None
    currency: Annotated[
        str | None,
        Field(title="섹션 통화", description="해당 섹션에서 사용하는 통화 코드입니다."),
    ] = None
    isolation: Annotated[
        str | None,
        Field(title="섹션 격리 여부", description="섹션 데이터 격리 설정 값입니다."),
    ] = None
    total_assets: Annotated[
        MoneyValue | None,
        Field(title="총 자산", description="섹션 내 전체 자산 합계입니다."),
    ] = None
    total_liabilities: Annotated[
        MoneyValue | None,
        Field(title="총 부채", description="섹션 내 전체 부채 합계입니다."),
    ] = None
    skin_id: Annotated[
        int | None, Field(title="스킨 ID", description="섹션 UI 스킨 식별자입니다.")
    ] = None
    decimal_places: Annotated[
        int | None,
        Field(title="소수점 자리수", description="금액 표시에 사용하는 소수점 자리수입니다."),
    ] = None
    date_format: Annotated[
        str | None,
        Field(title="날짜 형식", description="섹션에서 사용하는 날짜 표시 형식입니다."),
    ] = None
    webhook_token: Annotated[
        str | None,
        Field(title="웹훅 토큰", description="섹션 웹훅 연동에 사용하는 토큰입니다."),
    ] = None
    use_ai: Annotated[
        YnFlag | str | None,
        Field(title="AI 사용 여부", description="섹션의 AI 기능 사용 여부입니다."),
    ] = None
    ui: Annotated[
        dict[str, object] | None,
        Field(title="UI 설정", description="후잉 섹션 화면 표시와 관련된 UI 설정입니다."),
    ] = None


class Account(WhooingModel):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="후잉 계정 과목 식별자입니다."),
    ] = None
    type: Annotated[
        AccountGroupValue | str | None,
        Field(title="계정 종류", description="자산, 부채, 자본, 수입, 비용 등 계정 분류입니다."),
    ] = None
    title: Annotated[
        str | None, Field(title="계정 이름", description="계정 과목 표시 이름입니다.")
    ] = None
    memo: Annotated[
        str | None, Field(title="계정 메모", description="계정 과목에 대한 설명 메모입니다.")
    ] = None
    open_date: Annotated[
        DateValue | None,
        Field(title="개설일", description="계정 과목이 시작되는 날짜입니다."),
    ] = None
    close_date: Annotated[
        DateValue | None,
        Field(title="종료일", description="계정 과목이 종료되는 날짜입니다."),
    ] = None
    category: Annotated[
        str | None,
        Field(title="계정 카테고리", description="계정 과목의 세부 카테고리입니다."),
    ] = None
    opt_use_date: Annotated[
        DateValue | None,
        Field(title="사용일 옵션", description="카드 등 특수 계정에서 사용하는 사용일 옵션입니다."),
    ] = None
    opt_pay_date: Annotated[
        DateValue | None,
        Field(title="결제일 옵션", description="카드 등 특수 계정에서 사용하는 결제일 옵션입니다."),
    ] = None
    opt_pay_account_id: Annotated[
        str | None,
        Field(title="결제 계정 ID", description="카드 결제 등에 연결된 지불 계정 식별자입니다."),
    ] = None
    opt_1: Annotated[
        str | None,
        Field(title="계정 옵션 1", description="후잉 계정 과목의 추가 옵션 값입니다."),
    ] = None
    opt_2: Annotated[
        str | None,
        Field(title="계정 옵션 2", description="후잉 계정 과목의 추가 옵션 값입니다."),
    ] = None
    opt_3: Annotated[
        str | None,
        Field(title="계정 옵션 3", description="후잉 계정 과목의 추가 옵션 값입니다."),
    ] = None
    opt_4: Annotated[
        str | None,
        Field(title="계정 옵션 4", description="후잉 계정 과목의 추가 옵션 값입니다."),
    ] = None


class AccountExistence(WhooingModel):
    count: Annotated[
        int | None, Field(title="거래 건수", description="해당 계정에 연결된 거래 수입니다.")
    ] = None
    min_date: Annotated[
        DateValue | None,
        Field(
            alias="minDate",
            title="최초 거래일",
            description="해당 계정에 연결된 가장 이른 거래일입니다.",
        ),
    ] = None
    max_date: Annotated[
        DateValue | None,
        Field(
            alias="maxDate",
            title="마지막 거래일",
            description="해당 계정에 연결된 가장 최근 거래일입니다.",
        ),
    ] = None
    balance: Annotated[
        MoneyValue | None,
        Field(title="잔액", description="해당 계정의 현재 또는 기준 잔액입니다."),
    ] = None
    last_one: Annotated[
        YnFlag | str | None,
        Field(
            title="마지막 계정 여부",
            description="후잉 계정 존재 확인 응답의 마지막 항목 여부입니다.",
        ),
    ] = None
    close_date: Annotated[
        DateValue | None,
        Field(title="종료일", description="해당 계정 과목의 종료 날짜입니다."),
    ] = None
    clients: Annotated[
        list[str],
        Field(
            default_factory=list,
            title="거래처 목록",
            description="계정과 연결된 거래처 목록입니다.",
        ),
    ]


class Accounts(WhooingModel):
    assets: Annotated[
        list[Account],
        Field(
            default_factory=list, title="자산 계정 목록", description="자산 계정 과목 목록입니다."
        ),
    ]
    liabilities: Annotated[
        list[Account],
        Field(
            default_factory=list, title="부채 계정 목록", description="부채 계정 과목 목록입니다."
        ),
    ]
    capital: Annotated[
        list[Account],
        Field(
            default_factory=list, title="자본 계정 목록", description="자본 계정 과목 목록입니다."
        ),
    ]
    income: Annotated[
        list[Account],
        Field(
            default_factory=list, title="수입 계정 목록", description="수입 계정 과목 목록입니다."
        ),
    ]
    expenses: Annotated[
        list[Account],
        Field(
            default_factory=list, title="비용 계정 목록", description="비용 계정 과목 목록입니다."
        ),
    ]


class Entry(WhooingModel):
    entry_id: Annotated[
        IdentifierValue | None,
        Field(title="거래 ID", description="후잉 거래 내역 식별자입니다."),
    ] = None
    entry_date: Annotated[
        DateValue | None,
        Field(title="거래일", description="거래가 발생한 날짜입니다."),
    ] = None
    l_account: Annotated[
        AccountGroupValue | str | None,
        Field(title="왼쪽 계정 종류", description="복식부기 거래의 왼쪽 계정 분류입니다."),
    ] = None
    l_account_id: Annotated[
        str | None,
        Field(title="왼쪽 계정 ID", description="복식부기 거래의 왼쪽 계정 과목 식별자입니다."),
    ] = None
    r_account: Annotated[
        AccountGroupValue | str | None,
        Field(title="오른쪽 계정 종류", description="복식부기 거래의 오른쪽 계정 분류입니다."),
    ] = None
    r_account_id: Annotated[
        str | None,
        Field(title="오른쪽 계정 ID", description="복식부기 거래의 오른쪽 계정 과목 식별자입니다."),
    ] = None
    item: Annotated[
        str | None, Field(title="거래 항목", description="거래 내역의 항목명입니다.")
    ] = None
    money: Annotated[MoneyValue | None, Field(title="금액", description="거래 금액입니다.")] = None
    memo: Annotated[
        str | None, Field(title="거래 메모", description="거래 내역에 적힌 메모입니다.")
    ] = None
    total: Annotated[
        str | MoneyValue | None,
        Field(
            title="누적 합계", description="거래 목록 응답에서 제공되는 누적 또는 표시 합계입니다."
        ),
    ] = None
    detail: Annotated[
        str | None,
        Field(title="거래 상세", description="거래 상세 조회 응답에서 제공되는 세부 내용입니다."),
    ] = None
    app_id: Annotated[
        IdentifierValue | None,
        Field(title="앱 ID", description="거래를 생성한 앱 또는 연동 식별자입니다."),
    ] = None
    attachments: Annotated[
        list[dict[str, object]],
        Field(
            default_factory=list,
            title="첨부 파일 목록",
            description="거래에 연결된 첨부 파일 목록입니다.",
        ),
    ]
    timestamp: Annotated[
        TimestampValue | None,
        Field(title="기록 시각", description="거래가 기록되거나 수정된 Unix timestamp입니다."),
    ] = None


class EntryList(WhooingModel):
    reports: Annotated[
        list[dict[str, object]],
        Field(
            default_factory=list,
            title="거래 목록 리포트",
            description="거래 목록과 함께 제공되는 리포트 데이터입니다.",
        ),
    ]
    rows: Annotated[
        list[Entry],
        Field(
            default_factory=list,
            title="거래 행 목록",
            description="조회 조건에 맞는 거래 행 목록입니다.",
        ),
    ]


class EntryChangeRow(WhooingModel):
    date: Annotated[
        DateValue | None,
        Field(title="집계 날짜", description="거래 변화 분석에서 집계 기준이 되는 날짜입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="집계 금액", description="해당 날짜 또는 구간의 거래 집계 금액입니다."),
    ] = None


class EntryChangeAggregate(WhooingModel):
    in_: Annotated[
        MoneyValue | None,
        Field(
            default=None,
            alias="in",
            title="유입 금액",
            description="분석 기간의 유입 금액 합계입니다.",
        ),
    ]
    out: Annotated[
        MoneyValue | None,
        Field(title="유출 금액", description="분석 기간의 유출 금액 합계입니다."),
    ] = None


class EntryChangeReport(WhooingModel):
    aggregate: Annotated[
        EntryChangeAggregate | None,
        Field(title="변화 분석 합계", description="거래 변화 분석의 전체 집계 값입니다."),
    ] = None
    rows_type: Annotated[
        str | None,
        Field(title="행 집계 단위", description="거래 변화 분석 행의 집계 단위입니다."),
    ] = None
    rows: Annotated[
        list[EntryChangeRow],
        Field(
            default_factory=list,
            title="변화 분석 행",
            description="거래 변화 분석의 상세 행 목록입니다.",
        ),
    ]


class EntryAnalysis(WhooingModel):
    account: Annotated[
        AccountGroupValue | str | None,
        Field(title="계정 종류", description="분석 대상 계정 분류입니다."),
    ] = None
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="분석 대상 계정 과목 식별자입니다."),
    ] = None
    item: Annotated[str | None, Field(title="항목", description="분석 대상 거래 항목명입니다.")] = (
        None
    )
    client: Annotated[
        str | None, Field(title="거래처", description="분석 대상 거래처 이름입니다.")
    ] = None
    money: Annotated[
        MoneyValue | None, Field(title="합계 금액", description="분석 결과의 합계 금액입니다.")
    ] = None
    count: Annotated[
        int | None, Field(title="건수", description="분석 결과에 포함된 거래 건수입니다.")
    ] = None
    entries: Annotated[
        list[Entry] | None,
        Field(title="거래 목록", description="분석 결과에 포함된 거래 내역 목록입니다."),
    ] = None


class EntryNameAmount(WhooingModel):
    name: Annotated[
        str | None,
        Field(title="이름", description="분석 결과의 계정, 거래처, 항목 이름입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="금액", description="해당 이름에 대한 집계 금액입니다."),
    ] = None


class EntryFlowAmount(WhooingModel):
    from_: Annotated[
        MoneyValue | None,
        Field(
            default=None,
            alias="from",
            title="시작 금액",
            description="조회 기간 시작 시점의 금액입니다.",
        ),
    ]
    to: Annotated[
        MoneyValue | None,
        Field(title="종료 금액", description="조회 기간 종료 시점의 금액입니다."),
    ] = None
    margin: Annotated[
        MoneyValue | None,
        Field(title="증감액", description="시작 금액과 종료 금액의 차이입니다."),
    ] = None


class EntryFlowAccount(EntryFlowAmount):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="흐름 분석이 연결된 계정 과목 ID입니다."),
    ] = None


class EntryFlowGroup(WhooingModel):
    total: Annotated[
        EntryFlowAmount | None,
        Field(title="계정 흐름 합계", description="계정 분류별 흐름 합계입니다."),
    ] = None
    accounts: Annotated[
        list[EntryFlowAccount],
        Field(
            default_factory=list,
            title="계정별 흐름",
            description="계정 과목별 시작 금액, 종료 금액, 증감액 목록입니다.",
        ),
    ]


class EntryFlowReport(WhooingModel):
    assets: Annotated[
        EntryFlowGroup | None,
        Field(title="자산 흐름", description="자산 계정 흐름 분석 결과입니다."),
    ] = None
    liabilities: Annotated[
        EntryFlowGroup | None,
        Field(title="부채 흐름", description="부채 계정 흐름 분석 결과입니다."),
    ] = None
    capital: Annotated[
        EntryFlowGroup | None,
        Field(title="자본 흐름", description="자본 계정 흐름 분석 결과입니다."),
    ] = None
    income: Annotated[
        EntryFlowGroup | None,
        Field(title="수입 흐름", description="수입 계정 흐름 분석 결과입니다."),
    ] = None
    expenses: Annotated[
        EntryFlowGroup | None,
        Field(title="비용 흐름", description="비용 계정 흐름 분석 결과입니다."),
    ] = None


class FrequentItem(WhooingModel):
    item_id: Annotated[
        IdentifierValue | None,
        Field(title="자주 쓰는 항목 ID", description="자주 쓰는 항목 식별자입니다."),
    ] = None
    section_id: Annotated[
        str | None, Field(title="섹션 ID", description="항목이 속한 섹션 ID입니다.")
    ] = None
    item: Annotated[
        str | None, Field(title="항목명", description="자주 쓰는 거래 항목명입니다.")
    ] = None
    money: Annotated[
        MoneyValue | None, Field(title="기본 금액", description="항목에 설정된 기본 금액입니다.")
    ] = None
    memo: Annotated[
        str | None, Field(title="메모", description="항목에 설정된 기본 메모입니다.")
    ] = None
    l_account: Annotated[
        AccountGroupValue | str | None,
        Field(title="왼쪽 계정 종류", description="항목에 연결된 왼쪽 계정 분류입니다."),
    ] = None
    l_account_id: Annotated[
        str | None,
        Field(title="왼쪽 계정 ID", description="항목에 연결된 왼쪽 계정 과목 ID입니다."),
    ] = None
    r_account: Annotated[
        AccountGroupValue | str | None,
        Field(title="오른쪽 계정 종류", description="항목에 연결된 오른쪽 계정 분류입니다."),
    ] = None
    r_account_id: Annotated[
        str | None,
        Field(title="오른쪽 계정 ID", description="항목에 연결된 오른쪽 계정 과목 ID입니다."),
    ] = None


class MonthlyItem(FrequentItem):
    start_date: Annotated[
        DateValue | None,
        Field(title="시작일", description="월별 반복 항목이 시작되는 날짜입니다."),
    ] = None
    end_date: Annotated[
        DateValue | None,
        Field(title="종료일", description="월별 반복 항목이 종료되는 날짜입니다."),
    ] = None
    d_day: Annotated[
        int | None,
        Field(title="남은 일수", description="반복 항목의 예정일까지 남은 일수입니다."),
    ] = None
    due_date: Annotated[
        DateValue | None,
        Field(title="예정일", description="월별 반복 항목의 예정 날짜입니다."),
    ] = None
    paid_date: Annotated[
        DateValue | None,
        Field(title="처리일", description="월별 반복 항목이 처리된 날짜입니다."),
    ] = None
    pay_date: Annotated[
        DateValue | None,
        Field(title="결제일", description="월별 반복 항목의 결제 기준일입니다."),
    ] = None
    skip_holiday: Annotated[
        YnFlag | str | None,
        Field(title="휴일 건너뛰기 여부", description="반복 항목이 휴일을 건너뛰는지 여부입니다."),
    ] = None


class FrequentItems(WhooingModel):
    slot1: Annotated[
        list[FrequentItem],
        Field(
            default_factory=list,
            title="자주 쓰는 항목 슬롯 1",
            description="slot1에 저장된 자주 쓰는 항목입니다.",
        ),
    ]
    slot2: Annotated[
        list[FrequentItem],
        Field(
            default_factory=list,
            title="자주 쓰는 항목 슬롯 2",
            description="slot2에 저장된 자주 쓰는 항목입니다.",
        ),
    ]
    slot3: Annotated[
        list[FrequentItem],
        Field(
            default_factory=list,
            title="자주 쓰는 항목 슬롯 3",
            description="slot3에 저장된 자주 쓰는 항목입니다.",
        ),
    ]
    slot4: Annotated[
        list[FrequentItem],
        Field(
            default_factory=list,
            title="자주 쓰는 항목 슬롯 4",
            description="slot4에 저장된 자주 쓰는 항목입니다.",
        ),
    ]
    slot5: Annotated[
        list[FrequentItem],
        Field(
            default_factory=list,
            title="자주 쓰는 항목 슬롯 5",
            description="slot5에 저장된 자주 쓰는 항목입니다.",
        ),
    ]


class MonthlyItems(WhooingModel):
    count: Annotated[
        int | None, Field(title="월별 항목 수", description="월별 반복 항목 총 개수입니다.")
    ] = None
    slot1: Annotated[
        list[MonthlyItem],
        Field(
            default_factory=list,
            title="월별 항목 슬롯 1",
            description="slot1에 저장된 월별 반복 항목입니다.",
        ),
    ]


class Budget(WhooingModel):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="예산이 설정된 계정 과목 식별자입니다."),
    ] = None
    target_ym: Annotated[
        DateValue | None,
        Field(title="대상 연월", description="예산이 적용되는 대상 연월입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None, Field(title="예산 금액", description="설정된 예산 금액입니다.")
    ] = None


class BudgetAmount(WhooingModel):
    budget: Annotated[
        MoneyValue | None,
        Field(title="예산", description="해당 계정 또는 구간에 설정된 예산 금액입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(
            title="사용 금액",
            description="해당 계정 또는 구간에서 실제 사용되거나 집계된 금액입니다.",
        ),
    ] = None
    remains: Annotated[
        MoneyValue | None,
        Field(title="남은 금액", description="예산에서 사용 금액을 제외한 남은 금액입니다."),
    ] = None


class BudgetAccount(BudgetAmount):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="예산 집계가 연결된 계정 과목 식별자입니다."),
    ] = None


class BudgetRow(BudgetAmount):
    title: Annotated[
        str | None,
        Field(title="예산 행 이름", description="예산 리포트 행의 표시 이름입니다."),
    ] = None
    accounts: Annotated[
        list[BudgetAccount],
        Field(
            default_factory=list,
            title="예산 계정 목록",
            description="해당 행에 포함된 계정별 예산 정보입니다.",
        ),
    ]


class BudgetReport(WhooingModel):
    aggregate: Annotated[
        BudgetAmount | None,
        Field(
            title="예산 합계", description="조회 범위 전체의 예산, 사용 금액, 남은 금액 합계입니다."
        ),
    ] = None
    rows_type: Annotated[
        str | None,
        Field(
            title="예산 행 종류",
            description="예산 리포트 행이 어떤 기준으로 구성되었는지 나타냅니다.",
        ),
    ] = None
    rows: Annotated[
        list[BudgetRow],
        Field(
            default_factory=list,
            title="예산 행 목록",
            description="예산 리포트의 상세 행 목록입니다.",
        ),
    ]
    max: Annotated[
        MoneyValue | None,
        Field(
            title="최대 예산 기준값",
            description="예산 화면 표시 또는 차트 계산에 쓰이는 최대 기준 금액입니다.",
        ),
    ] = None
    misc: Annotated[
        BudgetAmount | None,
        Field(title="기타 예산", description="명시적인 행에 포함되지 않는 기타 예산 집계입니다."),
    ] = None
    total: Annotated[
        BudgetAmount | None,
        Field(title="전체 예산", description="예산 리포트 전체 합계입니다."),
    ] = None
    total_floating: Annotated[
        BudgetAmount | None,
        Field(title="변동 예산 합계", description="변동성 예산 항목의 합계입니다."),
    ] = None
    total_steady: Annotated[
        BudgetAmount | None,
        Field(title="고정 예산 합계", description="고정성 예산 항목의 합계입니다."),
    ] = None


class BudgetGoal(WhooingModel):
    section_id: Annotated[
        str | None, Field(title="섹션 ID", description="예산 목표가 속한 섹션 ID입니다.")
    ] = None
    start_date: Annotated[
        DateValue | None,
        Field(title="시작일", description="예산 목표 기간의 시작 날짜입니다."),
    ] = None
    end_date: Annotated[
        DateValue | None,
        Field(title="종료일", description="예산 목표 기간의 종료 날짜입니다."),
    ] = None
    set_id: Annotated[
        IdentifierValue | None,
        Field(title="예산 목표 설정 ID", description="예산 목표 설정을 식별하는 ID입니다."),
    ] = None
    last_modified: Annotated[
        TimestampValue | None,
        Field(
            title="마지막 수정 시각",
            description="예산 목표가 마지막으로 수정된 Unix timestamp입니다.",
        ),
    ] = None
    base_ym: Annotated[
        DateValue | None,
        Field(title="기준 연월", description="예산 목표 계산의 기준이 되는 연월입니다."),
    ] = None
    goal_ym: Annotated[
        DateValue | None,
        Field(title="목표 연월", description="예산 목표 달성 목표 연월입니다."),
    ] = None
    base_money: Annotated[
        MoneyValue | None,
        Field(title="기준 금액", description="예산 목표 계산의 기준 금액입니다."),
    ] = None
    goal_money: Annotated[
        MoneyValue | None,
        Field(title="목표 금액", description="예산 목표로 설정된 금액입니다."),
    ] = None
    base_income: Annotated[
        MoneyValue | None,
        Field(title="기준 수입", description="예산 목표 계산에 쓰이는 기준 수입 금액입니다."),
    ] = None
    base_expenses: Annotated[
        MoneyValue | None,
        Field(title="기준 비용", description="예산 목표 계산에 쓰이는 기준 비용 금액입니다."),
    ] = None
    each_months: Annotated[
        list[MoneyValue],
        Field(
            default_factory=list,
            title="월별 목표 금액",
            description="월 단위로 분할된 목표 금액 목록입니다.",
        ),
    ]
    split_type: Annotated[
        str | None,
        Field(title="분할 방식", description="예산 목표를 월별로 나누는 방식입니다."),
    ] = None


class CapitalGoal(WhooingModel):
    section_id: Annotated[
        str | None, Field(title="섹션 ID", description="자본 목표가 속한 섹션 ID입니다.")
    ] = None
    monthly_goals: Annotated[
        dict[str, MoneyValue] | None,
        Field(title="월별 자본 목표", description="월 단위로 설정된 자본 목표 금액입니다."),
    ] = None


class CapitalGoalRow(WhooingModel):
    date: Annotated[
        DateValue | None,
        Field(title="목표 날짜", description="자본 목표가 적용되는 날짜 또는 연월입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="목표 금액", description="해당 날짜 또는 연월의 자본 목표 금액입니다."),
    ] = None


class Bill(WhooingModel):
    account_id: Annotated[
        str | None, Field(title="계정 ID", description="청구서와 연결된 계정 ID입니다.")
    ] = None
    title: Annotated[
        str | None, Field(title="청구서 이름", description="청구 항목 이름입니다.")
    ] = None
    money: Annotated[
        MoneyValue | None, Field(title="청구 금액", description="청구되거나 예정된 금액입니다.")
    ] = None
    entry_date: Annotated[
        DateValue | None, Field(title="청구일", description="청구 또는 결제 예정 날짜입니다.")
    ] = None


class Checkcard(Bill):
    pass


class BillAccount(WhooingModel):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="청구 또는 체크카드 집계와 연결된 계정 과목 ID입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="금액", description="해당 계정의 청구 또는 체크카드 집계 금액입니다."),
    ] = None
    pay_account_id: Annotated[
        str | None,
        Field(title="결제 계정 ID", description="결제에 사용되는 계정 과목 ID입니다."),
    ] = None
    pay_date: Annotated[
        DateValue | None,
        Field(title="결제일", description="청구 또는 체크카드 결제 예정일입니다."),
    ] = None
    start_use_date: Annotated[
        DateValue | None,
        Field(title="사용 시작일", description="집계 대상 사용 기간의 시작일입니다."),
    ] = None
    end_use_date: Annotated[
        DateValue | None,
        Field(title="사용 종료일", description="집계 대상 사용 기간의 종료일입니다."),
    ] = None


class BillReportRow(WhooingModel):
    title: Annotated[
        str | None,
        Field(title="청구 행 이름", description="청구 또는 체크카드 리포트 행의 표시 이름입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="행 금액", description="청구 또는 체크카드 리포트 행의 합계 금액입니다."),
    ] = None
    accounts: Annotated[
        list[BillAccount],
        Field(
            default_factory=list,
            title="청구 계정 목록",
            description="해당 행에 포함된 계정별 청구 정보입니다.",
        ),
    ]


class BillReport(WhooingModel):
    aggregate: Annotated[
        MoneyValue | dict[str, object] | None,
        Field(title="청구 합계", description="청구 또는 체크카드 조회 결과의 전체 집계입니다."),
    ] = None
    rows_type: Annotated[
        str | None,
        Field(title="행 종류", description="청구 또는 체크카드 리포트 행의 분류 기준입니다."),
    ] = None
    rows: Annotated[
        list[BillReportRow],
        Field(
            default_factory=list,
            title="청구 행 목록",
            description="청구 또는 체크카드 리포트 상세 행 목록입니다.",
        ),
    ]


class InOut(WhooingModel):
    account: Annotated[
        AccountGroupValue | str | None,
        Field(title="계정 종류", description="입출금 분석 대상 계정 분류입니다."),
    ] = None
    account_id: Annotated[
        str | None, Field(title="계정 ID", description="입출금 분석 대상 계정 ID입니다.")
    ] = None
    in_money: Annotated[
        MoneyValue | None, Field(title="입금액", description="대상 기간의 입금 합계입니다.")
    ] = None
    out_money: Annotated[
        MoneyValue | None, Field(title="출금액", description="대상 기간의 출금 합계입니다.")
    ] = None
    balance: Annotated[
        MoneyValue | None, Field(title="잔액", description="입출금 분석 기준 잔액입니다.")
    ] = None


class InOutDetail(WhooingModel):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="입출금 집계가 연결된 계정 과목 ID입니다."),
    ] = None
    in_: Annotated[
        MoneyValue | None,
        Field(default=None, alias="in", title="입금액", description="대상 기간의 입금 합계입니다."),
    ]
    out: Annotated[
        MoneyValue | None,
        Field(title="출금액", description="대상 기간의 출금 합계입니다."),
    ] = None
    margin: Annotated[
        MoneyValue | None,
        Field(title="순증감액", description="입금액에서 출금액을 뺀 순증감 금액입니다."),
    ] = None
    balance: Annotated[
        MoneyValue | None,
        Field(title="잔액", description="입출금 집계 기준 잔액입니다."),
    ] = None


class InOutReport(WhooingModel):
    accounts: Annotated[
        list[InOutDetail],
        Field(
            default_factory=list,
            title="계정별 입출금",
            description="계정별 입금, 출금, 순증감, 잔액 목록입니다.",
        ),
    ]
    total: Annotated[
        InOutDetail | None,
        Field(
            title="입출금 합계", description="조회 범위 전체의 입금, 출금, 순증감, 잔액 합계입니다."
        ),
    ] = None


class InOutOverview(WhooingModel):
    assets: Annotated[
        InOutReport | dict[str, object] | None,
        Field(title="자산 입출금", description="자산 계정의 입금, 출금, 순증감 집계입니다."),
    ] = None
    liabilities: Annotated[
        InOutReport | dict[str, object] | None,
        Field(title="부채 입출금", description="부채 계정의 입금, 출금, 순증감 집계입니다."),
    ] = None


class CalendarItem(WhooingModel):
    entry_date: Annotated[
        DateValue | None, Field(title="거래일", description="캘린더 항목의 날짜입니다.")
    ] = None
    entries: Annotated[
        list[Entry] | None,
        Field(title="거래 목록", description="해당 날짜에 포함된 거래 내역 목록입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="일별 금액", description="해당 날짜의 거래 합계 금액입니다."),
    ] = None


class CalendarAggregate(WhooingModel):
    count: Annotated[
        int | None,
        Field(title="거래 건수", description="캘린더 조회 범위의 거래 건수입니다."),
    ] = None
    income: Annotated[
        MoneyValue | None,
        Field(title="수입 합계", description="캘린더 조회 범위의 수입 합계입니다."),
    ] = None
    expenses: Annotated[
        MoneyValue | None,
        Field(title="비용 합계", description="캘린더 조회 범위의 비용 합계입니다."),
    ] = None
    etc: Annotated[
        MoneyValue | None,
        Field(
            title="기타 합계", description="수입과 비용으로 분류되지 않은 캘린더 집계 금액입니다."
        ),
    ] = None


class CalendarDay(WhooingModel):
    day: Annotated[
        int | None,
        Field(title="일", description="캘린더 셀의 일자 값입니다."),
    ] = None
    date: Annotated[
        DateValue | None,
        Field(title="날짜", description="캘린더 셀의 날짜입니다."),
    ] = None
    count: Annotated[
        int | None,
        Field(title="거래 건수", description="해당 날짜의 거래 건수입니다."),
    ] = None
    income: Annotated[
        MoneyValue | None,
        Field(title="수입 합계", description="해당 날짜의 수입 합계입니다."),
    ] = None
    expenses: Annotated[
        MoneyValue | None,
        Field(title="비용 합계", description="해당 날짜의 비용 합계입니다."),
    ] = None
    etc: Annotated[
        MoneyValue | None,
        Field(title="기타 합계", description="해당 날짜의 기타 집계 금액입니다."),
    ] = None
    entries: Annotated[
        list[Entry],
        Field(
            default_factory=list,
            title="거래 목록",
            description="해당 날짜에 포함된 거래 목록입니다.",
        ),
    ]
    is_holiday: Annotated[
        bool | None,
        Field(title="휴일 여부", description="해당 날짜가 휴일인지 여부입니다."),
    ] = None
    label: Annotated[
        str | None,
        Field(title="날짜 라벨", description="캘린더 셀에 표시되는 날짜 라벨입니다."),
    ] = None


class CalendarReport(WhooingModel):
    aggregate: Annotated[
        CalendarAggregate | None,
        Field(title="캘린더 합계", description="캘린더 조회 범위 전체의 집계 값입니다."),
    ] = None
    rows_type: Annotated[
        str | None,
        Field(title="캘린더 행 종류", description="캘린더 응답 행의 구성 방식입니다."),
    ] = None
    rows: Annotated[
        dict[str, dict[str, CalendarDay | dict[str, object]] | list[CalendarDay]],
        Field(
            default_factory=dict,
            title="캘린더 행",
            description="월과 일을 키로 가지는 캘린더 데이터입니다.",
        ),
    ]


class Report(WhooingModel):
    account: Annotated[
        AccountGroupValue | str | None,
        Field(title="계정 종류", description="리포트 대상 계정 분류입니다."),
    ] = None
    account_id: Annotated[
        str | None, Field(title="계정 ID", description="리포트 대상 계정 ID입니다.")
    ] = None
    money: Annotated[
        MoneyValue | None, Field(title="리포트 금액", description="리포트 행의 집계 금액입니다.")
    ] = None
    entries: Annotated[
        list[Entry] | None,
        Field(title="거래 목록", description="리포트 행에 포함된 거래 내역 목록입니다."),
    ] = None


class ReportAccount(WhooingModel):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="리포트 집계가 연결된 계정 과목 ID입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="집계 금액", description="해당 계정의 리포트 집계 금액입니다."),
    ] = None


class ReportAccountGroup(WhooingModel):
    accounts: Annotated[
        dict[str, MoneyValue],
        Field(
            default_factory=dict,
            title="계정별 집계",
            description="계정 과목 ID를 키로 가지는 리포트 집계입니다.",
        ),
    ]
    total: Annotated[
        MoneyValue | None,
        Field(title="합계", description="해당 계정 분류의 리포트 합계입니다."),
    ] = None
    total_steady: Annotated[
        MoneyValue | None,
        Field(title="고정 합계", description="고정성 계정 또는 항목의 리포트 합계입니다."),
    ] = None
    total_floating: Annotated[
        MoneyValue | None,
        Field(title="변동 합계", description="변동성 계정 또는 항목의 리포트 합계입니다."),
    ] = None


class ReportResult(WhooingModel):
    income: Annotated[
        ReportAccountGroup | None,
        Field(title="수입 리포트", description="수입 계정 분류의 리포트 집계입니다."),
    ] = None
    expenses: Annotated[
        ReportAccountGroup | None,
        Field(title="비용 리포트", description="비용 계정 분류의 리포트 집계입니다."),
    ] = None
    net_income: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="순수입 리포트", description="수입에서 비용을 제외한 순수입 집계입니다."),
    ] = None


class ReportSummary(WhooingModel):
    account: Annotated[
        AccountGroupValue | str | None,
        Field(title="계정 종류", description="요약 대상 계정 분류입니다."),
    ] = None
    income: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="수입 합계", description="리포트 요약 또는 계정별 수입 집계입니다."),
    ] = None
    expenses: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="비용 합계", description="리포트 요약 또는 계정별 비용 집계입니다."),
    ] = None
    assets: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="자산 합계", description="리포트 요약 또는 계정별 자산 집계입니다."),
    ] = None
    liabilities: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="부채 합계", description="리포트 요약 또는 계정별 부채 집계입니다."),
    ] = None
    capital: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="자본 합계", description="리포트 요약 또는 계정별 자본 집계입니다."),
    ] = None
    net_income: Annotated[
        ReportAccountGroup | MoneyValue | None,
        Field(title="순수입 합계", description="수입에서 비용을 제외한 순수입 집계입니다."),
    ] = None


class CustomReportRow(WhooingModel):
    id: Annotated[
        IdentifierValue | None,
        Field(title="사용자 정의 리포트 행 ID", description="사용자 정의 리포트 행 식별자입니다."),
    ] = None
    row_id: Annotated[
        IdentifierValue | None,
        Field(title="사용자 정의 리포트 행 ID", description="사용자 정의 리포트 행 식별자입니다."),
    ] = None
    report: Annotated[
        str | None,
        Field(title="보고서 종류", description="사용자 정의 행이 속한 보고서 종류입니다."),
    ] = None
    title: Annotated[
        str | None,
        Field(title="사용자 정의 행 이름", description="사용자 정의 리포트 행의 표시 이름입니다."),
    ] = None
    plus: Annotated[
        list[str],
        Field(
            default_factory=list,
            title="더할 항목",
            description="행 계산식에서 더할 계정 항목 목록입니다.",
        ),
    ]
    minus: Annotated[
        list[str],
        Field(
            default_factory=list,
            title="뺄 항목",
            description="행 계산식에서 뺄 계정 항목 목록입니다.",
        ),
    ]
    addminus: Annotated[
        str | None,
        Field(title="추가 계산식", description="plus-minus 합산값 x에 적용할 사칙연산 식입니다."),
    ] = None
    money: Annotated[
        MoneyValue | None,
        Field(title="계산 금액", description="사용자 정의 리포트 행의 계산 결과 금액입니다."),
    ] = None
    account: Annotated[
        AccountGroupValue | str | None,
        Field(title="계정 종류", description="사용자 정의 행과 연결된 계정 분류입니다."),
    ] = None
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="사용자 정의 행과 연결된 계정 과목 ID입니다."),
    ] = None


class CustomReportRowsResult(WhooingModel):
    status: Annotated[
        str | None,
        Field(title="처리 상태", description="사용자 정의 보고서 행 API의 처리 상태입니다."),
    ] = None
    rows: Annotated[
        list[CustomReportRow],
        Field(
            default_factory=list,
            title="사용자 정의 행 목록",
            description="사용자 정의 보고서 행 목록입니다.",
        ),
    ]


class PostIt(WhooingModel):
    post_it_id: Annotated[
        IdentifierValue | None,
        Field(title="포스트잇 ID", description="후잉 포스트잇 메모 식별자입니다."),
    ] = None
    section_id: Annotated[
        str | None,
        Field(title="섹션 ID", description="포스트잇이 속한 가계부 섹션 ID입니다."),
    ] = None
    title: Annotated[
        str | None, Field(title="포스트잇 제목", description="포스트잇 메모 제목입니다.")
    ] = None
    contents: Annotated[
        str | None, Field(title="포스트잇 내용", description="포스트잇 메모 본문입니다.")
    ] = None
    position: Annotated[
        str | None,
        Field(title="포스트잇 위치", description="후잉 화면에서 포스트잇이 배치된 위치 값입니다."),
    ] = None
    color: Annotated[
        str | None, Field(title="포스트잇 색상", description="포스트잇 메모 색상 값입니다.")
    ] = None


class Message(WhooingModel):
    message_id: Annotated[
        IdentifierValue | None,
        Field(title="쪽지 ID", description="후잉 메시지 또는 쪽지 식별자입니다."),
    ] = None
    opponent_user_id: Annotated[
        IdentifierValue | None,
        Field(title="상대 사용자 ID", description="메시지 상대방의 후잉 사용자 ID입니다."),
    ] = None
    opponent_username: Annotated[
        str | None,
        Field(title="상대 사용자 이름", description="메시지 상대방의 후잉 표시 이름입니다."),
    ] = None
    opponent_image_url: Annotated[
        str | None,
        Field(
            title="상대 프로필 이미지 URL", description="메시지 상대방의 프로필 이미지 URL입니다."
        ),
    ] = None
    message: Annotated[str | None, Field(title="메시지", description="메시지 본문입니다.")] = None
    contents: Annotated[
        str | None,
        Field(title="메시지 내용", description="메시지 응답에서 제공되는 본문 내용입니다."),
    ] = None
    summary: Annotated[
        str | None,
        Field(title="메시지 요약", description="메시지 목록에서 제공되는 본문 요약입니다."),
    ] = None
    datetime: Annotated[
        TimestampValue | None,
        Field(title="메시지 시각", description="메시지 작성 Unix timestamp입니다."),
    ] = None
    timestamp: Annotated[
        TimestampValue | None,
        Field(
            title="메시지 timestamp", description="메시지 목록에서 제공되는 Unix timestamp입니다."
        ),
    ] = None
    timestamp_id: Annotated[
        IdentifierValue | None,
        Field(
            title="timestamp ID",
            description="메시지 목록 정렬 또는 페이징에 쓰이는 timestamp 식별자입니다.",
        ),
    ] = None
    type: Annotated[
        str | None,
        Field(title="메시지 종류", description="메시지 상세 응답에서 제공되는 메시지 종류입니다."),
    ] = None
    attachments: Annotated[
        list[dict[str, object]],
        Field(
            default_factory=list,
            title="첨부 파일 목록",
            description="메시지에 연결된 첨부 파일 목록입니다.",
        ),
    ]
    read: Annotated[
        YnFlag | str | bool | None,
        Field(title="읽음 여부", description="메시지 읽음 상태입니다."),
    ] = None


class BbsPost(WhooingModel):
    bbs_id: Annotated[
        IdentifierValue | None,
        Field(title="게시글 ID", description="후잉 게시판 글 식별자입니다."),
    ] = None
    category: Annotated[
        str | None, Field(title="게시판 카테고리", description="게시글이 속한 게시판 분류입니다.")
    ] = None
    subject: Annotated[
        str | None, Field(title="게시글 제목", description="후잉 게시판 목록 응답의 제목입니다.")
    ] = None
    title: Annotated[str | None, Field(title="게시글 제목", description="게시글 제목입니다.")] = (
        None
    )
    contents: Annotated[
        str | None, Field(title="게시글 내용", description="게시글 본문입니다.")
    ] = None
    user_id: Annotated[
        IdentifierValue | None,
        Field(title="작성자 ID", description="게시글 작성자의 후잉 사용자 ID입니다."),
    ] = None
    datetime: Annotated[
        TimestampValue | None,
        Field(title="작성 시각", description="게시글 작성 Unix timestamp입니다."),
    ] = None
    timestamp: Annotated[
        TimestampValue | None,
        Field(
            title="게시글 timestamp", description="게시글 목록 응답의 작성 Unix timestamp입니다."
        ),
    ] = None
    updated_at: Annotated[
        TimestampValue | None,
        Field(title="수정 시각", description="게시글이 마지막으로 수정된 Unix timestamp입니다."),
    ] = None
    comments: Annotated[
        int | list[BbsComment] | None,
        Field(title="댓글", description="목록에서는 댓글 수, 상세에서는 댓글 목록으로 제공됩니다."),
    ] = None
    writer: Annotated[
        dict[str, object] | None,
        Field(title="작성자", description="게시글 작성자 정보입니다."),
    ] = None
    group: Annotated[
        str | None,
        Field(title="게시글 그룹", description="게시글이 속한 게시판 그룹 값입니다."),
    ] = None
    etc: Annotated[
        str | dict[str, object] | None,
        Field(title="기타 정보", description="게시글 응답에 포함되는 기타 정보입니다."),
    ] = None
    hits: Annotated[
        int | None,
        Field(title="조회수", description="게시글 조회 수입니다."),
    ] = None
    is_attachment: Annotated[
        bool | int | str | None,
        Field(title="첨부 여부", description="게시글에 첨부 파일이 있는지 나타냅니다."),
    ] = None
    language: Annotated[
        str | None,
        Field(title="언어", description="게시글 언어 코드입니다."),
    ] = None
    latest: Annotated[
        TimestampValue | str | None,
        Field(title="최근 활동", description="게시글의 최근 댓글 또는 활동 시각입니다."),
    ] = None
    notice: Annotated[
        bool | int | str | None,
        Field(title="공지 여부", description="게시글이 공지인지 여부입니다."),
    ] = None
    recommandation: Annotated[
        int | None,
        Field(title="추천 수", description="게시글 추천 수입니다."),
    ] = None
    shorturl: Annotated[
        str | None,
        Field(title="짧은 URL", description="게시글에 연결된 짧은 URL입니다."),
    ] = None
    thumb_path: Annotated[
        str | None,
        Field(title="썸네일 경로", description="게시글 썸네일 이미지 경로입니다."),
    ] = None


class BbsComment(WhooingModel):
    comment_id: Annotated[
        IdentifierValue | None,
        Field(title="댓글 ID", description="후잉 게시판 댓글 식별자입니다."),
    ] = None
    addition_id: Annotated[
        IdentifierValue | None,
        Field(title="답글 ID", description="댓글에 달린 답글 또는 추가 댓글 식별자입니다."),
    ] = None
    contents: Annotated[
        str | None, Field(title="댓글 내용", description="댓글 또는 답글 본문입니다.")
    ] = None
    user_id: Annotated[
        IdentifierValue | None,
        Field(title="작성자 ID", description="댓글 작성자의 후잉 사용자 ID입니다."),
    ] = None
    datetime: Annotated[
        TimestampValue | None,
        Field(title="작성 시각", description="댓글 작성 Unix timestamp입니다."),
    ] = None
    replies: Annotated[
        list[BbsComment] | None,
        Field(title="답글 목록", description="댓글에 연결된 답글 목록입니다."),
    ] = None


class UploadInfo(WhooingModel):
    uuid: Annotated[
        str | None,
        Field(
            title="업로드 UUID", description="파일 업로드 완료 처리에 사용하는 업로드 식별자입니다."
        ),
    ] = None
    url: Annotated[
        str | None,
        Field(title="업로드 URL", description="파일을 업로드할 대상 URL입니다."),
    ] = None
    fields: Annotated[
        dict[str, object] | None,
        Field(
            title="업로드 필드", description="파일 업로드 요청에 함께 전송해야 하는 폼 필드입니다."
        ),
    ] = None
    file_info: Annotated[
        UploadFileInfo | None,
        Field(
            title="파일 정보", description="업로드 준비 응답에서 반환되는 파일 메타데이터입니다."
        ),
    ] = None


class UploadFileInfo(WhooingModel):
    uuid: Annotated[
        str | None,
        Field(title="파일 UUID", description="업로드 대상 파일을 식별하는 UUID입니다."),
    ] = None
    name: Annotated[
        str | None,
        Field(title="파일 이름", description="업로드 대상 파일 이름입니다."),
    ] = None
    size: Annotated[
        int | None,
        Field(title="파일 크기", description="업로드 대상 파일 크기입니다."),
    ] = None
    mime_type: Annotated[
        str | None,
        Field(
            alias="mimeType",
            title="MIME 타입",
            description="업로드 대상 파일의 MIME 타입입니다.",
        ),
    ] = None


class Notification(WhooingModel):
    notification_id: Annotated[
        IdentifierValue | None,
        Field(title="알림 ID", description="후잉 알림 식별자입니다."),
    ] = None
    section_id: Annotated[
        str | None,
        Field(title="섹션 ID", description="알림과 연결된 가계부 섹션 ID입니다."),
    ] = None
    title: Annotated[str | None, Field(title="알림 제목", description="알림 제목입니다.")] = None
    contents: Annotated[str | None, Field(title="알림 내용", description="알림 본문입니다.")] = None
    summary: Annotated[
        str | None,
        Field(title="알림 요약", description="알림 목록에서 표시되는 요약 문구입니다."),
    ] = None
    link: Annotated[
        str | None,
        Field(title="알림 링크", description="알림을 눌렀을 때 이동할 링크입니다."),
    ] = None
    nav: Annotated[
        str | dict[str, object] | None,
        Field(
            title="알림 내비게이션", description="후잉 UI 내부 이동을 위한 내비게이션 정보입니다."
        ),
    ] = None
    noti_id: Annotated[
        IdentifierValue | None,
        Field(title="알림 ID", description="후잉 알림 목록의 알림 식별자입니다."),
    ] = None
    timestamp: Annotated[
        TimestampValue | None,
        Field(title="알림 timestamp", description="알림이 발생한 Unix timestamp입니다."),
    ] = None
    datetime: Annotated[
        TimestampValue | None,
        Field(title="알림 시각", description="알림 발생 Unix timestamp입니다."),
    ] = None
    read: Annotated[
        YnFlag | str | bool | None,
        Field(title="읽음 여부", description="알림 읽음 상태입니다."),
    ] = None


class NotificationBucket(WhooingModel):
    badge_count: Annotated[
        int | None,
        Field(
            alias="badgeCount",
            title="배지 수",
            description="후잉 UI에서 표시되는 알림 배지 수입니다.",
        ),
    ] = None
    last_timestamp: Annotated[
        TimestampValue | None,
        Field(
            alias="lastTimestamp",
            title="마지막 알림 시각",
            description="가장 최근 알림의 Unix timestamp입니다.",
        ),
    ] = None
    rows: Annotated[
        list[Notification],
        Field(default_factory=list, title="알림 목록", description="알림 상세 행 목록입니다."),
    ]


class Notifications(WhooingModel):
    account: Annotated[
        int | dict[str, object] | None,
        Field(title="계정 알림", description="계정 관련 알림 상태 또는 상세 정보입니다."),
    ] = None
    messages: Annotated[
        int | list[Message] | dict[str, object] | None,
        Field(title="메시지 알림", description="메시지 관련 알림 상태 또는 상세 정보입니다."),
    ] = None
    messages_count: Annotated[
        int | None,
        Field(title="메시지 알림 수", description="읽지 않은 메시지 또는 메시지 알림 개수입니다."),
    ] = None
    new_releases: Annotated[
        int | list[dict[str, object]] | None,
        Field(
            alias="newReleases",
            title="새 릴리스 알림",
            description="새 릴리스 관련 알림 상태 또는 목록입니다.",
        ),
    ] = None
    notification: Annotated[
        NotificationBucket | None,
        Field(title="일반 알림", description="일반 알림 배지와 알림 행 목록입니다."),
    ] = None
    outside: Annotated[
        int | dict[str, object] | None,
        Field(title="외부 알림", description="외부 연동 관련 알림 상태 또는 상세 정보입니다."),
    ] = None
    payment: Annotated[
        int | dict[str, object] | None,
        Field(title="결제 알림", description="결제 관련 알림 상태 또는 상세 정보입니다."),
    ] = None
