# Medicare-Synth 프로젝트 감사: 문헌 기반 조율과 장기 확장성

검토 기준: 2026년 11월 8일 · GitHub `main` 브랜치 · Read-only audit

## 1. 종합 평가

현재 프로젝트는 제시한 세 가지 목표를 실현하기 위한 좋은 출발점이지만, 궁극적으로 필요한 시스템과 현재 구현 사이에는 상당한 구조적 차이가 있습니다.

특히 프로젝트를 단순한 Evidence-Calibrated Synthetic Data Generator에서 Literature-Constrained, Continually Calibrated Medicare Population Model로 발전시키는 것이 적절해 보입니다.

여기서 중요한 변화는 더 많은 문헌을 수집하거나 조율 알고리즘을 고도화하는 것만이 아닙니다.

조율의 대상 자체를 개별 데이터셋에서, 여러 문헌이 동시에 제약하는 공통 확률모형으로 옮겨야 합니다.

### 세 가지 목표별 평가

| 목표                                   | 현재 상태                           | 평가               |
| ------------------------------------ | ------------------------------- | ---------------- |
| 1. 문헌을 누적해 개선하는 거대한 공통 데이터셋          | 고정된 문헌 집합에 대한 조율과 재현 가능한 생성만 지원 | 핵심 아키텍처 확장 필요    |
| 2. 특정 연구 목적에 최적화된 world              | 세 가지 MVP world 구현               | 좋은 기반. 일반화 필요    |
| 3. 문헌의 inferential relationship까지 재현 | 유병률과 조건부 입원 확률 중심. 조정 회귀분석 미지원  | 새로운 분석·최적화 계층 필요 |

현재의 세 목표에 대한 구현 성숙도를 굳이 구분하면 다음과 같습니다.

공통 모델의 누적 조율

설계 및 부분 기반

특정 context의 world

제한적 MVP 구현

Inferential calibration

기초적인 조건부 관계만 구현

정량적 완성도 점수가 아니라, 현재 확인된 기능의 상대적인 범위를 설명하는 개념적 표시입니다.

현재 저장소의 강점은 이미 검증 가능한 조율 파이프라인을 구축했다는 것입니다. 특히 다음은 재사용할 가치가 큽니다.

- Evidence IR: 문헌의 모집단, 변수 정의, estimand, 추정치, 출처를 구조화합니다.
- Evidence corpus: 조율용 근거와 독립 평가용 근거를 분리하고 체크섬으로 고정합니다.
- Calibration engine: IPF 기반 reweighting과 생성 파라미터 탐색이 가능합니다.
- World family: 동일한 문헌 제약을 만족하면서도 다른 데이터 생성 가정을 가진 world들을 비교할 수 있습니다.
- Governance: 문헌 해석과 조율 목표의 변경에 인간 검토를 요구합니다.

이는 단순한 프로토타입 이상의 기반입니다. 그러나 아직 새로운 문헌이 기존의 지식을 어떻게 업데이트하며, 기존 관계를 유지하면서 새로운 관계를 학습할 것인가라는 핵심 문제가 해결되어 있지 않습니다.

이 부분을 중심으로 감사하겠습니다.

## 2. 현재 구현에서 발견한 주요 병목

### 2.1. 가장 큰 문제: Calibration의 결과가 누적되는 모델이 없다

현재 파이프라인은 대략 다음과 같습니다.

Frozen literature corpus

3개 calibration finding

Calibration

IPF reweighting / Generator parameter search

World 1

동일한 근거 집합

World 2

동일한 근거 집합

World 3

동일한 근거 집합

이 구조에서는 새로운 문헌이 들어오면 기존 corpus를 업데이트하고 재조율하는 방식이 필요합니다.

그러나 기존 모델의 조율 상태를 유지하면서 새로운 제약을 추가하는 기능은 아직 없습니다.

구체적으로 현재 구현에는 다음과 같은 한계가 있습니다.

