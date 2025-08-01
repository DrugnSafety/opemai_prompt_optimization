# 🚀 GPT-4.1 Prompt Optimizer

**Human-in-the-Loop 프롬프트 최적화 시스템**

OpenAI의 [Prompt Optimization Cookbook](https://cookbook.openai.com/examples/optimize_prompts)을 기반으로 하여, 사용자 피드백을 통한 반복적 개선이 가능한 고도화된 프롬프트 최적화 도구입니다.

## ✨ 주요 기능

### 🔍 **자동 프롬프트 분석**
- **명확성 검사**: 모호한 표현 및 역할 정의 문제 감지
- **구체성 검사**: 추상적 지시사항 및 출력 형식 문제 식별
- **지시사항 준수 검사**: 상충되는 지시사항 및 모순점 탐지
- **에이전틱 능력 검사**: GPT-4.1 가이드라인 기반 에이전틱 기능 분석

### 🛠️ **자동 최적화**
- GPT-4.1 Prompting Guide 기반 프롬프트 개선
- Few-shot 예제 일관성 검사 및 수정
- 구조화된 출력 형식 명시
- 에이전틱 능력 강화 (지속성, 계획 수립, 반성적 사고)

### 💬 **Human-in-the-Loop 개선**
- 사용자 피드백 기반 추가 최적화
- 실시간 피드백 분석 및 프롬프트 수정
- 반복적 개선을 통한 점진적 품질 향상
- Before/After 비교 및 변경사항 추적

### 🎨 **사용자 친화적 인터페이스**
- Streamlit 기반 웹 인터페이스
- 5단계 탭 구조 (입력 → 분석 → 결과 → 최적화 → 피드백)
- 실시간 진행 상황 표시
- 결과 다운로드 및 공유 기능

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   프롬프트 입력   │───▶│   자동 분석      │───▶│   최적화 결과    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Few-shot 예제   │    │   병렬 검사기    │    │   피드백 입력    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   문제 감지      │    │   피드백 분석    │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   자동 수정      │    │   추가 개선      │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd openai_prompt_optimization

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. 실행

#### 웹 인터페이스 (권장)
```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501` 접속

#### 명령줄 테스트
```bash
python test_optimizer.py
```

## 📋 사용법

### 1. 프롬프트 입력
- 메인 프롬프트 작성
- Few-shot 예제 추가 (선택사항)
- 고급 설정 구성

### 2. 자동 분석
- 4개 전문 Agent가 병렬로 분석
- 실시간 진행 상황 확인
- 발견된 문제점 검토

### 3. 최적화 결과
- 개선된 프롬프트 확인
- 적용된 변경사항 검토
- Before/After 비교

### 4. 피드백 기반 개선
- 최적화된 프롬프트에 대한 피드백 제공
- 추가 개선 요청
- 반복적 개선 수행

## 🔧 기술 스택

### 백엔드
- **Python 3.13**: 최신 Python 버전 활용
- **FastAPI**: 비동기 웹 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **asyncio**: 비동기 처리
- **OpenAI API**: GPT-4.1 모델 활용

### 프론트엔드
- **Streamlit**: 대화형 웹 애플리케이션
- **Tailwind CSS**: 모던 UI 디자인
- **JavaScript**: 동적 인터랙션

### 개발 도구
- **Black**: 코드 포맷팅
- **isort**: import 정렬
- **mypy**: 타입 검사
- **pytest**: 테스트 프레임워크

## 📊 OpenAI Cookbook과의 차이점

### 🔄 **주요 개선사항**

#### 1. **의존성 문제 해결**
```python
# 원본 (의존성 충돌)
from agents import Agent, Runner, set_default_openai_client, trace

# 개선된 버전 (자체 구현)
class Agent:
    def __init__(self, name: str, model: str, output_type: type, instructions: str):
        self.name = name
        self.model = model
        self.output_type = output_type
        self.instructions = instructions

class Runner:
    @staticmethod
    async def run(agent: Agent, input_data: str, progress_callback=None):
        # 자체 구현된 Agent 실행 로직
```

#### 2. **GPT-4.1 가이드라인 통합**
```python
# 새로운 Agent 타입 추가
clarity_checker = Agent(
    name="clarity_checker",
    model="gpt-4.1",
    output_type=Issues,
    instructions="명확성 분석..."
)

specificity_checker = Agent(
    name="specificity_checker", 
    model="gpt-4.1",
    output_type=Issues,
    instructions="구체성 분석..."
)

instruction_following_checker = Agent(
    name="instruction_following_checker",
    model="gpt-4.1", 
    output_type=Issues,
    instructions="지시사항 준수 분석..."
)

agentic_capability_checker = Agent(
    name="agentic_capability_checker",
    model="gpt-4.1",
    output_type=Issues, 
    instructions="에이전틱 능력 분석..."
)
```

#### 3. **Human-in-the-Loop 시스템**
```python
# 피드백 분석 및 개선
async def revise_prompt_with_feedback(
    optimized_prompt: str,
    user_feedback: str,
    progress_callback=None
) -> Dict[str, Any]:
    """피드백을 기반으로 최적화된 프롬프트를 추가 개선"""
    
    # 1단계: 피드백 분석
    feedback_analysis_result = await Runner.run(
        feedback_analyzer,
        json.dumps({"user_feedback": user_feedback}),
        progress_callback
    )
    
    # 2단계: 프롬프트 수정
    revision_result = await Runner.run(
        prompt_reviser,
        json.dumps({
            "original_optimized_prompt": optimized_prompt,
            "user_feedback": user_feedback
        }),
        progress_callback
    )
    
    return {
        "original_optimized_prompt": optimized_prompt,
        "user_feedback": user_feedback,
        "feedback_analysis": feedback_analysis_result.final_output.model_dump(),
        "revision_details": revision_result.final_output.model_dump(),
        "revised_prompt": revision_result.final_output.revised_prompt,
        "changes_made": revision_result.final_output.changes_made,
        "feedback_addressed": revision_result.final_output.feedback_addressed
    }
```

#### 4. **웹 인터페이스 추가**
```python
# Streamlit 기반 사용자 인터페이스
import streamlit as st

# 5단계 탭 구조
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 프롬프트 입력", 
    "🔍 분석 진행", 
    "📊 분석 결과", 
    "✨ 최적화 결과",
    "🔄 피드백 & 리비전"
])
```

### 🔧 **버전 호환성 문제 해결**

#### 1. **Python 3.13 호환성**
- 최신 Python 버전의 타입 힌트 활용
- `asyncio` 비동기 처리 최적화
- Pydantic v2 모델 사용

#### 2. **의존성 충돌 해결**
```python
# 문제: openai-agents 패키지 버전 충돌
# 해결: 자체 Agent/Runner 구현

class Agent:
    """OpenAI Agents SDK 호환 Agent 클래스"""
    def __init__(self, name: str, model: str, output_type: type, instructions: str):
        self.name = name
        self.model = model
        self.output_type = output_type
        self.instructions = instructions

class Runner:
    """Agent 실행을 위한 Runner 클래스"""
    @staticmethod
    async def run(agent: Agent, input_data: str, progress_callback=None):
        # 시뮬레이션된 Agent 실행 로직
        # 실제 OpenAI API 호출로 대체 가능
```

#### 3. **비동기 처리 개선**
```python
# 원본: 동기 처리
# 개선: asyncio 기반 비동기 처리
async def optimize_prompt_comprehensive(
    prompt: str,
    few_shot_messages: List[ChatMessage] = None,
    progress_callback=None
) -> Dict[str, Any]:
    """종합적 프롬프트 최적화"""
    
    # 병렬 Agent 실행
    tasks = [
        Runner.run(clarity_checker, prompt, progress_callback),
        Runner.run(specificity_checker, prompt, progress_callback),
        Runner.run(instruction_following_checker, prompt, progress_callback),
        Runner.run(agentic_capability_checker, prompt, progress_callback)
    ]
    
    results = await asyncio.gather(*tasks)
```

## 📈 성능 개선

### 1. **병렬 처리**
- 4개 Agent 동시 실행으로 분석 시간 단축
- `asyncio.gather()` 활용

### 2. **캐싱 시스템**
- 분석 결과 캐싱
- 중복 분석 방지

### 3. **점진적 개선**
- Human-in-the-Loop를 통한 반복적 최적화
- 피드백 기반 지속적 개선

## 🧪 테스트

### 자동화된 테스트
```bash
# 전체 테스트 실행
python test_optimizer.py

# 개별 테스트
python -m pytest tests/
```

### 테스트 시나리오
1. **기본 프롬프트 최적화**
2. **Few-shot 예제 포함 최적화**
3. **피드백 기반 추가 개선**
4. **에러 처리 및 예외 상황**

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **문서**: [Wiki](https://github.com/your-repo/wiki)
- **이메일**: your-email@example.com

## 🙏 감사의 말

- [OpenAI Cookbook](https://cookbook.openai.com/examples/optimize_prompts) 팀
- [GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)
- Streamlit 개발팀
- 모든 기여자들

---

**Made with ❤️ for better AI prompts** 