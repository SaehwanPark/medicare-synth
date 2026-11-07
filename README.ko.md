[English](README.md) · **한국어**

# Medicare-Synth

제한된 메디케어 자료를 다루기 전에, 메디케어와 비슷한 합성 데이터로 연구 아이디어를 살펴보고 분석 코드를 시험할 수 있습니다. Medicare-Synth는 실제 파일과 비슷한 구조를 제공하고, 범위를 한 가지 연구 상황으로 좁히면 공개된 통계 일부에 맞춰 합성 집단을 조정할 수 있습니다. 연구 준비와 방법론을 시험하는 작업 공간이며, 메디케어 수급자의 실제 모습을 추정하는 자료는 아닙니다.

**[문서 사이트 (한국어)](https://saehwanpark.github.io/medicare-synth/ko/)** ·
[연구자 안내](https://saehwanpark.github.io/medicare-synth/ko/researchers/) ·
[개발자 안내 (영어)](https://saehwanpark.github.io/medicare-synth/developers/) ·
[소스](https://github.com/SaehwanPark/medicare-synth)

## 왜 만드나

CMS 제한 자료는 시간, 접근 권한, 작업 절차, 비용이 걸립니다. 메디케어 형태의 인공 표로 먼저 조인, 코호트 정의, 분석 코드를 고쳐 보면 자료이용계약(DUA)과 추출본 작업 전에 문제를 찾을 수 있습니다. 그렇다고 합성 결과가 메디케어의 실제 결과인 것은 아닙니다.

## 지금 할 수 있는 일

- **구조 연습:** 파일 관계, 키, 올바른 예시와 일부러 틀린 예시를 살펴보고, 개발 도구로 일반 CSV/Parquet를 내보낼 수 있습니다.
- **범위를 고정한 근거 보정 시범:** 2021년 전통적 메디케어(Original Medicare) 행위별 수가(FFS)와 비슷한 65세 이상 집단에 당뇨병·심부전 표지를 두고, 원인과 무관한 입원 여부를 세 가지 공개 수치에 맞춰 조정할 수 있습니다.
- **코드와 절차 시험:** 여러 합성 세계(world)에서 정의와 가정 민감도를 연습할 수 있습니다.

지금은 임의 질환·연도 보정, 웹사이트에서 보정 데이터를 한 번에 내려받기, 모집단·인과·임상 주장을 지원하지 않습니다.

자세한 내용: [할 수 있는 일](https://saehwanpark.github.io/medicare-synth/ko/researchers/what-you-can-do/).

## 구체적인 예 하나

고정 맥락 `mvp-2021-om-ffs-diabetes-ip`: 2021년 FFS와 비슷한 인공 코호트, 65세 이상, 당뇨병에서 모든 원인의 입원 여부(진단이 특정된 입원이 아님)로 이어집니다. 보정에 쓰는 기준값은 대략적인 예시입니다. 당뇨병 유병률 약 27.7%(2018년 출처), 심부전 약 12%(2022년 출처), 당뇨병이 있는 사람의 입원 위험 약 13%(이보다 약한 업계 사전 정보)입니다. 저장된 5단계 합성 세계는 수급자 6,000명에서 이 목표에 맞출 수 있으면서도, 배경 입원 위험을 자유롭게 두면 입원 청구 건수가 달라질 수 있습니다(예: **404**건과 **572**건).

→ [따라 해 보기](https://saehwanpark.github.io/medicare-synth/ko/researchers/diabetes-hospitalization-example/)

## 현재 한계

- 모든 질환·연도를 다루지 않습니다. 시범은 맥락이 고정되어 있고 실험적입니다.
- 임상, 장기 추적, 제공자 현실을 모두 재현한다고 말하지 않습니다.
- 보정에 성공해도 연구에 일반적으로 쓸 수 있다는 뜻은 아닙니다. 6단계(Phase 6) 평가는 **진행 중**입니다.
- 문서 사이트에 브라우저 생성기나 원클릭 보정 CSV는 없습니다.
- 합성 결과를 메디케어 모집단의 결과로 보고하면 안 됩니다.

→ [한계와 범위](https://saehwanpark.github.io/medicare-synth/ko/researchers/limitations/)

## 시작하기

1. **연구자로 살펴보기** — [문서 사이트](https://saehwanpark.github.io/medicare-synth/ko/)와 [연구자 안내](https://saehwanpark.github.io/medicare-synth/ko/researchers/)를 읽습니다. 설명만 따라갈 때는 설치가 필요 없습니다.
2. **개발자로 설치해 사용하기** — Python 3.13+와 [`uv`](https://docs.astral.sh/uv/)가 필요합니다. [설치 (영어)](https://saehwanpark.github.io/medicare-synth/developers/installation/)와 [첫 실행 (영어)](https://saehwanpark.github.io/medicare-synth/developers/first-run/)을 보세요.

연구자가 바로 받을 수 있는 공개 다운로드는 아직 기술 협업이 필요할 수 있습니다. 웹사이트에 보정된 릴리스 파일이 준비되어 있다고 가정하지 마세요.

```shell
git clone https://github.com/SaehwanPark/medicare-synth.git
cd medicare-synth
uv sync
uv run medicare-synth validate --scenario valid_baseline_cohort
```

## 책임 있는 사용

생성된 추정치, 연관성, 모형 성능을 메디케어의 실증 결과로 인용하지 마세요. 가정, 근거의 기준점, 아직 남은 평가를 밝히세요. 코드 라이선스는 Apache-2.0입니다. 상위 원천 파일을 받을 때는 CMS 합성 자료의 이용 조건을 따로 확인하세요.

## 상태와 기여

고정된 시범에 대해 0–5단계는 끝났습니다. 6단계 독립 평가는 **진행 중**이고, 7단계는 예정되어 있습니다([`ROADMAP.md`](ROADMAP.md), 영어). 상태 문서도 영어입니다. [`SPEC.md`](SPEC.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`CHANGELOG.md`](CHANGELOG.md), [`LESSONS.md`](LESSONS.md). 기여 안내: [developers/contributing](https://saehwanpark.github.io/medicare-synth/developers/contributing/).

```shell
uv run pytest && uv run basedpyright && uv run ruff check .
uv sync --dry-run && git diff --check
```
