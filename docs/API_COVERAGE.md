# API 구현 커버리지

이 문서는 [후잉 개발자 API 문서](https://whooing.com/api/docs)를 기준으로 현재 라이브러리의
구현 범위를 추적합니다. 기본 방향은 공식 경로 호출을 안정적으로 제공하고, 응답 스키마는
`ApiResponse[JsonValue]`로 보존한 뒤 필요한 사용자가 optional Pydantic 헬퍼로 검증하는
것입니다.

## 인증

| 영역 | 상태 | 구현 |
| --- | --- | --- |
| API key 인증 | 완료 | `APIKeyAuth`, `WhooingClient(api_key=...)` |
| Bearer token 인증 | 완료 | `BearerTokenAuth`, `WhooingClient(access_token=...)` |
| OAuth 2.0 PKCE authorization URL | 완료 | `create_pkce_challenge`, `build_authorization_url` |
| OAuth 2.0 token exchange | 완료 | `OAuth2TokenClient.exchange_code` |
| OAuth 2.0 refresh | 완료 | `OAuth2TokenClient.refresh` |
| OAuth 2.0 revoke | 완료 | `OAuth2TokenClient.revoke` |
| OAuth 2.0 metadata | 완료 | `get_oauth2_metadata`, `async_get_oauth2_metadata` |
| OAuth 1.0a request token | 완료 | `AppAuthClient.request_token` |
| OAuth 1.0a authorization URL | 완료 | `AppAuthClient.build_authorization_url` |
| OAuth 1.0a access token | 완료 | `AppAuthClient.access_token` |
| Onetime PIN | 완료 | `AppAuthClient.access_token_by_onetime` |
| 비동기 인증 헬퍼 | 완료 | `AsyncOAuth2TokenClient`, `AsyncAppAuthClient` |

## API 리소스

| 문서 영역 | 상태 | 구현 |
| --- | --- | --- |
| 사용자 | 완료 | `client.users` |
| 사용자 요청 모델 | 부분 | `UserInput` |
| 섹션 | 완료 | `client.sections` |
| 섹션 요청 모델 | 부분 | `SectionInput` |
| 계정 | 완료 | `client.accounts` |
| 계정 요청 모델 | 부분 | `AccountInput`, 생성/수정 지원 |
| 거래 CRUD | 완료 | `client.entries` |
| 거래 입력 요청 모델 | 부분 | `EntryInput`, 단건/다건 입력 지원 |
| 거래 분석성 API | 완료 | `flow_of_account`, `changes_of_item` 등 명시 메서드 |
| 외부 거래 입력 | 완료 | `parse_outside`, `report_outside_source` |
| 예산 | 완료 | `client.budgets` |
| 예산 요청 모델 | 부분 | `BudgetInput`, `BasicTotalBudgetInput` |
| 목표 예산 요청 모델 | 부분 | `BudgetGoalInput`, `CapitalGoalInput` |
| 보고서 | 완료 | `client.reports` |
| 자주입력/매월입력 | 완료 | `client.extras` |
| 카드/입출금/캘린더 | 완료 | `client.extras` |
| 포스트잇/쪽지/게시판 | 완료 | `client.extras` |
| 포스트잇/쪽지 요청 모델 | 부분 | `PostItInput`, `MessageInput` |
| 반복 입력 요청 모델 | 부분 | `FrequentItemInput`, `MonthlyItemInput` |
| 게시판 요청 모델 | 부분 | `BbsPostInput`, `BbsCommentInput` |
| 업로드 준비/완료 | 완료 | `prepare_upload`, `complete_upload` |
| 알림 | 완료 | `notifications`, `mark_notifications_read` |
| 직접 경로 호출 | 완료 | `client.request`, `async_client.request` |
| 실제 API 통합 테스트 | 부분 | `WHOOING_API_KEY`, `WHOOING_SECTION_ID` 기반 skip-safe 테스트 |

## 응답 모델링

| 항목 | 상태 | 설명 |
| --- | --- | --- |
| 공통 응답 메타데이터 | 완료 | `ApiResponse.code`, `message`, `rest_of_api`, `raw` |
| API 오류 매핑 | 완료 | 인증, rate limit, 일반 API 오류 |
| HTTP 429 매핑 | 완료 | `WhooingRateLimitError` |
| 선택적 재시도 정책 | 완료 | `RetryPolicy` |
| Optional Pydantic 파싱 | 완료 | `parse`, `parse_results`, `parse_as`, `parse_results_as` |
| 리소스별 Pydantic 응답 모델 | 완료 | `whooing.pydantic_models` |

## 남은 작업

- 문서 예제와 실제 API 응답 샘플을 기준으로 자주 쓰는 응답 모델을 추가합니다.
- 실제 API 응답 샘플을 기준으로 요청 모델 필드명을 추가 검증하고, 필요한 경우 alias를
  보강합니다.
- 실제 계정이 필요한 통합 테스트는 환경 변수 기반으로 분리되어 있습니다.
- 재시도 정책은 추가되어 있으나, 실제 운영 환경의 rate limit 사용 패턴에 맞춘 고급 정책은
  별도 옵션으로 확장합니다.
