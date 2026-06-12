from __future__ import annotations

from typing import Annotated

from pydantic import Field

from whooing._pydantic_models.base import WhooingModel


class User(WhooingModel):
    user_id: Annotated[
        int | None, Field(title="사용자 ID", description="후잉 사용자 식별자입니다.")
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
        int | None,
        Field(title="마지막 로그인 시각", description="마지막 로그인 시각의 Unix timestamp입니다."),
    ] = None
    created_timestamp: Annotated[
        int | None,
        Field(title="생성 시각", description="후잉 계정 생성 시각의 Unix timestamp입니다."),
    ] = None
    modified_timestamp: Annotated[
        int | None,
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
        int | None,
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
        str | int | float | None,
        Field(title="포인트", description="사용자 계정에 표시되는 후잉 포인트 값입니다."),
    ] = None
    mileage: Annotated[
        int | float | None,
        Field(title="마일리지", description="사용자 계정의 후잉 마일리지 값입니다."),
    ] = None
    sound: Annotated[
        str | None,
        Field(title="소리 설정", description="후잉 UI의 알림음 사용 여부 설정입니다."),
    ] = None


class UserLog(WhooingModel):
    id: Annotated[int | None, Field(title="로그 ID", description="사용자 로그 식별자입니다.")] = (
        None
    )
    contents: Annotated[
        str | None,
        Field(title="로그 내용", description="사용자 활동 로그의 내용입니다."),
    ] = None
    datetime: Annotated[
        int | None,
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
        int | None,
        Field(title="포인트 로그 ID", description="포인트 변동 로그 식별자입니다."),
    ] = None
    datetime: Annotated[
        int | None,
        Field(title="포인트 변동 시각", description="포인트가 변동된 Unix timestamp입니다."),
    ] = None
    description: Annotated[
        str | None,
        Field(title="포인트 설명", description="포인트 변동 사유 설명입니다."),
    ] = None
    point: Annotated[
        int | float | None,
        Field(title="포인트", description="변동된 포인트 값입니다."),
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
    currency: Annotated[
        str | None,
        Field(title="섹션 통화", description="해당 섹션에서 사용하는 통화 코드입니다."),
    ] = None
    isolation: Annotated[
        str | None,
        Field(title="섹션 격리 여부", description="섹션 데이터 격리 설정 값입니다."),
    ] = None
    total_assets: Annotated[
        int | float | None,
        Field(title="총 자산", description="섹션 내 전체 자산 합계입니다."),
    ] = None
    total_liabilities: Annotated[
        int | float | None,
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
        str | None,
        Field(title="계정 종류", description="자산, 부채, 자본, 수입, 비용 등 계정 분류입니다."),
    ] = None
    title: Annotated[
        str | None, Field(title="계정 이름", description="계정 과목 표시 이름입니다.")
    ] = None
    memo: Annotated[
        str | None, Field(title="계정 메모", description="계정 과목에 대한 설명 메모입니다.")
    ] = None
    open_date: Annotated[
        int | str | None,
        Field(title="개설일", description="계정 과목이 시작되는 날짜입니다."),
    ] = None
    close_date: Annotated[
        int | str | None,
        Field(title="종료일", description="계정 과목이 종료되는 날짜입니다."),
    ] = None
    category: Annotated[
        str | None,
        Field(title="계정 카테고리", description="계정 과목의 세부 카테고리입니다."),
    ] = None
    opt_use_date: Annotated[
        str | int | None,
        Field(title="사용일 옵션", description="카드 등 특수 계정에서 사용하는 사용일 옵션입니다."),
    ] = None
    opt_pay_date: Annotated[
        str | int | None,
        Field(title="결제일 옵션", description="카드 등 특수 계정에서 사용하는 결제일 옵션입니다."),
    ] = None
    opt_pay_account_id: Annotated[
        str | None,
        Field(title="결제 계정 ID", description="카드 결제 등에 연결된 지불 계정 식별자입니다."),
    ] = None


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
        int | str | None,
        Field(title="거래 ID", description="후잉 거래 내역 식별자입니다."),
    ] = None
    entry_date: Annotated[
        int | str | None,
        Field(title="거래일", description="거래가 발생한 날짜입니다."),
    ] = None
    l_account: Annotated[
        str | None,
        Field(title="왼쪽 계정 종류", description="복식부기 거래의 왼쪽 계정 분류입니다."),
    ] = None
    l_account_id: Annotated[
        str | None,
        Field(title="왼쪽 계정 ID", description="복식부기 거래의 왼쪽 계정 과목 식별자입니다."),
    ] = None
    r_account: Annotated[
        str | None,
        Field(title="오른쪽 계정 종류", description="복식부기 거래의 오른쪽 계정 분류입니다."),
    ] = None
    r_account_id: Annotated[
        str | None,
        Field(title="오른쪽 계정 ID", description="복식부기 거래의 오른쪽 계정 과목 식별자입니다."),
    ] = None
    item: Annotated[
        str | None, Field(title="거래 항목", description="거래 내역의 항목명입니다.")
    ] = None
    money: Annotated[int | float | None, Field(title="금액", description="거래 금액입니다.")] = None
    memo: Annotated[
        str | None, Field(title="거래 메모", description="거래 내역에 적힌 메모입니다.")
    ] = None
    timestamp: Annotated[
        int | None,
        Field(title="기록 시각", description="거래가 기록되거나 수정된 Unix timestamp입니다."),
    ] = None


