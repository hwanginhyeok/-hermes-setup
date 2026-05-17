# experience_campaigns 테이블 스키마 (인성이블로그)

> 2026-05-14 확인. 체험단 통합 포털 개발 시 참조.

## 테이블명
`experience_campaigns`

## 컬럼 목록
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | uuid | PK |
| source_site | text | gangnammatzip / revu / pavlovu / mrblog / dailyview / dinnerqueen / assaview / cometoplay / modan |
| external_id | text | 사이트 내 ID |
| title | text | 캠페인 제목 |
| description | text | null 많음 |
| image_url | text | null 많음 |
| category | text | 맛집/뷰티/생활 등 |
| online_offline | text | online / offline |
| delivery_type | text | shipping / visit |
| location | text | 지역명 (예: 충남 천안) |
| location_geo | point | null 대부분 |
| deadline | date | null 많음 |
| reward | text | 혜택 설명. null 많음 |
| url | text | 원본 사이트 URL |
| fetched_at | timestamptz | 수집 시각 |
| source_id | text | null 많음 |
| recruit_count | int | 모집 인원. null 많음 |
| applicant_count | int | 신청자 수. null 많음 |
| competition_ratio | float | 경쟁률. null 많음 |
| channels | text[] | ['블로그'] 형태 |
| value_estimate | int | 혜택 추정가 |
| is_high_value | bool | 고가 여부 |
| start_date | date | null 많음 |
| review_period | text | null 많음 |
| region_code | text | ISO 3166-2 (예: KR-44) |
| district | text | 구/군 |
| tags | text[] | null 대부분 |
| requires_purchase | bool | null 대부분 |
| archived_at | timestamptz | 아카이브 시각 |
| station | text | 근처 지하철역 (965/1000이 null) |
| station_lat | float | 역 위도 |
| station_lon | float | 역 경도 |
| city | text | 시 |

## 수집 현황 (2026-05-14)
- **총 1,000건**
- 사이트별: gangnammatzip(255) / revu(189) / pavlovu(188) / mrblog(112) / dailyview(106) / dinnerqueen(62) / assaview(45) / cometoplay(23) / modan(20)

## 주요 null 비율 문제
- reward, description, image_url, recruit_count, competition_ratio, deadline 대부분 null
- station: 965/1000이 null (지하철역 데이터 미완성)
- 카드 UX 개선 시 null safe 처리 필수

## API 엔드포인트
- `GET /api/experience/campaigns` — 필터링 + 매칭점수 정렬
- `GET /api/experience/zones` — 활동지역
- `GET /api/experience/keywords` — 관심키워드
- `GET /api/experience/new-matches-today` — 오늘 새 매칭

## 프론트엔드
- 페이지: `apps/web/app/(dashboard)/(social)/experience/page.tsx`
- 컴포넌트: `CampaignCard`, `FilterBar`, `ActivityZoneEditor`, `InterestKeywordsEditor`
- 현재 이슈: `max-h-[800px]` 박스 스크롤로 UX 답답. 페이지 전체 스크롤로 변경 권장

## 체험단 포털 개선 우선순위 (CEO Review 2026-05-14)
1. **UX 개선** (0.5일) — 박스스크롤 제거, D-day 뱃지, "NEW" 뱃지
2. **카드 품질** (1~2일) — reward/recruit_count 파싱 강화, 매칭 이유 텍스트
3. **수집 확대** (2~3일) — 잔여 사이트 robots 우회
