# Product Brief: neulbom

**Date:** 2025-11-03
**Author:** Shang
**Status:** Draft for PM Review

---

## Executive Summary

Neulbom is a comprehensive management platform that automates ZEP space creation and management for Seoul's after-school education program across 13 universities. The platform addresses critical operational challenges faced by instructors managing student accounts and spaces while providing administrators with real-time monitoring capabilities.

**Core Problem:** Instructors spend excessive time manually creating student accounts and ZEP spaces, while administrators lack visibility into program-wide activities. Students' educational achievements are not systematically accumulated as portfolios.

**Solution:** An automated system that enables bulk student registration, automatic space creation with preset permissions, and a centralized dashboard for monitoring 13 universities. Student spaces accumulate over semesters as personal portfolios with selective public visibility for showcasing achievements.

**Target Market:** Primary users are instructors from 13 Seoul universities managing the Neulbom program (estimated 100+ instructors, 2,000+ students). Secondary users include program administrators (Konkuk University, KERIS) requiring oversight and reporting capabilities.

**Value Proposition:**
- Reduces instructor operational time by 50% through automation
- Enables real-time program monitoring across all participating universities
- Creates long-term student portfolio ecosystem with public showcase capabilities
- Strengthens Seoul education brand through seoul.zep.us domain

**MVP Scope:** ID/PW authentication, instructor management, bulk student registration with automatic space creation, space management with public visibility controls, public landing page, and administrator dashboard. Launch timeline: December 2025 for instructors, March 2026 official launch.

**Strategic Alignment:** Establishes ZEP's education market presence through B2G partnership (Konkuk University, KERIS, Seoul Metropolitan Office of Education), with expansion potential to other regions and educational institutions nationwide.

---

## Problem Statement

**현재 상황:**
서울시 내 13개 대학이 주관하는 늘봄 방과후 교육 프로그램에서 학생들의 학습 활동과 성과물을 체계적으로 관리하고 축적할 수 있는 시스템이 부재합니다. 강사들은 수십 명의 학생 계정을 수동으로 관리해야 하며, 학생별 ZEP 스페이스 생성 및 권한 설정에 많은 시간을 소비하고 있습니다.

**구체적 문제점:**
- 강사가 학생 계정과 스페이스를 일일이 수동 생성해야 하는 운영 부담
- 학생들의 활동 성과물이 체계적으로 축적되지 않아 포트폴리오화 불가능
- 관리자(건국대, 정보원)가 13개 대학의 운영 현황과 학생 활동을 실시간으로 모니터링할 수 없음
- 외부(학부모, 교육청)에 성과를 효과적으로 공유하고 홍보할 수단 부재
- 분기별 학생 명단 변경 시마다 반복되는 수작업 부담

**긴급성:**
2025년 12월부터 강사들이 실제 현장에서 사용해야 하며, 초기부터 안정적 운영이 필수적입니다.

---

## Proposed Solution

**핵심 접근:**
늘봄(Neulbom) 플랫폼은 학교-강사-학생 단위로 ZEP 스페이스를 자동 생성·관리하고, 학생 개별 스페이스를 포트폴리오처럼 축적·공개할 수 있는 통합 관리 시스템입니다.

**주요 차별점:**
- **자동화된 대량 등록**: 강사가 학생 명단을 업로드하면 계정과 스페이스가 자동 생성되어 운영 부담 최소화
- **계층적 권한 관리**: 학생=소유자, 강사·관리자=스태프 권한으로 자동 설정되어 별도 권한 작업 불필요
- **포트폴리오 구조**: 학생 스페이스가 학기별로 축적되어 개인 포트폴리오로 성장
- **선택적 공개**: 스페이스 내 특정 섹션만 비로그인 사용자에게 공개하여 성과 홍보
- **통합 대시보드**: 13개 대학의 이용 현황, 방문자 수, 활성도를 한눈에 모니터링

**성공 요인:**
- ID/PW 기반 인증으로 초등학생도 쉽게 접근 가능
- seoul.zep.us 도메인으로 서울시 교육 브랜드 강화
- 강사 교육 이수 여부 추적으로 품질 관리 (향후 LMS 연동)

---

## Target Users

### Primary User Segment

**강사 (Primary User)**