class EntryAnalysis(WhooingModel):
    account: Annotated[
        str | None, Field(title="계정 종류", description="분석 대상 계정 분류입니다.")
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
        int | float | None, Field(title="합계 금액", description="분석 결과의 합계 금액입니다.")
    ] = None
    count: Annotated[
        int | None, Field(title="건수", description="분석 결과에 포함된 거래 건수입니다.")
    ] = None
    entries: Annotated[
        list[Entry] | None,
        Field(title="거래 목록", description="분석 결과에 포함된 거래 내역 목록입니다."),
    ] = None


class FrequentItem(WhooingModel):
    item_id: Annotated[
        str | int | None,
        Field(title="자주 쓰는 항목 ID", description="자주 쓰는 항목 식별자입니다."),
    ] = None
    section_id: Annotated[
        str | None, Field(title="섹션 ID", description="항목이 속한 섹션 ID입니다.")
    ] = None
    item: Annotated[
        str | None, Field(title="항목명", description="자주 쓰는 거래 항목명입니다.")
    ] = None
    money: Annotated[
        int | float | None, Field(title="기본 금액", description="항목에 설정된 기본 금액입니다.")
    ] = None
    memo: Annotated[
        str | None, Field(title="메모", description="항목에 설정된 기본 메모입니다.")
    ] = None
    l_account: Annotated[
        str | None,
        Field(title="왼쪽 계정 종류", description="항목에 연결된 왼쪽 계정 분류입니다."),
    ] = None
    l_account_id: Annotated[
        str | None,
        Field(title="왼쪽 계정 ID", description="항목에 연결된 왼쪽 계정 과목 ID입니다."),
    ] = None
    r_account: Annotated[
        str | None,
        Field(title="오른쪽 계정 종류", description="항목에 연결된 오른쪽 계정 분류입니다."),
    ] = None
    r_account_id: Annotated[
        str | None,
        Field(title="오른쪽 계정 ID", description="항목에 연결된 오른쪽 계정 과목 ID입니다."),
    ] = None


class MonthlyItem(FrequentItem):
    start_date: Annotated[
        int | str | None,
        Field(title="시작일", description="월별 반복 항목이 시작되는 날짜입니다."),
    ] = None
    end_date: Annotated[
        int | str | None,
        Field(title="종료일", description="월별 반복 항목이 종료되는 날짜입니다."),
    ] = None


class Budget(WhooingModel):
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="예산이 설정된 계정 과목 식별자입니다."),
    ] = None
    target_ym: Annotated[
        int | str | None,
        Field(title="대상 연월", description="예산이 적용되는 대상 연월입니다."),
    ] = None
    money: Annotated[
        int | float | None, Field(title="예산 금액", description="설정된 예산 금액입니다.")
    ] = None