| 항목                                | 실제 구현                            |
| --------------------------------- | -------------------------------- |
| 기존 모델을 초기값으로 재학습                  | 일반적인 기능으로 지원하지 않음                |
| 새로운 문헌의 누적 적용                     | Corpus 버전 관리 기반은 있으나 모델 갱신 기능 없음 |
| 이전 calibration의 유지 여부 검사          | 일반적인 regression gate 없음          |
| 새 근거와 기존 근거의 충돌 처리                | 기록·분류 기반은 있으나 최적화 차원의 조정은 없음     |
| 공통 모델에서 purpose-specific world 분기 | 고정된 MVP preset에서만 가능             |

여기서 corpus를 freeze하는 현재 정책 자체는 올바릅니다. 이미 발표한 모델을 재현할 수 있어야 하기 때문입니다.

필요한 것은 기존 corpus를 변경하는 것이 아니라, 이전 버전을 보존하면서 새 근거가 추가된 corpus와 새로운 모델 상태를 만드는 기능입니다.

예를 들어 다음처럼 발전해야 합니다.

v1

Base Medicare model

문헌 A, B, C

v2

Updated model

A, B, C + D, E

v3

Updated model

A–E + F, G, H

각 버전은 자신의 파라미터, 근거 집합, 평가 결과를 보존하며, 새 버전은 이전 버전을 초기 상태로 활용합니다.

다만 여기서 중요한 차이가 있습니다.

누적 조율은 이전 문헌을 영원히 정확히 만족한다는 뜻이 아닙니다.

새로운 근거가 더 신뢰할 만하거나 기존 근거와 충돌한다면 기존 관계를 수정할 수 있어야 합니다. 이때 무엇이 얼마나 바뀌었는지를 기록하고, 변경이 정당한지를 평가해야 합니다.

따라서 필요한 것은 단순한 추가 학습보다 versioned continual calibration입니다.

### 2.2. 생성모형 자체의 표현력이 지나치게 제한적이다