| 속성 | 설명 |
|------|------|
| **프로필** | 서울시 13개 대학 소속 늘봄 방과후 교육 강사, 초등학생 대상 수업 진행 |
| **현재 방식** | 학생 계정을 수동으로 생성하거나, 학생들에게 개별 가입을 안내하여 시간 소모 |
| **핵심 Pain Point** | - 분기마다 20~40명 학생 계정/스페이스를 수동 생성<br>- 학생별 권한 설정 작업 반복<br>- 학생 활동 모니터링의 어려움 |
| **목표** | 수업 준비 시간 단축, 학생 관리 자동화, 교육 품질 향상에 집중 |
| **기술 수준** | 중급 (웹 기반 도구 사용 가능, 복잡한 기술 설정은 부담) |

### Secondary User Segment

**관리자 (건국대 교수, 정보원 연구사)**

| 속성 | 설명 |
|------|------|
| **프로필** | 서울시 늘봄 사업 총괄 담당, 13개 대학 운영 관리 및 성과 보고 책임 |
| **현재 방식** | 강사들로부터 개별 보고 수렴, Excel 수동 집계 |
| **핵심 Pain Point** | - 실시간 운영 현황 파악 불가<br>- 통합 성과 데이터 수집 어려움<br>- 교육청/학부모 대상 성과 공유 수단 부족 |
| **목표** | 통합 모니터링, 데이터 기반 의사결정, 사업 성과 가시화 |

**학생 (Indirect User)**

학생은 별도 UI 없이 ZEP 스페이스 내에서 활동하지만, 본인 계정/스페이스의 **소유자**로서 콘텐츠를 축적하고 향후 개인 포트폴리오로 활용합니다.

---

## Goals and Success Metrics

### Business Objectives

| 목표 | 측정 지표 | 목표치 (6개월) |
|------|----------|---------------|
| **운영 효율성 향상** | 강사 1인당 학생 관리 시간 단축 | 50% 감소 (현재 평균 2시간 → 1시간) |
| **사업 확장성 확보** | 플랫폼 지원 가능 학교/강사 수 | 13개 대학, 100명 강사, 2,000명 학생 |
| **성과 가시화** | 외부 공개 포트폴리오 수 | 500개 이상 |
| **파트너십 강화** | 건국대-ZEP-정보원 MoU 체결 및 PR 배포 | 2025년 12월 전 완료 |

### User Success Metrics

| 사용자 | 성공 지표 | 측정 방법 |
|--------|----------|----------|
| **강사** | 학생 등록/스페이스 생성 완료율 | 벌크 업로드 후 24시간 내 100% 자동 완료 |
| **강사** | 플랫폼 활성 사용률 | 주 1회 이상 로그인 강사 비율 80% 이상 |
| **관리자** | 대시보드 활용도 | 월 2회 이상 대시보드 접속 100% |
| **학생** | 스페이스 소유권 유지율 | 학기 종료 후 포트폴리오 전환율 30% 이상 |

### Key Performance Indicators (KPIs)

1. **시스템 안정성**: 2025년 12월 출시 후 uptime 99% 이상
2. **사용자 만족도**: 강사 NPS 점수 50 이상
3. **운영 자동화율**: 수동 작업 시간 대비 자동화 비율 80% 이상
4. **데이터 품질**: 대시보드 데이터 정확도 95% 이상
5. **공개 콘텐츠 노출**: 외부 방문자 수 월 1,000명 이상 (2026년 3월 기준)

---

## Strategic Alignment and Financial Impact

### Financial Impact

**개발 투자:**
- 초기 개발 비용: Django 기반 웹 플랫폼 구축, ZEP API 연동, 대시보드 개발
- 운영 비용: 서버 호스팅, 도메인 유지(seoul.zep.us), 유지보수

**비용 절감:**
- 강사 운영 시간 절감: 100명 강사 × 주 2시간 절감 × 시급 환산 = 연간 약 1억원 절감 효과
- 수동 집계 작업 제거: 관리자 운영 시간 월 40시간 → 5시간 (87% 감소)

**수익 기회:**
- ZEP 교육 사업 확장: 서울시 성공 사례를 타 지역/기관으로 확대 가능
- 교육청 대상 SaaS 모델 전환 가능성

