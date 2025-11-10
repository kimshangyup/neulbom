# Product Brief: neulbom (Executive Summary)

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

## Problem Statement & Solution

**현재 상황:**
서울시 내 13개 대학이 주관하는 늘봄 방과후 교육 프로그램에서 학생들의 학습 활동과 성과물을 체계적으로 관리하고 축적할 수 있는 시스템이 부재합니다. 강사들은 수십 명의 학생 계정을 수동으로 관리해야 하며, 학생별 ZEP 스페이스 생성 및 권한 설정에 많은 시간을 소비하고 있습니다.

**핵심 접근:**
늘봄(Neulbom) 플랫폼은 학교-강사-학생 단위로 ZEP 스페이스를 자동 생성·관리하고, 학생 개별 스페이스를 포트폴리오처럼 축적·공개할 수 있는 통합 관리 시스템입니다.

**주요 차별점:**
- **자동화된 대량 등록**: 강사가 학생 명단을 업로드하면 계정과 스페이스가 자동 생성
- **계층적 권한 관리**: 학생=소유자, 강사·관리자=스태프 권한으로 자동 설정
- **포트폴리오 구조**: 학생 스페이스가 학기별로 축적되어 개인 포트폴리오로 성장
- **선택적 공개**: 스페이스 내 특정 섹션만 비로그인 사용자에게 공개
- **통합 대시보드**: 13개 대학의 이용 현황을 한눈에 모니터링

---

## Target Users & Goals

### Primary User: 강사

| 속성 | 설명 |
|------|------|
| **프로필** | 서울시 13개 대학 소속 늘봄 방과후 교육 강사, 초등학생 대상 수업 진행 |
| **핵심 Pain Point** | 분기마다 20~40명 학생 계정/스페이스를 수동 생성, 학생별 권한 설정 작업 반복 |
| **목표** | 수업 준비 시간 단축, 학생 관리 자동화, 교육 품질 향상에 집중 |

### Secondary User: 관리자 (건국대 교수, 정보원 연구사)

| 속성 | 설명 |
|------|------|
| **프로필** | 서울시 늘봄 사업 총괄 담당, 13개 대학 운영 관리 및 성과 보고 책임 |
| **핵심 Pain Point** | 실시간 운영 현황 파악 불가, 통합 성과 데이터 수집 어려움 |
| **목표** | 통합 모니터링, 데이터 기반 의사결정, 사업 성과 가시화 |

### Key Performance Indicators (KPIs)

1. **시스템 안정성**: 2025년 12월 출시 후 uptime 99% 이상
2. **사용자 만족도**: 강사 NPS 점수 50 이상
3. **운영 자동화율**: 수동 작업 시간 대비 자동화 비율 80% 이상
4. **공개 콘텐츠 노출**: 외부 방문자 수 월 1,000명 이상 (2026년 3월 기준)

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
- 강사 교육 이수 여부 표기 (수동 입력)

**3. 학생 벌크 등록 (강사 페이지)**
- 학생 명단 CSV/Excel 업로드
- 학생 계정 자동 생성 (fake email)
- 학생별 ZEP 스페이스 자동 생성 및 URL 연결
- 권한 자동 설정 (학생=소유자, 강사/관리자=스태프)

**4. 스페이스 관리**
- 학교/반/학생 스페이스 목록 테이블
- 스페이스 URL 관리 및 ZEP 연동
- 스페이스 공개 범위 설정

**5. 공용 랜딩 페이지 (비로그인)**
- 늘봄 로고 및 프로젝트 소개
- 참여 학교 로고/리스트 그리드
- 공개된 학생 스페이스 일부 노출

**6. 대시보드 (관리자용)**
- 총 학교/강사/학생 수, 활성 스페이스 수
- 방문자 수 (일/주/월), 강사별 운영 현황

### Out of Scope for MVP

- 유비온 LMS API 연동 → Phase 2
- 학생용 별도 UI → 학생은 ZEP 스페이스에서만 활동
- 고급 분석 기능, 다국어 지원, 모바일 앱

---

## Technical Considerations & Timeline

### Technology Stack

**Backend:** Django (Python), PostgreSQL/MySQL, Django REST Framework
**Frontend:** Django Templates or React/Vue.js, Bootstrap/Tailwind CSS
**Infrastructure:** AWS/GCP, Docker, Nginx
**Integration:** ZEP API (space creation, permissions)

### Timeline & Milestones

| 단계 | 일정 | 목표 |
|------|------|------|
| **베타 테스트** | 2025년 10~11월 | 강사 10명 온보딩, 주요 버그 0건 |
| **강사용 페이지 출시** | 2025년 12월 | Core Features 100% 구현 |
| **공식 오픈** | 2026년 3월 | 전체 13개 대학 운영 |

### Key Risks & Mitigation

| 위험 | 영향도 | 대응 전략 |
|------|--------|----------|
| **ZEP API 제약** | 높음 | 개발 초기 ZEP API 스펙 확인 및 기술 검증 |
| **타이트한 일정** | 높음 | MVP 범위 최소화, 애자일 개발, 조기 베타 테스트 |
| **개인정보 보호 이슈** | 높음 | 법률 자문, 개인정보 암호화, 학부모 동의서 프로세스 |

---

## Strategic Impact

**Financial Impact:**
- 강사 운영 시간 절감: 100명 강사 × 주 2시간 절감 = 연간 약 1억원 절감 효과
- 관리자 운영 시간: 월 40시간 → 5시간 (87% 감소)

**Company Objectives Alignment:**
- 교육 시장 진입 및 레퍼런스 확보 (B2G 사업 경험)
- 메타버스 교육 플랫폼 브랜드 강화
- 공공 기관 파트너십 구축 (건국대, 정보원, 서울시교육청)

**Expansion Opportunities:**
1. **타 지역 확장**: 경기도, 부산시 등 타 지역 교육청 제안
2. **B2B SaaS 전환**: 개별 학교 단위 구독 모델
3. **국제 시장**: 한국어 교육 기관, 해외 한인 학교 대상

---

_This Product Brief serves as the foundational input for Product Requirements Document (PRD) creation._

_Next Steps: Handoff to Product Manager for PRD development using the `/bmad:bmm:workflows:prd` command._