현재 [`synthesis.py`](https://github.com/SaehwanPark/medicare-synth/blob/main/src/medicare_synth/synthesis.py?utm_source=chatgpt.com)는 다음을 중심으로 데이터를 생성합니다.

\\[ P(D), \quad P(H), \quad P(I\mid D), \quad P(I\mid \neg D) \\]

여기서 \\(D\\)는 당뇨, \\(H\\)는 심부전, \\(I\\)는 입원 여부입니다.

하지만 심부전은 당뇨와 독립적으로 생성됩니다. 나이와 성별 역시 임상 결과에 영향을 미치도록 모델링되어 있지 않습니다.

따라서 현실적으로 중요한 다음 관계를 모델링하기 어렵습니다.

\\[ P(I\mid D,H,\text{Age},\text{Sex}) \\]

예를 들어 당뇨와 심부전을 모두 가진 환자의 입원 확률이 각각의 질환을 가진 환자와 어떻게 다른지에 대한 문헌이 새로 들어온다고 가정해 보겠습니다.

현재 모델에는 그 관계를 독립적으로 조절할 파라미터가 없습니다.

문헌 100편을 추가하더라도, 생성모형에 해당 관계를 표현할 수 있는 구조가 없다면 이를 학습할 수 없습니다.

이것은 calibration algorithm의 문제가 아니라 model capacity의 문제입니다.

우선 다음과 같은 다변량 조건부 모형으로 확장하는 것이 좋습니다.

\\[ \operatorname{logit}P(I=1\mid X) = \beta_0+\beta_DD+\beta_HH+ \beta_AA+\beta_SS+ \beta\_{DH}DH \\]

이를 통해 당뇨, 심부전, 연령, 성별, 상호작용에 대한 문헌 제약을 표현할 수 있습니다.

처음부터 거대한 딥러닝 모델을 도입할 필요는 없습니다. 오히려 해석 가능하고 제약을 쉽게 적용할 수 있는 모듈식 확률모형이 현재 단계에는 더 적합합니다.

### 2.3. 현재의 Evidence IR은 추론적 관계를 실행하지 못한다

[`evidence_ir.py`](https://github.com/SaehwanPark/medicare-synth/blob/main/src/medicare_synth/evidence_ir.py?utm_source=chatgpt.com)는 중요한 기반입니다. 하지만 현재 지원되는 estimand는 세 가지입니다.

- Prevalence
- Binary risk
- Rate

이 중 두 번째는 조건부 관계를 다루므로 이미 기초적인 관계 조율은 가능합니다.

하지만 문헌에서 흔히 보고하는 adjusted association을 그대로 재현할 수는 없습니다.

예를 들어 연구가 다음과 같이 보고했다고 가정하겠습니다.

> After adjustment for age, sex, and comorbidities, diabetes was associated with an odds ratio of 1.45 for hospitalization.

이 결과는 단순히 \\(P(I\mid D)\\)를 1.45라는 값에 맞추는 것으로 재현되지 않습니다.

동일한 모집단을 구성하고, 동일한 변수를 정의하고, 동일한 조정변수를 넣어 로지스틱 회귀를 실행해야 합니다.

현재 코드에서는 `analysis.adjustment_set`이 비어 있지 않으면 compiler가 명시적으로 오류를 반환합니다.

또한 `analysis.estimator`는 저장되는 필드이지만, 현재 compiler는 지원되는 estimand 유형에 따라 자체적으로 추정 방법을 선택합니다.

즉, 문헌에 어떤 분석 방법이 적혀 있는지와 실제로 실행하는 분석이 일치한다는 보장이 아직 없습니다.

여기가 세 번째 목표를 구현하기 위해 가장 중요하게 확장해야 할 부분입니다.

## 3. 코드 수준에서 발견한 개선 사항

구현 자체에서도 몇 가지 우선순위가 높은 문제가 확인되었습니다.

| 중요도      | 문제                                | 근거 및 영향                                                                      |
| -------- | --------------------------------- | ---------------------------------------------------------------------------- |
| Critical | IPF 수렴 판정 오류 가능성                  | 각 제약 적용 직후 오차만 검사하므로 이전 제약이 다시 벗어나도 수렴했다고 판단할 수 있음                           |
| High     | Unsupported target이 최적화에서 빠질 수 있음 | `discrepancy_for_findings`는 계산 실패 시 missing을 기록하지만, MAE는 계산 가능한 항목만 평균       |
| High     | Reweight 결과를 일반 데이터셋으로 오해할 위험     | Level B는 데이터 자체를 변경하지 않고 가중치만 생성                                             |
| High     | 조율과 분석의 대상 모집단 정렬이 일반화되지 않음       | IPF는 전체 beneficiary frame을 사용하지만 Evidence IR 비교는 finding별 eligible cohort 사용 |
| Medium   | Holdout을 후보별로 반복 계산               | Level C에서 선택 목적함수에 사용하지는 않으나 모든 후보의 holdout을 계산                              |
| Medium   | 불확실성·근거 의존성 미반영                   | SE/CI 저장은 가능하지만 최적화는 비가중 평균절대오차 중심                                           |

### 특히 IPF의 수렴 판정

[`calibration.py`의 `reweight_beneficiaries`](https://github.com/SaehwanPark/medicare-synth/blob/main/src/medicare_synth/calibration.py?utm_source=chatgpt.com#L527-L637)를 보면 각 constraint를 보정한 다음 바로 그 constraint의 오차를 검사합니다.

그러나 IPF에서는 뒤에 적용한 보정이 앞서 맞춰 놓은 제약을 다시 변화시킬 수 있습니다.

따라서 올바른 종료 조건은 한 번의 전체 보정 순회가 끝난 뒤 모든 제약의 잔여 오차를 재평가하는 것이어야 합니다.

실제 [`Phase 4 보고서`](https://github.com/SaehwanPark/medicare-synth/blob/main/reports/phase4/known_truth_experiment.json?utm_source=chatgpt.com)에는 Level B가 `converged=true`라고 보고하면서도 calibration MAE는 약 0.000729로 남아 있습니다. 기본 수렴 허용오차 \\(10^{-6}\\)보다 큰 값입니다.

이를 수정하고, 종료 시 모든 제약이 허용오차 안에 있는지를 검증하는 테스트를 추가해야 합니다.

또 다른 중요한 부분은 `n_missing`입니다. 앞으로 문헌 목표가 수십 개로 늘어나면 계산할 수 없는 제약을 단순히 제외하는 것이 오히려 낮은 MAE를 만들어낼 위험이 있습니다.

조율 대상으로 승인된 제약을 계산할 수 없다면 성공이 아니라 실패 또는 명시적 미충족 상태로 처리해야 합니다.

이 분석은 실제 소스와 저장된 보고서를 기반으로 한 정적 감사입니다. 저장소 전체 테스트 스위트를 실행한 결과는 아닙니다.

## 4. 권장 아키텍처: 공통 모델과 목적별 world의 분리

제시한 세 가지 목표를 모두 만족시키려면 다음 구조를 권장합니다.

Literature Evidence Registry

CMS aggregates · Research studies · Methodological definitions

Evidence IR + Analysis Compiler

Population · Estimand · Adjustment · Uncertainty · Compatibility

Continually Calibrated Base Population Model

공통 확률분포 · 관계 구조 · 버전별 파라미터 · Calibration history

핵심 신규 계층

General world

기준 모집단

Cohort world

질환·연구별

Scenario world

민감도·대안

Synthetic Data Releases + Evaluation

CSV/Parquet · Manifests · Fidelity reports · Workflow tests

### 핵심 결정: 데이터셋보다 생성모형을 중심 자산으로 유지

궁극적으로 매우 큰 pre-calibrated 데이터셋을 제공하는 것은 가능합니다.

하지만 그 자체를 주된 학습 대상으로 삼는 것은 권장하지 않습니다.

대신 다음 두 가지를 분리해야 합니다.

Base Population Model

문헌으로부터 조율된 확률분포와 조건부 관계, 생성 파라미터, 코호트 정의를 보유하는 버전 관리 대상입니다.

Materialized Dataset

특정 모델 버전, 모집단, 표본 크기, 난수 시드를 사용해 생성한 데이터입니다.

이렇게 하면 공통 모델이 개선될 때 새로운 대규모 데이터셋을 생성할 수 있고, 과거 데이터셋도 정확히 재현할 수 있습니다.

또한 연구자가 10만 명 또는 1,000만 명 규모의 데이터를 원해도 새로운 조율 과정 없이 동일한 모델에서 표본을 생성할 수 있습니다.

단, 표본 크기를 늘린다고 문헌에 없는 관계가 현실적으로 변하지는 않습니다.

### 목적별 world는 공통 모델에서 분기해야 한다

여기서 world를 크게 두 종류로 나누면 좋겠습니다.

Cohort-conditioned world는 공통 모델의 특정 부분을 추출합니다. 예를 들어 2021년 FFS, 65세 이상, 당뇨 환자만 대상으로 하는 데이터입니다. 새로운 근거를 추가하지 않아도 공통 모델의 조건부 분포를 사용합니다.

Locally calibrated world는 공통 모델을 초기값으로 하되, 특정 연구 목적에 적합한 문헌 제약을 추가로 적용합니다.

이때 다음 원칙을 권장합니다.

\\[ P\_{\text{world}} = \operatorname{Calibrate} \left(P\_{\text{base}},\mathcal E\_{\text{local}}\right) \\]

즉, purpose-specific world는 처음부터 다시 만드는 별개의 모델이 아니라 공통 모델의 파생형입니다.

하지만 국소적인 조율이 공통 모델을 변경해서는 안 됩니다. 별도 버전의 world를 생성해야 합니다.

## 5. Inferential calibration: 가장 중요한 신규 기능

세 번째 목표는 단순한 부가 기능이 아니라 프로젝트의 연구적 가치를 크게 높일 수 있는 요소입니다.

### 5.1. 무엇을 맞춰야 하는가?

가상의 연구에서 다음 결과를 보고했다고 가정하겠습니다.

| 연구 결과                | 문헌 값 |
| -------------------- | ---- |
| 당뇨 유병률               | 28%  |
| 당뇨 환자 입원 위험          | 13%  |
| 당뇨와 입원의 adjusted OR  | 1.45 |
| 심부전과 입원의 adjusted HR | 1.80 |

위 수치는 방법 설명을 위한 가상 예시이며, 실제 Medicare 문헌에서 추출한 조율 목표가 아닙니다.

현재 시스템은 첫 번째와 두 번째 유형의 통계를 다룰 수 있습니다.

새 시스템은 세 번째와 네 번째 결과도 사용할 수 있어야 합니다.

하지만 이를 생성모형 내부의 관계 파라미터에 직접 입력해서는 안 됩니다.

예를 들어 adjusted OR 1.45라는 결과는 다음 분석에서 도출된 값일 수 있습니다.

\\[ \operatorname{logit}P(Y=1) = \alpha+\beta_D D+\beta_A A+\beta_S S+\cdots \\]

이 경우 조율 목표는 생성모형 내부의 \\(\beta_D\\)가 아니라, \*\*생성된 데이터에 동일한 분석을 적용했을 때 얻는 \\(\exp(\hat\beta_D)\\)\*\*입니다.

이 구분은 중요합니다.

원래의 연구에서 사용한 회귀분석이 복잡하거나 편향이 있거나 조정변수가 달라져도, 그 분석을 수행한 결과가 문헌과 호환되도록 하는 것이 목적이기 때문입니다.

### 5.2. 이를 구현하는 가장 적절한 방법: Indirect inference

이 접근은 통계학에서 indirect inference 또는 더 일반적인 simulation-based minimum-distance estimation과 연결됩니다.

생성모형의 내부 파라미터를 직접 관측할 수 없더라도, 시뮬레이션 데이터에 특정 분석을 적용하고 그 결과를 관측된 통계량과 비교하여 모델을 조율하는 방식입니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://onlinelibrary.wiley.com\&sz=32)

onlinelibrary.wiley.com+1



구체적으로 다음 과정을 반복합니다.

1

문헌 분석 명세 작성

Eligibility, outcome, exposure, adjustment, estimator

2

현재 모델에서 데이터 생성

해당 연구의 모집단과 관찰 기간을 재현

3

동일한 통계분석 실행

Logistic regression, Poisson regression, Cox model 등

4

문헌 추정치와 비교

Point estimate, uncertainty, compatibility

5

생성모형 파라미터 업데이트

다른 문헌 제약을 동시에 고려하며 재조율

단순한 예를 들면, 문헌에서 보고한 adjusted OR이 1.45일 때 생성된 데이터에서는 다음과 같은 결과가 나올 수 있습니다.

예시: 반복 조율에 따른 회귀분석 결과

실제 프로젝트 실행 결과가 아닌 가상 과정입니다.

Synthetic adjusted ORLiterature target

11.522.53초기1차2차3차4차

중요한 것은 adjusted OR 자체만 맞추는 것이 아니라, 그 과정에서 유병률, 연령 분포, 심부전과 당뇨의 관계 등 기존에 만족한 제약도 검사한다는 점입니다.

### 5.3. Inferential estimand를 제대로 정의해야 한다

이 목표를 구현하려면 Evidence IR을 확장해야 합니다.

특히 다음 정보들이 기계적으로 실행 가능해야 합니다.

| 영역                 | 필요한 표현                                              |
| ------------------ | --------------------------------------------------- |
| Population         | Medicare program, year, enrollment, eligibility     |
| Exposure / Outcome | 정의, 코드, 시점, 관찰 기간                                   |
| Estimand           | OR, RR, RD, HR, regression coefficient 등            |
| Adjustment         | Covariate set, coding, interaction, transformations |
| Estimator          | Logistic, Poisson, Cox, standardization 등           |
| Study design       | Matching, weighting, sampling, censoring            |
| Uncertainty        | SE, CI, 표본 크기, 근거 간 의존성                             |
| Compatibility      | 일치, 근사 실행, 실행 불가                                    |
| Provenance         | 논문 위치, 추출 버전, 검토 결과                                 |

단순히 `estimator: "cox"` 같은 문자열을 넣는 것으로는 부족합니다.

그 문자열을 해당 코호트와 이벤트 정의에 맞는 실제 실행 가능한 분석 명세로 컴파일해야 합니다.

또한 동일한 OR이나 HR이라도 조정변수와 marginal/conditional 정의가 다르면 같은 통계량이 아닙니다. 특히 OR과 HR의 noncollapsibility는 이 구분을 매우 중요하게 만듭니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://pmc.ncbi.nlm.nih.gov\&sz=32)

pmc.ncbi.nlm.nih.gov



처음부터 모든 통계분석을 지원하기보다는 다음 순서를 추천합니다.

1. Crude risk ratio, risk difference, odds ratio
2. Adjusted logistic regression
3. Poisson regression과 event rate
4. Survival analysis와 Cox regression
5. Matching, propensity-score weighting, subgroup interaction 등 복합 추정기

여기서 2단계만 성공적으로 구현해도 현재 프로젝트보다 훨씬 폭넓은 문헌을 calibration 대상으로 사용할 수 있습니다.

## 6. Continual calibration을 위한 최적화 구조

여러 문헌의 결과를 동시에 맞추려면 더 일반적인 목적함수가 필요합니다.

개념적으로 다음처럼 정의할 수 있습니다.

\\[ \begin{aligned} \theta\_{v+1} =\arg\min\_\theta\\;& L\_{\text{evidence}}(\theta;\mathcal E\_{v+1})\\\ &+\lambda L\_{\text{preservation}}(\theta,\theta_v)\\\ &+\gamma L\_{\text{structure}}(\theta) \end{aligned} \\]

여기서:

- \\(L\_{\text{evidence}}\\): 새 문헌과 기존 문헌의 분석 결과 차이
- \\(L\_{\text{preservation}}\\): 이전 모델에서 불필요하게 멀어지는 것에 대한 페널티
- \\(L\_{\text{structure}}\\): 자료의 구조적·시간적·논리적 제약 위반

구조적 불변 조건 중 일부는 페널티가 아니라 hard constraint로 처리하는 것이 적절합니다.

문헌 비교는 단순한 절대오차보다 불확실성을 고려한 형태가 유용합니다.

예를 들어 서로 독립적인 근거라면:

\\[ L\_{\text{evidence}} = \sum\_{j=1}^{K} w_j \rho\left( \frac{ g_j(P\_\theta)-\hat\eta_j }{ s_j } \right) \\]

여기서 \\(g_j(P\_\theta)\\)는 합성 데이터에 해당 논문의 분석을 실행한 결과이고, \\(\hat\eta_j\\)는 문헌에서 보고한 값입니다. \\(s_j\\)는 비교에 적합한 불확실성 척도입니다.

실제 문헌들이 같은 CMS 모집단이나 데이터베이스를 공유한다면 독립성 가정은 부적절하므로, 근거 간 공분산이나 source-cluster 단위의 목적함수가 필요합니다.

이것은 기존 코드에서 문헌들의 의존 가능성을 기록하지만 실제 목적함수에는 반영하지 않는 부분을 보완합니다.

### 새 문헌을 수집할수록 반드시 더 현실적이 되는 것은 아니다

이 부분은 프로젝트 전체의 설계 원칙으로 명문화할 필요가 있습니다.

가령 문헌 A에서는 당뇨 유병률이 27%이고 문헌 B에서는 32%라고 하더라도, 반드시 두 문헌 중 하나가 잘못되었다는 뜻은 아닙니다.

연도, 연령, 진단 알고리즘, FFS 포함 기준이 다를 수 있습니다.

따라서 일반적인 조율 엔진은 이런 상황을 자동으로 29.5%로 절충해서는 안 됩니다.

먼저 두 연구가 실제로 같은 estimand를 측정했는지를 판단해야 합니다.

실제로 CMS CCW에서도 27-condition과 30-condition 정의가 함께 존재하며 알고리즘 변경은 유병률의 비교 가능성에 영향을 줍니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www2.ccwdata.org\&sz=32)

Chronic Conditions Data Warehouse



따라서 Evidence Registry에는 단순한 finding의 집합 외에, 다음 관계를 표현할 수 있어야 합니다.

Compatible, overlapping, transport-dependent, contradictory, superseded.

이러한 관계를 기반으로 새 근거를 공통 모델에 적용할지, 특정 context에만 적용할지, 별도의 대안 world를 만들지 결정해야 합니다.

## 7. 목표 1에 대한 중요한 현실적 제약: Medicare 자료에 수렴할 수 있는가?

여기는 기대치를 구분할 필요가 있습니다.

문헌이 늘어나면서 실제 Medicare 모집단의 여러 특성에 더 가깝게 접근하는 것은 가능합니다. 그러나 전체 joint distribution이 실제 Medicare 자료에 수렴한다는 보장은 없습니다.

예를 들어 다음 세 가지를 정확히 알고 있다고 가정하겠습니다.

\\[ P(D)=0.28 \\]

\\[ P(H)=0.12 \\]

\\[ P(I\mid D)=0.13 \\]

이 세 숫자를 만족하는 확률분포는 무수히 많습니다.

특히 다음은 여전히 알 수 없습니다.

\\[ P(D,H),\quad P(I\mid D,H),\quad P(I\mid D,H,A,S) \\]

현재 Phase 5의 실제 보고서가 이 문제를 잘 보여줍니다.

World 2 · 6,000명

# 404

입원 claims

당뇨가 없는 사람의 입원 확률 4%

World 3 · 6,000명

# 572

입원 claims

당뇨가 없는 사람의 입원 확률 8%

두 world는 동일한 세 문헌 목표를 만족하도록 조율되었지만, 입원 claims는 크게 다릅니다. 이 차이는 현재 근거가 제한하지 않는 배경 입원 위험을 다르게 설정했기 때문입니다.

출처: [Phase 5 world family report](https://github.com/SaehwanPark/medicare-synth/blob/main/reports/phase5/world_family_summary.json?utm_source=chatgpt.com)

이는 현재 시스템의 실패라기보다 문헌 제약만으로는 식별할 수 없는 분포의 차이입니다.

장기적으로는 많은 문헌을 추가해 가능한 분포의 범위를 좁힐 수 있습니다. 그래도 관측되지 않은 상관관계나 복잡한 환자 경과는 끝까지 불확실할 수 있습니다.

따라서 최종 제품은 하나의 거대한 데이터셋뿐 아니라, 여러 합리적인 world 사이에서 연구 결과가 얼마나 안정적인지를 평가하는 기능을 유지해야 합니다.

이 점은 기존 연구 playground라는 목적과도 잘 맞습니다.

## 8. 권장 개발 로드맵

현재 ROADMAP의 Phase 6 independent evaluation은 그대로 진행하는 것이 좋습니다. 다만 그 이후의 Phase 7을 단순한 literature expansion으로 두기보다는, 새로운 아키텍처로 전환하는 단계로 세분화할 것을 제안합니다.

| 단계                          | 주요 작업                                                          | 완료 기준                                 |
| --------------------------- | -------------------------------------------------------------- | ------------------------------------- |
| A. Correctness hardening    | IPF 수렴 오류, missing-target 처리, 모집단 정렬, 검증 강화                    | 모든 승인된 제약을 정확히 평가하고 실패를 숨기지 않음        |
| B. Inferential Evidence IR  | Estimand·analysis 표현 확대, adjusted logistic regression MVP      | 실제 문헌의 조정 회귀분석을 재현 가능하게 실행            |
| C. Richer joint synthesizer | Age, sex, diabetes, HF, IP 간 다변량 관계 지원                         | 다양한 유병률과 adjusted association을 동시에 제어 |
| D. Continual calibration    | 모델 상태, incremental evidence registry, preservation loss, 회귀 검증 | 새로운 문헌 추가 후 이전 모델과의 차이 및 유지 여부 확인     |
| E. Base/world separation    | 공통 reference model에서 context-specific world 파생                 | 추가 조율의 영향이 해당 world에 국한됨              |
| F. Scaling and evaluation   | 추가 질환, longitudinal data, 다양한 estimator, 대규모 데이터 생성            | 여러 모집단에서 독립적인 문헌 및 연구 워크플로 평가 통과      |

이 중 가장 먼저 시도할 실질적인 MVP는 다음과 같습니다.

추천: Joint + Inferential Calibration MVP

첫 구현 목표

기존 2021 FFS diabetes–HF–hospitalization context를 유지하면서, 새로운 조건부 관계와 조정 회귀계수를 동시에 맞추는 실험입니다.

필수 목표

- 기존 유병률·입원 위험 제약 유지
- 당뇨–심부전 comorbidity 관계 추가
- Age/sex에 따른 입원 위험 차이 추가
- Adjusted OR 하나를 실제 문헌에서 formalize하고 calibration
- 새 제약을 추가하기 전후의 모든 기존 목표 재평가

문헌에 조정 회귀결과가 적절히 보고되어 있고 생성변수가 지원된다는 전제 아래, 이 실험이 성공하면 목표 1–3을 관통하는 기술적 가능성을 입증할 수 있습니다.

여기서 중요한 것은 100편의 문헌을 수집하는 것보다 먼저 기존 세 개의 제약을 유지하면서 새로운 inferential constraint 하나를 추가할 수 있는지 검증하는 것입니다.

이것이 성공하면 문헌을 추가하는 것은 상대적으로 반복 가능한 엔지니어링 작업이 됩니다.

반대로 이 실험이 실패한다면 원인은 주로 Evidence IR, joint generator, calibration optimizer 중 하나에 있을 가능성이 큽니다. 문제를 작게 분리해 해결할 수 있습니다.

## 9. 기존 문서와 프로젝트 정의의 변경

이번 목표를 채택한다면 현재 문서의 몇 가지 전략적 표현도 변경해야 합니다.

특히 [`SPEC.md`](https://github.com/SaehwanPark/medicare-synth/blob/main/SPEC.md?utm_source=chatgpt.com)는 one universal synthetic Medicare distribution을 명시적 non-goal로 규정하고 있습니다.

이전 목표에서는 합리적인 결정이었지만, 이제는 다소 수정할 필요가 있습니다.

제가 권장하는 새로운 프로젝트 정의는 다음과 같습니다.

> Medicare-Synth is a literature-constrained synthetic population modeling system that incrementally calibrates a shared Medicare-like generative model against published aggregate and inferential findings. It supports reproducible general-purpose datasets and specialized research worlds, enabling researchers to develop, validate, and stress-test study designs before accessing restricted Medicare data.

다만 반드시 명확히 유지할 부분이 있습니다.

실제 Medicare beneficiary나 claim을 복원하는 것이 목적이 아니고, 문헌과의 일치가 실제 Medicare 자료의 대표성이나 환자 수준의 정확성을 보장하지 않는다는 점입니다.

사용자에게 중요한 것은 실제 Medicare 자료의 완벽한 모사보다도, 제한된 실제 데이터에 접근하기 전에 분석 파이프라인을 시험할 수 있을 만큼의 현실적인 통계적 관계와 데이터 구조입니다.

## 최종 결론

이번 감사를 통해 가장 중요하다고 판단한 것은 세 가지입니다.

첫째, 현재 프로젝트의 가장 중요한 자산은 개별 synthetic dataset이 아니라 Evidence IR과 재현 가능한 calibration pipeline입니다. 이 자산을 유지하면서, 누적해서 업데이트되는 공통 생성모형을 도입하는 것이 다음 단계입니다.

둘째, 문헌을 단순한 marginal statistics의 집합으로 취급해서는 충분하지 않습니다. 문헌에서 실시한 분석 자체를 합성 데이터에 다시 실행하고 비교하는 inferential calibration이 필요합니다. 이것이 프로젝트의 연구적 차별점이 될 수 있습니다.

셋째, 모든 문헌을 만족하는 유일한 Medicare world를 찾으려 하기보다는, 문헌이 제약하는 공통 모델과 그 제약으로도 식별되지 않는 불확실성을 표현하는 여러 world를 함께 지원해야 합니다.

현재의 Phase 0–5는 폐기하거나 전면 재작성할 필요가 없습니다. 다만 Phase 6 이후에는 단순히 문헌과 질환을 확장하는 대신, 위 세 가지를 실현하는 아키텍처로 발전시키는 것이 적절합니다.

가장 높은 우선순위는 다변량 생성모형 + adjusted regression 실행 + 기존 제약을 보존하는 incremental calibration을 하나의 작은 end-to-end 실험에서 검증하는 것입니다. 이것이 성공해야 거대한 pre-calibrated Medicare dataset이라는 장기 목표도 기술적으로 설득력을 갖게 됩니다.