### Company Objectives Alignment

**ZEP 전략과의 정렬:**
- 교육 시장 진입 및 레퍼런스 확보 (B2G 사업 경험)
- 메타버스 교육 플랫폼으로서의 브랜드 강화
- 공공 기관 파트너십 구축 (건국대, 정보원, 서울시교육청)

**사업 우선순위:**
- 건국대 교수의 강력한 의지와 정보원 지원으로 초기 성공 가능성 높음
- 2026년 3월 공식 오픈 전 12월 사전 검증 기회 확보

### Strategic Initiatives

1. **교육 사업 확장**: 늘봄 → 일반 학교 → 교육청 전체 확대 로드맵
2. **포트폴리오 생태계**: 학생 개인 포트폴리오가 장기 자산으로 축적되어 네트워크 효과 창출
3. **데이터 기반 교육**: 대시보드 데이터를 통한 교육 효과성 분석 및 개선

---

## MVP Scope

### Core Features (Must Have)

**1. 인증 및 권한 관리**
- ID/PW 기반 로그인 시스템
- 역할별 권한 관리 (관리자/강사/학생)
- seoul.zep.us 도메인 설정

**2. 강사 관리 기능 (관리자 페이지)**
- 강사 계정 생성/조회/검색
- 강사별 소속 학교 및 반 정보 관리
- 강사 교육 이수 여부 표기 (수동 입력, LMS 연동은 Phase 2)

**3. 학생 벌크 등록 (강사 페이지)**
- 학생 명단 CSV/Excel 업로드
- 학생 계정 자동 생성 (fake email)
- 학생별 ZEP 스페이스 자동 생성 및 URL 연결
- 권한 자동 설정 (학생=소유자, 강사/관리자=스태프)

**4. 스페이스 관리**
- 학교/반/학생 스페이스 목록 테이블
- 스페이스 URL 관리 및 ZEP 연동
- 스페이스 공개 범위 설정 (일부 섹션 비로그인 공개)

**5. 공용 랜딩 페이지 (비로그인)**
- 늘봄 로고 및 프로젝트 소개
- 참여 학교 로고/리스트 그리드
- 대표 영상
- 공개된 학생 스페이스 일부 노출

**6. 대시보드 (관리자용)**
- 총 학교/강사/학생 수
- 활성 스페이스 수
- 방문자 수 (일/주/월)
- 강사별 운영 현황

### Out of Scope for MVP

- 유비온 LMS API 연동 (자동 교육 이수 여부 동기화) → Phase 2
- 학생용 별도 UI → 학생은 ZEP 스페이스에서만 활동
- 고급 분석 기능 (학습 데이터 분석, AI 추천 등)
- 다국어 지원
- 모바일 앱

### MVP Success Criteria

1. **기능 완성도**: 2025년 12월 출시 시 Core Features 100% 구현
2. **사용자 온보딩**: 강사 10명이 학생 등록부터 스페이스 생성까지 성공적으로 완료
3. **시스템 안정성**: 베타 테스트 기간(2025년 10~11월) 동안 주요 버그 0건
4. **성과 공유**: 공개 랜딩 페이지를 통해 외부 방문자 100명 이상 유입

---

## Post-MVP Vision

### Phase 2 Features

**유비온 LMS 연동**
- 강사 교육 이수 여부 자동 동기화
- API 기반 실시간 데이터 업데이트

**고급 대시보드**
- 학습 참여도 분석 (스페이스 방문 빈도, 활동 시간)
- 학생별 성장 지표 추적
- 강사별 성과 비교 리포트

**학생 포트폴리오 전환 기능**
- 학기 종료 시 학생이 개인 이메일로 소유권 이관 신청
- 자동 권한 업데이트 워크플로우

**알림 시스템**
- 강사에게 학생 활동 알림
- 관리자에게 시스템 이벤트 알림

### Long-term Vision

**확장 가능한 교육 플랫폼**
- 서울시 13개 대학 → 전국 교육청 확장
- 늘봄 프로그램 → 정규 수업 및 방과후 활동 전반으로 확대
- 학생 포트폴리오 생태계 구축 (초등→중등→고등 연계)