class BudgetGoal(WhooingModel):
    section_id: Annotated[
        str | None, Field(title="섹션 ID", description="예산 목표가 속한 섹션 ID입니다.")
    ] = None
    start_date: Annotated[
        int | str | None,
        Field(title="시작일", description="예산 목표 기간의 시작 날짜입니다."),
    ] = None
    end_date: Annotated[
        int | str | None,
        Field(title="종료일", description="예산 목표 기간의 종료 날짜입니다."),
    ] = None


class CapitalGoal(WhooingModel):
    section_id: Annotated[
        str | None, Field(title="섹션 ID", description="자본 목표가 속한 섹션 ID입니다.")
    ] = None
    monthly_goals: Annotated[
        dict[str, int | float] | None,
        Field(title="월별 자본 목표", description="월 단위로 설정된 자본 목표 금액입니다."),
    ] = None


class Bill(WhooingModel):
    account_id: Annotated[
        str | None, Field(title="계정 ID", description="청구서와 연결된 계정 ID입니다.")
    ] = None
    title: Annotated[
        str | None, Field(title="청구서 이름", description="청구 항목 이름입니다.")
    ] = None
    money: Annotated[
        int | float | None, Field(title="청구 금액", description="청구되거나 예정된 금액입니다.")
    ] = None
    entry_date: Annotated[
        int | str | None, Field(title="청구일", description="청구 또는 결제 예정 날짜입니다.")
    ] = None


class Checkcard(Bill):
    pass


class InOut(WhooingModel):
    account: Annotated[
        str | None, Field(title="계정 종류", description="입출금 분석 대상 계정 분류입니다.")
    ] = None
    account_id: Annotated[
        str | None, Field(title="계정 ID", description="입출금 분석 대상 계정 ID입니다.")
    ] = None
    in_money: Annotated[
        int | float | None, Field(title="입금액", description="대상 기간의 입금 합계입니다.")
    ] = None
    out_money: Annotated[
        int | float | None, Field(title="출금액", description="대상 기간의 출금 합계입니다.")
    ] = None
    balance: Annotated[
        int | float | None, Field(title="잔액", description="입출금 분석 기준 잔액입니다.")
    ] = None


class CalendarItem(WhooingModel):
    entry_date: Annotated[
        int | str | None, Field(title="거래일", description="캘린더 항목의 날짜입니다.")
    ] = None
    entries: Annotated[
        list[Entry] | None,
        Field(title="거래 목록", description="해당 날짜에 포함된 거래 내역 목록입니다."),
    ] = None
    money: Annotated[
        int | float | None,
        Field(title="일별 금액", description="해당 날짜의 거래 합계 금액입니다."),
    ] = None


class Report(WhooingModel):
    account: Annotated[
        str | None, Field(title="계정 종류", description="리포트 대상 계정 분류입니다.")
    ] = None
    account_id: Annotated[
        str | None, Field(title="계정 ID", description="리포트 대상 계정 ID입니다.")
    ] = None
    money: Annotated[
        int | float | None, Field(title="리포트 금액", description="리포트 행의 집계 금액입니다.")
    ] = None
    entries: Annotated[
        list[Entry] | None,
        Field(title="거래 목록", description="리포트 행에 포함된 거래 내역 목록입니다."),
    ] = None


class ReportSummary(WhooingModel):
    account: Annotated[
        str | None, Field(title="계정 종류", description="요약 대상 계정 분류입니다.")
    ] = None
    income: Annotated[
        int | float | None, Field(title="수입 합계", description="리포트 요약의 수입 합계입니다.")
    ] = None
    expenses: Annotated[
        int | float | None, Field(title="비용 합계", description="리포트 요약의 비용 합계입니다.")
    ] = None
    assets: Annotated[
        int | float | None, Field(title="자산 합계", description="리포트 요약의 자산 합계입니다.")
    ] = None
    liabilities: Annotated[
        int | float | None, Field(title="부채 합계", description="리포트 요약의 부채 합계입니다.")
    ] = None
    capital: Annotated[
        int | float | None, Field(title="자본 합계", description="리포트 요약의 자본 합계입니다.")
    ] = None


