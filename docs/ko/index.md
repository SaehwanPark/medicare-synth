---
title: "문서 포털"
description: "연구 준비를 위한 메디케어형 합성 데이터. 지금 되는 일, 당뇨병–입원 예시, 추정에 쓸 수 없는 범위를 안내합니다."
permalink: /ko/
lang: ko
lang_alternate: /
---

<section class="hero">
  <div class="eyebrow">메디케어형 합성 데이터로 연구 준비하기</div>
  <h1>제한된 메디케어 자료에 들어가기 전에, 아이디어를 먼저 살펴보세요.</h1>
  <p class="lede">Medicare-Synth는 파일 구조를 점검하고 분석 방법을 시험할 수 있도록, 메디케어와 비슷한 형태의 인공 데이터를 제공합니다. 범위를 한 가지 연구 상황으로 좁히면, 공개된 통계 일부에 맞춰 합성 집단을 조정할 수도 있습니다. 메디케어 모집단을 추정하는 자료는 아닙니다.</p>
  <div class="hero-actions">
    <a class="button" href="{{ '/ko/researchers/' | relative_url }}">연구자로 살펴보기</a>
    <a class="button secondary" href="{{ '/ko/researchers/diabetes-hospitalization-example/' | relative_url }}">따라 해 보기</a>
  </div>
</section>

<div class="callout callout-warning">
  <div class="callout-title">메디케어 통계가 아닙니다</div>
  구조가 맞고 고른 공개 수치와 비슷해도, 합성 결과를 메디케어의 실증 통계, 임상 결론, 정책 근거로 인용할 수는 없습니다.
</div>

## 지금 할 수 있는 일

| 상태 | 의미 |
| --- | --- |
| **지금 됩니다** | 파일 구조와 조인을 살펴보고, 예시 데이터로 코드를 연습하고, 개발 도움을 받아 수업용 CSV/Parquet를 내보냅니다 |
| **제한된 시범** | 2021년 FFS와 비슷한 당뇨병·입원(원인 무관) 합성 세계를 만들고, 고른 공개 목표 세 가지에 맞춰 조정한 뒤 비교합니다 |
| **의도한 용도가 아닙니다** | 웹에서 보정 데이터를 한 번에 받기, 아무 질환·연도나 보정 제품으로 쓰기, 모집단·인과·임상 주장 |

전체 표: [할 수 있는 일](researchers/what-you-can-do/).

## 연구자가 자주 하는 세 가지

<div class="card-grid">
  <div class="card">
    <h3>있는 데이터 살펴보기</h3>
    <p>사람, 자격, 질환, 청구 형태 기록이 어떻게 연결되는지, 그리고 환자 수와 청구 건수가 왜 다른지 확인합니다.</p>
    <p><a href="{{ '/ko/researchers/understanding-the-data/' | relative_url }}">데이터 이해하기 →</a></p>
  </div>
  <div class="card">
    <h3>분석 설계하기</h3>
    <p>지원되는 당뇨병·입원(원인 무관) 예시를 먼저 걸어 보고, 제한 추출본에 시간을 쓸지 판단합니다.</p>
    <p><a href="{{ '/ko/researchers/diabetes-hospitalization-example/' | relative_url }}">따라 해 보기 →</a></p>
  </div>
  <div class="card">
    <h3>가정 비교하기</h3>
    <p>보정 목표가 같아도, 자유롭게 둔 가정이 바뀌면 결과는 달라질 수 있습니다.</p>
    <p><a href="{{ '/ko/researchers/interpreting-results/' | relative_url }}">결과 해석 →</a></p>
  </div>
</div>

## 대표 예시 (저장된 5단계 그림)

**2021년 전통적 메디케어 행위별 수가(FFS)와 비슷한** 65세 이상 인공 집단입니다. 당뇨병과 심부전 표지가 있고, 입원은 진단을 특정하지 않은 **어떤 입원이든** 해당합니다. 고른 기준은 당뇨병 유병률 약 27.7%(2018년 출처), 심부전 12%(2022년 출처), 당뇨병이 있는 사람의 입원 위험 약 13%(이보다 약한 업계 사전 정보)입니다.

저장소에 들어 있는 5단계 합성 세계는 가상 수급자 6,000명입니다. 보정 목표가 같은 두 세계에서 입원 청구 기록은 자유로운 배경 위험 가정에 따라 **404**건과 **572**건으로 갈립니다. 이 차이는 민감도를 연습하는 데 쓰고, 메디케어의 참값을 가두는 구간으로 쓰지 않습니다.

→ [당뇨병–입원 예시](researchers/diabetes-hospitalization-example/)

## 어디서 시작할까

- **읽기:** 설치 없이 [연구자 안내](researchers/)와 [자주 묻는 질문](researchers/faq/)부터 봅니다.
- **분석:** 협업자에게 예시 표 내보내기를 부탁하고, CSV/Parquet를 R, Stata, Python으로 불러옵니다([시작하기](researchers/getting-started/)).
- **개발:** [로컬 설치 (영어)](../developers/installation/) 후 CLI/API를 사용합니다. 개발자 문서는 영어입니다.

## 도구를 고치거나 확장하나요?

<div class="callout callout-note">
  <div class="callout-title">개발자 문서 (영어)</div>
  설치, CLI, 시나리오, 데이터 모형, 보정된 합성 세계 재현, 기여 안내는 <a href="{{ '/developers/' | relative_url }}">개발자 문서</a>에 있습니다. 기술 상태의 기준 문서는 저장소 루트의 <code>SPEC.md</code>, <code>ARCHITECTURE.md</code>, <code>ROADMAP.md</code>이며 영어입니다.
</div>

## 범위

고정된 시범에 대해 0–5단계는 끝났고, 6단계 독립 평가는 **진행 중**입니다. 원고나 제안서에 릴리스나 합성 요약을 쓰기 전에 [한계와 범위](researchers/limitations/)를 읽으세요.