**데이터 기반 교육 혁신**
- 학습 패턴 분석을 통한 맞춤형 교육 제안
- AI 기반 콘텐츠 추천
- 교육 효과성 측정 및 개선 사이클 구축

### Expansion Opportunities

1. **타 지역 확장**: 경기도, 부산시 등 타 지역 교육청 제안
2. **B2B SaaS 전환**: 개별 학교 단위 구독 모델
3. **국제 시장**: 한국어 교육 기관, 해외 한인 학교 대상

---

## Technical Considerations

### Platform Requirements

**웹 플랫폼 (필수)**
- 브라우저: Chrome, Safari, Edge 최신 버전 지원
- 반응형 디자인 (데스크톱 우선, 태블릿 지원)
- 접근성: WCAG 2.1 AA 수준 준수

**도메인**
- seoul.zep.us (서울시 브랜드 강화)

**성능 요구사항**
- 페이지 로드 시간 3초 이내
- 동시 접속자 500명 지원
- 벌크 업로드 처리: 100명 학생 데이터 처리 시간 30초 이내

### Technology Preferences

**Backend**
- Django (Python) - 기존 프로젝트 구조 활용
- PostgreSQL 또는 MySQL - 관계형 데이터베이스
- Django REST Framework - API 구축

**Frontend**
- Django Templates 또는 React/Vue.js (선택 가능)
- Bootstrap 또는 Tailwind CSS - UI 프레임워크

**Infrastructure**
- AWS 또는 GCP - 클라우드 호스팅
- Docker - 컨테이너화
- Nginx - 웹 서버

**Third-party Integration**
- ZEP API - 스페이스 생성 및 권한 관리
- (향후) 유비온 LMS API - 강사 교육 이수 데이터

### Architecture Considerations

**데이터 모델**
- 학교(School) - 강사(Instructor) - 반(Class) - 학생(Student) 계층 구조
- ZEP 스페이스 URL 및 권한 매핑 테이블
- 사용자 로그 및 활동 추적

**보안**
- ID/PW 인증 + Django 기본 보안 (CSRF, XSS 방지)
- HTTPS 필수
- 학생 개인정보 암호화 저장

**확장성**
- 마이크로서비스 아키텍처 고려 (향후 확장 시)
- API 우선 설계로 모바일 앱 확장 가능

---

## Constraints and Assumptions

### Constraints

**타임라인**
- 베타 테스트: 2025년 10~11월
- 강사용 페이지 출시: 2025년 12월
- 공식 오픈: 2026년 3월
- 타이트한 일정으로 MVP 범위 엄격히 제한 필요

**리소스**
- 개발 팀 규모 제한 (소규모 팀 가정)
- 예산 제약 (공공 사업 특성상 비용 효율성 중요)

**기술**
- ZEP API 기능 및 제약사항에 의존
- 기존 Django 프로젝트 구조 활용 (재작성 불가)

**정책**
- 초등학생 개인정보 보호 법규 준수 필수
- 교육청 보안 정책 준수

### Key Assumptions

**사용자 행동**
- 강사들이 CSV/Excel 파일 업로드 방식에 익숙함
- 학생들은 ZEP 스페이스 사용법을 강사로부터 교육받음
- 관리자는 주기적으로 대시보드를 모니터링함

**기술**
- ZEP API가 대량 스페이스 생성 및 권한 관리를 지원함
- seoul.zep.us 도메인 설정이 기술적으로 가능함
- Django 프로젝트가 확장 가능한 구조로 이미 구성됨

**사업**
- 건국대 교수와 정보원의 지속적인 지원 및 협력
- 13개 대학의 강사 참여 의지
- MoU 체결 및 PR이 사업 추진력 확보에 기여

**검증 필요한 가정**
- ZEP API 스펙 및 rate limit 확인 필요
- 유비온 LMS API 존재 여부 및 연동 가능성 (Phase 2)
- 초등학생 fake email 생성 방식의 법적 적합성

---

## Risks and Open Questions

### Key Risks

