from __future__ import annotations

from whooing import (
    AccountInput,
    BasicTotalBudgetInput,
    BbsCommentInput,
    BbsPostInput,
    BudgetGoalInput,
    BudgetInput,
    CapitalGoalInput,
    EntryInput,
    FrequentItemInput,
    MessageInput,
    MonthlyItemInput,
    PostItInput,
    SectionInput,
    UserInput,
)
from whooing.types import RequestData


def assert_request_data(data: RequestData, expected_keys: set[str]) -> None:
    assert set(data) == expected_keys
    assert all(value is not None for value in data.values())


def test_static_request_models_emit_documented_field_names() -> None:
    assert_request_data(
        UserInput(nickname="flynn", language="ko", timezone="Asia/Seoul").to_request_data(),
        {"nickname", "language", "timezone"},
    )
    assert_request_data(
        SectionInput(title="개인", currency="KRW", memo="memo").to_request_data(),
        {"title", "currency", "memo"},
    )
    assert_request_data(
        AccountInput(
            title="현금",
            memo="memo",
            open_date=20260101,
            close_date=20261231,
            currency="KRW",
            initial_money=1000,
            order=1,
            group="assets",
        ).to_request_data(),
        {
            "title",
            "memo",
            "open_date",
            "close_date",
            "currency",
            "initial_money",
            "order",
            "group",
        },
    )
    assert_request_data(
        PostItInput(
            section_id="s1",
            title="메모",
            contents="내용",
            position="10,20",
            color="yellow",
        ).to_request_data(),
        {"section_id", "title", "contents", "position", "color"},
    )
    assert_request_data(
        EntryInput(
            entry_date=20260607,
            left_account="expenses",
            left_account_id="x1",
            right_account="assets",
            right_account_id="x2",
            item="커피",
            money=5000,
            memo="memo",
        ).to_request_data(),
        {
            "entry_date",
            "l_account",
            "l_account_id",
            "r_account",
            "r_account_id",
            "item",
            "money",
            "memo",
        },
    )


def test_dynamic_request_models_emit_documented_base_fields_and_dynamic_keys() -> None:
    assert_request_data(
        BudgetInput(target_ym=202606, amounts_by_account_id={"x1": 1000}).to_request_data(),
        {"target_ym", "x1"},
    )
    assert_request_data(
        BasicTotalBudgetInput(
            start_date=202601,
            end_date=202612,
            monthly_totals={1: 1000},
        ).to_request_data(),
        {"start_date", "end_date", "1"},
    )
    assert_request_data(
        BudgetGoalInput(start_date=202601, end_date=202612, extra_fields={"x1": 1000})
        .to_request_data(),
        {"start_date", "end_date", "x1"},
    )
    assert_request_data(
        CapitalGoalInput(monthly_goals={1: 1000, "12": 12000}).to_request_data(),
        {"1", "12"},
    )


def test_extra_field_request_models_preserve_explicit_extensions() -> None:
    assert_request_data(
        FrequentItemInput(
            section_id="s1",
            item="커피",
            money=5000,
            memo="memo",
            left_account="expenses",
            left_account_id="x1",
            right_account="assets",
            right_account_id="x2",
            extra_fields={"custom": "value"},
        ).to_request_data(),
        {
            "section_id",
            "item",
            "money",
            "memo",
            "l_account",
            "l_account_id",
            "r_account",
            "r_account_id",
            "custom",
        },
    )
    assert_request_data(
        MonthlyItemInput(
            section_id="s1",
            item="월세",
            money=500000,
            memo="memo",
            start_date=202601,
            end_date=202612,
            extra_fields={"custom": "value"},
        ).to_request_data(),
        {"section_id", "item", "money", "memo", "start_date", "end_date", "custom"},
    )
    assert_request_data(
        BbsPostInput(title="제목", contents="본문", extra_fields={"tag": "api"})
        .to_request_data(),
        {"title", "contents", "tag"},
    )
    assert_request_data(
        BbsCommentInput(contents="댓글", extra_fields={"tag": "api"}).to_request_data(),
        {"contents", "tag"},
    )


def test_message_input_normalizes_multiple_user_ids() -> None:
    assert MessageInput(opponent_user_ids=[1, "2"], message="hello").to_request_data() == {
        "opponent_user_ids": "1,2",
        "message": "hello",
    }
