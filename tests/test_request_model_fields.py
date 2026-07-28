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
        UserInput(
            username="flynn",
            country="KR",
            language="ko",
            timezone="Asia/Seoul",
            currency="KRW",
        ).to_request_data(),
        {"username", "country", "language", "timezone", "currency"},
    )
    assert_request_data(
        SectionInput(title="개인", currency="KRW", memo="memo").to_request_data(),
        {"title", "currency", "memo"},
    )
    assert_request_data(
        AccountInput(
            account_type="account",
            open_date=20260101,
            close_date=20261231,
            title="현금",
            memo="memo",
            category="normal",
            opt_use_date="p1",
            opt_pay_date=25,
            opt_pay_account_id="x2",
        ).to_request_data(),
        {
            "type",
            "open_date",
            "close_date",
            "title",
            "memo",
            "category",
            "opt_use_date",
            "opt_pay_date",
            "opt_pay_account_id",
        },
    )
    assert_request_data(
        PostItInput(
            section_id="s1",
            page="_main/index",
            contents="내용",
            everywhere="n",
            color="ffbd94",
        ).to_request_data(),
        {"section_id", "page", "contents", "everywhere", "color"},
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
            monthly_totals={month: month * 1000 for month in range(1, 13)},
        ).to_request_data(),
        {"start_date", "end_date", *(str(month) for month in range(1, 13))},
    )
    assert_request_data(
        BudgetGoalInput(
            base_ym=202601,
            goal_ym=202712,
            goal_money=50_000_000,
            base_money=10_000_000,
            split_type="manual",
        ).to_request_data(),
        {"base_ym", "goal_ym", "goal_money", "base_money", "split_type"},
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
            pay_date=27,
            money=500000,
            left_account="expenses",
            left_account_id="x1",
            right_account="assets",
            right_account_id="x2",
            skip_holiday="after",
            extra_fields={"custom": "value"},
        ).to_request_data(),
        {
            "section_id",
            "item",
            "pay_date",
            "money",
            "l_account",
            "l_account_id",
            "r_account",
            "r_account_id",
            "skip_holiday",
            "custom",
        },
    )
    assert_request_data(
        BbsPostInput(subject="제목", contents="본문", extra_fields={"tag": "api"})
        .to_request_data(),
        {"subject", "contents", "tag"},
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