| 위험 | 영향도 | 대응 전략 |
|------|--------|----------|
| **ZEP API 제약** | 높음 | 개발 초기 ZEP API 스펙 확인 및 기술 검증, 대안 설계 준비 |
| **타이트한 일정** | 높음 | MVP 범위 최소화, 애자일 개발, 조기 베타 테스트 |
| **강사 온보딩 실패** | 중간 | 직관적 UI 설계, 온보딩 가이드/교육 자료 제공, 초기 집중 지원 |
| **스페이스 공개 설정 복잡도** | 중간 | 단순한 기본 설정 제공, Phase 2에서 고급 기능 추가 |
| **개인정보 보호 이슈** | 높음 | 법률 자문, 개인정보 암호화, 학부모 동의서 프로세스 수립 |
| **파트너십 변동** | 낮음 | MoU를 통한 공식 협력 관계 구축, 정기 커뮤니케이션 |

### Open Questions

1. **ZEP API 대량 처리**: ZEP API가 한 번에 몇 개의 스페이스를 생성할 수 있나? Rate limit은?
2. **Fake Email 정책**: 학생용 fake email 생성 방식이 개인정보보호법에 부합하는가? 학부모 동의가 필요한가?
3. **스페이스 템플릿**: 학교/반/학생 스페이스의 기본 템플릿은 누가 제공하나? ZEP에서 표준 템플릿을 제공하는가?
4. **유비온 LMS API**: 유비온 LMS가 API를 제공하는가? 제공한다면 어떤 데이터를 얻을 수 있나?
5. **호스팅 인프라**: AWS/GCP 중 어느 것을 선택할 것인가? 비용 및 성능 비교 필요
6. **모바일 지원**: MVP에서 모바일 웹 지원 수준은 어디까지인가?

### Areas Needing Further Research

1. **ZEP API 기술 문서 리뷰**: 스페이스 생성, 권한 관리, 공개 설정 API 상세 확인
2. **경쟁 사례 조사**: 타 교육 플랫폼의 대량 등록 및 포트폴리오 관리 방식 벤치마크
3. **개인정보 법률 자문**: 초등학생 데이터 처리 관련 법적 요구사항 명확화
4. **사용자 리서치**: 강사 3~5명과 인터뷰하여 현재 운영 방식 및 pain point 심층 파악
5. **인프라 비용 산정**: 예상 트래픽 기준 클라우드 호스팅 비용 견적

---

## Appendices

### A. Research Summary

**미팅 기반 인사이트 (2025년 회의 내용)**
- 건국대 김경모 교수: 서울시 13개 대학 늘봄 사업 총괄 담당
- 정보원 김행선 연구사: 기획 구조 전면 동의, 초기 단계부터 진행 의지 강력
- 합의된 타임라인: 강사용 페이지 2025년 12월, 학생용 2026년 3월
- ID/PW 인증 방식 선호, seoul.zep.us 도메인 요청
- 대시보드가 늦어도 10월 말부터 활용 가능하기를 희망

**추가 요구사항**
- 강사 교육 이수 여부 표기 기능 (유비온 LMS 연동 가능성 확인 필요)
- MoU 체결 및 PR 배포 계획

**학생 계정 생성 방식 논의**
- 방법 1: 강사가 Gmail 생성 후 배정 (포트폴리오화 어려움)
- 방법 2: 학생 개별 이메일로 가입 (부모 동의서 필요)

### B. Stakeholder Input

**주요 이해관계자**
- 건국대학교 (김경모 교수): 사업 총괄, 13개 대학 조율
- 정보원 (김행선 연구사): 교육 정책 지원, 행정 협력
- ZEP (이기환): 기술 파트너, API 제공 및 인프라 지원
- 13개 대학 강사진: 실제 사용자, 피드백 제공

**협력 모델**
- 건국대-ZEP-정보원 3자 MoU 체결
- 정기 운영 회의 및 피드백 수렴 프로세스

### C. References

- 서울시 늘봄 방과후 교육 프로그램 정책 문서 (필요 시 추가)
- ZEP 플랫폼 기술 문서 (API 리뷰 예정)
- 유비온 LMS 시스템 개요 (API 확인 필요)
- 개인정보보호법 및 초등학생 데이터 처리 가이드라인 (법률 자문 예정)

---

_This Product Brief serves as the foundational input for Product Requirements Document (PRD) creation._

_Next Steps: Handoff to Product Manager for PRD development using the `workflow prd` command._