class CustomReportRow(WhooingModel):
    row_id: Annotated[
        str | int | None,
        Field(title="사용자 정의 리포트 행 ID", description="사용자 정의 리포트 행 식별자입니다."),
    ] = None
    title: Annotated[
        str | None,
        Field(title="사용자 정의 행 이름", description="사용자 정의 리포트 행의 표시 이름입니다."),
    ] = None
    account: Annotated[
        str | None,
        Field(title="계정 종류", description="사용자 정의 행과 연결된 계정 분류입니다."),
    ] = None
    account_id: Annotated[
        str | None,
        Field(title="계정 ID", description="사용자 정의 행과 연결된 계정 과목 ID입니다."),
    ] = None


class PostIt(WhooingModel):
    post_it_id: Annotated[
        int | str | None,
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
        int | str | None,
        Field(title="쪽지 ID", description="후잉 메시지 또는 쪽지 식별자입니다."),
    ] = None
    opponent_user_id: Annotated[
        int | str | None,
        Field(title="상대 사용자 ID", description="메시지 상대방의 후잉 사용자 ID입니다."),
    ] = None
    message: Annotated[str | None, Field(title="메시지", description="메시지 본문입니다.")] = None
    contents: Annotated[
        str | None,
        Field(title="메시지 내용", description="메시지 응답에서 제공되는 본문 내용입니다."),
    ] = None
    datetime: Annotated[
        int | None, Field(title="메시지 시각", description="메시지 작성 Unix timestamp입니다.")
    ] = None
    read: Annotated[
        str | bool | None,
        Field(title="읽음 여부", description="메시지 읽음 상태입니다."),
    ] = None


class BbsPost(WhooingModel):
    bbs_id: Annotated[
        int | str | None,
        Field(title="게시글 ID", description="후잉 게시판 글 식별자입니다."),
    ] = None
    category: Annotated[
        str | None, Field(title="게시판 카테고리", description="게시글이 속한 게시판 분류입니다.")
    ] = None
    title: Annotated[str | None, Field(title="게시글 제목", description="게시글 제목입니다.")] = (
        None
    )
    contents: Annotated[
        str | None, Field(title="게시글 내용", description="게시글 본문입니다.")
    ] = None
    user_id: Annotated[
        int | None, Field(title="작성자 ID", description="게시글 작성자의 후잉 사용자 ID입니다.")
    ] = None
    datetime: Annotated[
        int | None, Field(title="작성 시각", description="게시글 작성 Unix timestamp입니다.")
    ] = None
    comments: Annotated[
        list[BbsComment] | None,
        Field(title="댓글 목록", description="게시글에 연결된 댓글 목록입니다."),
    ] = None


class BbsComment(WhooingModel):
    comment_id: Annotated[
        str | int | None,
        Field(title="댓글 ID", description="후잉 게시판 댓글 식별자입니다."),
    ] = None
    addition_id: Annotated[
        str | int | None,
        Field(title="답글 ID", description="댓글에 달린 답글 또는 추가 댓글 식별자입니다."),
    ] = None
    contents: Annotated[
        str | None, Field(title="댓글 내용", description="댓글 또는 답글 본문입니다.")
    ] = None
    user_id: Annotated[
        int | None, Field(title="작성자 ID", description="댓글 작성자의 후잉 사용자 ID입니다.")
    ] = None
    datetime: Annotated[
        int | None, Field(title="작성 시각", description="댓글 작성 Unix timestamp입니다.")
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


class Notification(WhooingModel):
    notification_id: Annotated[
        int | str | None,
        Field(title="알림 ID", description="후잉 알림 식별자입니다."),
    ] = None
    section_id: Annotated[
        str | None,
        Field(title="섹션 ID", description="알림과 연결된 가계부 섹션 ID입니다."),
    ] = None
    title: Annotated[str | None, Field(title="알림 제목", description="알림 제목입니다.")] = None
    contents: Annotated[str | None, Field(title="알림 내용", description="알림 본문입니다.")] = None
    datetime: Annotated[
        int | None, Field(title="알림 시각", description="알림 발생 Unix timestamp입니다.")
    ] = None
    read: Annotated[
        str | bool | None,
        Field(title="읽음 여부", description="알림 읽음 상태입니다."),
    ] = None
