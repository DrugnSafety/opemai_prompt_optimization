# 🔧 MCP (Model Context Protocol) 통합 가이드

이 가이드는 프롬프트 최적화 기능을 MCP 서버로 구현하여 다른 AI 프로젝트에서 쉽게 활용하는 방법을 설명합니다.

## 📋 목차

1. [MCP란 무엇인가?](#mcp란-무엇인가)
2. [왜 MCP를 사용하는가?](#왜-mcp를-사용하는가)
3. [설치 및 설정](#설치-및-설정)
4. [제공되는 도구들](#제공되는-도구들)
5. [Claude Desktop 통합](#claude-desktop-통합)
6. [다른 클라이언트 통합](#다른-클라이언트-통합)
7. [사용 예시](#사용-예시)
8. [확장 및 커스터마이징](#확장-및-커스터마이징)
9. [트러블슈팅](#트러블슈팅)

---

## 🤖 MCP란 무엇인가?

**Model Context Protocol (MCP)**는 AI 모델이 외부 도구와 데이터에 안전하고 표준화된 방식으로 접근할 수 있게 하는 개방형 프로토콜입니다.

### 핵심 개념

- **표준화**: JSON-RPC 기반의 통일된 통신 방식
- **보안**: 안전한 샌드박스 환경에서 도구 실행
- **확장성**: 새로운 도구를 쉽게 추가 가능
- **호환성**: 다양한 AI 클라이언트에서 동일한 도구 사용

### 아키텍처

```
┌─────────────────┐    JSON-RPC     ┌─────────────────┐
│   AI Client     │◄─────────────────▶│   MCP Server    │
│                 │                  │                 │
│ • Claude Desktop│                  │ • prompt-optimizer │
│ • Cursor        │                  │ • 4개 전문 도구    │
│ • Custom Apps   │                  │ • GPT-4.1 최적화  │
└─────────────────┘                  └─────────────────┘
```

---

## 💡 왜 MCP를 사용하는가?

### Streamlit 웹 앱 vs MCP 서버

| 기능 | Streamlit 웹 앱 | MCP 서버 |
|------|----------------|----------|
| **접근성** | 웹 브라우저 필요 | AI 클라이언트에서 직접 사용 |
| **통합성** | 별도 앱 실행 | AI 워크플로우에 자연스럽게 통합 |
| **재사용성** | 단독 사용 | 다양한 프로젝트에서 재사용 |
| **자동화** | 수동 상호작용 | AI가 자동으로 도구 호출 |
| **표준화** | 커스텀 인터페이스 | MCP 표준 준수 |

### 주요 장점

1. **자연스러운 통합**: AI 대화 중에 자연스럽게 프롬프트 최적화 기능 사용
2. **자동화**: AI가 필요에 따라 자동으로 프롬프트 개선 제안
3. **재사용성**: 한 번 설정하면 모든 MCP 호환 클라이언트에서 사용
4. **확장성**: 새로운 도구를 쉽게 추가하여 기능 확장

---

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
# MCP 관련 패키지 설치
pip install -r requirements-mcp.txt

# 또는 개별 설치
pip install mcp pydantic openai streamlit
```

### 2. 환경 변수 설정

```bash
# .env 파일에 OpenAI API 키 설정
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. MCP 서버 테스트

```bash
# MCP 서버 기능 테스트
python test_mcp_client.py

# 실제 MCP 서버 실행 (별도 터미널)
python mcp_server.py
```

---

## 🛠️ 제공되는 도구들

우리 MCP 서버는 4개의 전문 도구를 제공합니다:

### 1. `optimize_prompt`
**종합적 프롬프트 최적화**

```json
{
  "name": "optimize_prompt",
  "description": "GPT-4.1 가이드라인에 따라 프롬프트를 종합적으로 분석하고 최적화합니다",
  "parameters": {
    "prompt": "최적화할 프롬프트 텍스트",
    "few_shot_messages": "Few-shot 예제 메시지들 (선택사항)",
    "include_analysis": "상세한 분석 결과 포함 여부 (기본값: true)"
  }
}
```

**예시 사용:**
```
AI에게: "optimize_prompt 도구를 사용해서 이 프롬프트를 개선해줘: 'Write a blog post about AI'"
```

### 2. `revise_with_feedback`
**피드백 기반 추가 개선**

```json
{
  "name": "revise_with_feedback", 
  "description": "사용자 피드백을 바탕으로 최적화된 프롬프트를 추가 개선합니다",
  "parameters": {
    "optimized_prompt": "이미 최적화된 프롬프트",
    "user_feedback": "사용자의 피드백",
    "include_analysis": "피드백 분석 결과 포함 여부 (기본값: true)"
  }
}
```

**예시 사용:**
```
AI에게: "revise_with_feedback 도구로 이 프롬프트를 '더 간단하게 만들어달라'는 피드백에 따라 개선해줘"
```

### 3. `analyze_prompt`
**프롬프트 분석 전용**

```json
{
  "name": "analyze_prompt",
  "description": "프롬프트를 분석하여 문제점만 찾아냅니다 (최적화하지 않음)",
  "parameters": {
    "prompt": "분석할 프롬프트 텍스트",
    "analysis_types": "수행할 분석 유형들 (clarity, specificity, instruction_following, agentic_capabilities)"
  }
}
```

**예시 사용:**
```
AI에게: "analyze_prompt 도구로 이 프롬프트의 문제점만 분석해줘"
```

### 4. `get_prompt_suggestions`
**도메인별 프롬프트 템플릿**

```json
{
  "name": "get_prompt_suggestions",
  "description": "특정 도메인이나 목적에 맞는 프롬프트 템플릿 및 제안사항을 제공합니다",
  "parameters": {
    "domain": "프롬프트 도메인 (coding, writing, analysis, creative, customer_service, education, general)",
    "task_type": "작업 유형 (debug, review, generate, summarize, translate)",
    "requirements": "특별 요구사항들"
  }
}
```

**예시 사용:**
```
AI에게: "get_prompt_suggestions 도구로 코딩 도메인의 디버깅용 프롬프트 템플릿을 만들어줘"
```

---

## 🖥️ Claude Desktop 통합

### 1. 설정 파일 위치

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. 설정 파일 내용

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "python",
      "args": ["/path/to/your/project/mcp_server.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "PYTHONPATH": "/path/to/your/project",
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 3. Claude Desktop 재시작

설정 파일을 수정한 후 Claude Desktop을 재시작하면 prompt-optimizer 도구들이 자동으로 로드됩니다.

### 4. 사용 확인

Claude Desktop에서:
```
"사용 가능한 도구들을 보여줘"
```

prompt-optimizer 관련 도구 4개가 표시되면 성공적으로 통합된 것입니다.

---

## 🔗 다른 클라이언트 통합

### Cursor (향후 MCP 지원시)

```json
{
  "mcp_servers": {
    "prompt-optimizer": {
      "command": "python",
      "args": ["mcp_server.py"],
      "working_directory": "/path/to/project"
    }
  }
}
```

### 커스텀 MCP 클라이언트

```python
import asyncio
from mcp.client import Client

async def use_prompt_optimizer():
    # MCP 클라이언트 생성
    client = Client()
    
    # MCP 서버 연결
    await client.connect("python", ["mcp_server.py"])
    
    # 도구 호출
    result = await client.call_tool(
        "optimize_prompt",
        {
            "prompt": "Write a summary",
            "include_analysis": True
        }
    )
    
    print(result)
```

### API 래퍼 생성

```python
from fastapi import FastAPI
from mcp.client import Client

app = FastAPI()

@app.post("/optimize-prompt")
async def optimize_prompt_api(prompt: str):
    client = Client()
    await client.connect("python", ["mcp_server.py"])
    
    result = await client.call_tool(
        "optimize_prompt",
        {"prompt": prompt}
    )
    
    return result
```

---

## 💡 사용 예시

### 기본 사용법

#### 1. 간단한 프롬프트 최적화

**사용자:**
```
이 프롬프트를 최적화해줘: "Write a blog post"
```

**Claude (MCP 도구 사용):**
```
optimize_prompt 도구를 사용해서 프롬프트를 분석하고 개선하겠습니다.

[도구 실행 중...]

# 🚀 프롬프트 최적화 결과

## 📊 최적화 요약
- **발견된 문제**: 3개
- **예상 개선율**: 75%

## ✨ 최적화된 프롬프트
```
You are a helpful AI assistant and expert writer. Write a blog post.

Please provide detailed, comprehensive responses with clear explanations.

Please keep going until the task is completely resolved, before ending your turn.
Plan extensively before taking action, and reflect on the outcomes of your actions.

Provide your response in a clear, structured format.
```

## 🔍 발견된 문제점
1. 역할이나 목표가 명확하게 정의되지 않았습니다
2. 출력 형식이나 구조에 대한 명시적 지침이 없습니다
3. 프롬프트가 너무 짧아 충분한 컨텍스트를 제공하지 못합니다
```

#### 2. 피드백 기반 개선

**사용자:**
```
위의 최적화된 프롬프트가 너무 길어. 더 간결하게 만들어줘.
```

**Claude (MCP 도구 사용):**
```
revise_with_feedback 도구를 사용해서 피드백을 반영하여 프롬프트를 개선하겠습니다.

[도구 실행 중...]

# 🔄 피드백 기반 프롬프트 개선 결과

## 📊 개선 요약
- **적용된 변경사항**: 2개
- **처리된 피드백**: 1개

## ✨ 개선된 프롬프트
```
You are an expert writer. Write a comprehensive, well-structured blog post.

Plan your approach and provide clear, engaging content.
```

## 🔧 적용된 변경사항
1. 불필요한 상세 지침 제거
2. 핵심 요구사항만 유지
```

#### 3. 도메인별 템플릿 생성

**사용자:**
```
코딩 프로젝트용 디버깅 프롬프트 템플릿을 만들어줘.
```

**Claude (MCP 도구 사용):**
```
get_prompt_suggestions 도구를 사용해서 코딩 도메인의 디버깅 프롬프트 템플릿을 생성하겠습니다.

[도구 실행 중...]

# 🎯 Coding 도메인 프롬프트 제안

## 🏗️ 기본 템플릿
```
You are an expert software developer and code reviewer.

# Guidelines:
- Always provide detailed explanations for code changes
- Include error handling and edge cases
- Follow best practices and coding standards
- Suggest performance improvements when applicable

Please keep going until the task is completely resolved, before ending your turn.
Plan extensively before taking action, and reflect on the outcomes of your actions.
```

## 💡 'debug' 작업을 위한 특화 프롬프트
```
You are an expert software developer and code reviewer.

Analyze this code and identify any bugs, performance issues, or security vulnerabilities. Provide specific fixes with explanations.
```

## 📝 추가 개선 제안
1. **명확한 출력 형식 지정**: 원하는 출력 형식(JSON, 마크다운, 구조화된 텍스트 등)을 명시하세요
2. **예제 제공**: Few-shot 예제를 추가하여 기대하는 응답 스타일을 명확히 하세요
3. **제약사항 명시**: 길이 제한, 사용할 언어, 피해야 할 내용 등을 명확히 하세요
4. **컨텍스트 제공**: 작업의 배경, 목적, 대상 독자 등의 컨텍스트를 제공하세요
```

### 고급 사용법

#### 1. 복잡한 프롬프트 분석

**사용자:**
```
이 프롬프트를 분석해줘. 최적화는 하지 말고 문제점만 찾아줘:

"You must always provide detailed answers, but keep responses brief. This is required but optional if needed."
```

**Claude (MCP 도구 사용):**
```
analyze_prompt 도구를 사용해서 프롬프트의 문제점만 분석하겠습니다.

[도구 실행 중...]

# 🔍 프롬프트 분석 결과

## 📊 분석 요약
- **분석 유형**: clarity, specificity, instruction_following, agentic_capabilities
- **발견된 문제**: 4개

## ⚠️ 발견된 문제점
1. 역할이나 목표가 명확하게 정의되지 않았습니다
2. 'must'과 'optional'와 같은 상충되는 지시사항이 포함되어 있습니다
3. 'required'과 'if needed'와 같은 상충되는 지시사항이 포함되어 있습니다
4. 출력 형식이나 구조에 대한 명시적 지침이 없습니다
```

#### 2. Few-shot 예제 포함 최적화

**사용자:**
```
이 프롬프트와 예제들을 함께 최적화해줘:

프롬프트: "Help users improve their writing"

예제들:
- 사용자: "Make this better: I went to store"
- 어시스턴트: "Better version: I went to the store"
- 사용자: "Fix this: The car is good"  
- 어시스턴트: "More descriptive: The car is excellent"
```

**Claude (MCP 도구 사용):**
```
optimize_prompt 도구를 사용해서 프롬프트와 Few-shot 예제들을 함께 최적화하겠습니다.

[도구 실행 중...]

# 🚀 프롬프트 최적화 결과

## 📊 최적화 요약
- **발견된 문제**: 3개
- **예상 개선율**: 70%

## ✨ 최적화된 프롬프트
```
You are a professional writing assistant and editor. Help users improve their writing.

Please provide detailed, comprehensive responses with clear explanations.

Please keep going until the task is completely resolved, before ending your turn.
Plan extensively before taking action, and reflect on the outcomes of your actions.

Provide your response in a clear, structured format.
```

## 💬 최적화된 Few-shot 예제
1. **user**: Make this better: I went to store.
2. **assistant**: Based on your request, here's a detailed response: Better version: I went to the store. Let me know if you need further clarification or have additional questions.
3. **user**: Fix this: The car is good.
4. **assistant**: Based on your request, here's a detailed response: More descriptive: The car is excellent. Let me know if you need further clarification or have additional questions.
```

---

## ⚙️ 확장 및 커스터마이징

### 새로운 도구 추가

1. **도구 정의 추가**

```python
# mcp_server.py의 handle_list_tools 함수에 추가
Tool(
    name="validate_prompt_safety",
    description="프롬프트의 안전성과 편향성을 검사합니다",
    inputSchema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string", 
                "description": "검사할 프롬프트"
            },
            "safety_level": {
                "type": "string",
                "enum": ["basic", "strict", "enterprise"],
                "description": "안전성 검사 수준"
            }
        },
        "required": ["prompt"]
    }
)
```

2. **핸들러 메서드 구현**

```python
async def _handle_validate_prompt_safety(self, arguments: dict) -> list[TextContent]:
    """프롬프트 안전성 검사"""
    prompt = arguments.get("prompt", "")
    safety_level = arguments.get("safety_level", "basic")
    
    # 안전성 검사 로직 구현
    safety_issues = self._check_prompt_safety(prompt, safety_level)
    
    response = self._format_safety_results(safety_issues)
    return [TextContent(type="text", text=response)]
```

3. **도구 호출 라우팅 추가**

```python
# handle_call_tool 함수에 추가
elif name == "validate_prompt_safety":
    return await self._handle_validate_prompt_safety(arguments)
```

### 커스텀 분석 로직

```python
class CustomPromptAnalyzer:
    """커스텀 프롬프트 분석기"""
    
    def analyze_bias(self, prompt: str) -> List[str]:
        """편향성 분석"""
        bias_indicators = [
            "gender-specific terms",
            "racial stereotypes", 
            "cultural assumptions"
        ]
        
        found_biases = []
        for indicator in bias_indicators:
            if self._detect_bias(prompt, indicator):
                found_biases.append(f"Potential {indicator} detected")
        
        return found_biases
    
    def analyze_complexity(self, prompt: str) -> Dict[str, Any]:
        """복잡도 분석"""
        return {
            "readability_score": self._calculate_readability(prompt),
            "sentence_count": len(prompt.split('.')),
            "average_sentence_length": self._avg_sentence_length(prompt),
            "complexity_level": self._determine_complexity(prompt)
        }
```

### 도메인별 특화 기능

```python
class DomainSpecificOptimizer:
    """도메인별 특화 최적화"""
    
    def optimize_for_healthcare(self, prompt: str) -> str:
        """의료 도메인 특화 최적화"""
        optimized = prompt
        
        # 의료 윤리 고려사항 추가
        if "diagnosis" in prompt:
            optimized += "\n\nIMPORTANT: This is for informational purposes only and does not constitute medical advice."
        
        # HIPAA 준수 사항 추가
        optimized += "\n\nEnsure all responses comply with patient privacy regulations."
        
        return optimized
    
    def optimize_for_legal(self, prompt: str) -> str:
        """법률 도메인 특화 최적화"""
        optimized = prompt
        
        # 법률 면책조항 추가
        optimized += "\n\nDISCLAIMER: This does not constitute legal advice. Consult with qualified legal professionals."
        
        return optimized
```

---

## 🔧 트러블슈팅

### 일반적인 문제들

#### 1. MCP 서버가 시작되지 않음

**증상:**
```
Error: Failed to connect to MCP server
```

**해결책:**
```bash
# 1. Python 경로 확인
which python

# 2. 의존성 설치 확인
pip install -r requirements-mcp.txt

# 3. 스크립트 실행 권한 확인
chmod +x mcp_server.py

# 4. 환경 변수 확인
echo $OPENAI_API_KEY
```

#### 2. 도구가 Claude Desktop에서 보이지 않음

**증상:**
도구 목록에 prompt-optimizer 관련 도구들이 나타나지 않음

**해결책:**
```json
// claude_desktop_config.json 설정 확인
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "python3",  // python3로 변경 시도
      "args": ["/full/absolute/path/to/mcp_server.py"],  // 절대 경로 사용
      "cwd": "/full/absolute/path/to/project",
      "env": {
        "PYTHONPATH": "/full/absolute/path/to/project",
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### 3. 프롬프트 최적화 실행 중 오류

**증상:**
```
Error: OpenAI API call failed
```

**해결책:**
```bash
# 1. API 키 확인
echo $OPENAI_API_KEY

# 2. API 키 권한 확인 (OpenAI 대시보드에서)

# 3. 네트워크 연결 확인
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# 4. 요청 제한 확인 (Rate limiting)
```

#### 4. 메모리 부족 오류

**증상:**
```
MemoryError: Unable to allocate memory
```

**해결책:**
```python
# 큰 프롬프트 처리를 위한 청크 분할
def split_large_prompt(prompt: str, max_size: int = 4000) -> List[str]:
    """큰 프롬프트를 청크로 분할"""
    chunks = []
    for i in range(0, len(prompt), max_size):
        chunks.append(prompt[i:i + max_size])
    return chunks

async def process_large_prompt(prompt: str) -> str:
    """큰 프롬프트 처리"""
    if len(prompt) > 4000:
        chunks = split_large_prompt(prompt)
        results = []
        
        for chunk in chunks:
            result = await optimize_prompt_comprehensive(chunk)
            results.append(result)
        
        return merge_optimization_results(results)
    else:
        return await optimize_prompt_comprehensive(prompt)
```

### 로깅 및 디버깅

#### 1. 상세 로깅 활성화

```python
# mcp_server.py에 추가
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("prompt-optimizer-mcp")

# 각 도구 호출 시 로깅
logger.info(f"Tool called: {name} with arguments: {arguments}")
```

#### 2. 성능 모니터링

```python
import time
from functools import wraps

def monitor_performance(func):
    """성능 모니터링 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    
    return wrapper

# 사용 예시
@monitor_performance
async def _handle_optimize_prompt(self, arguments: dict):
    # 기존 로직
    pass
```

#### 3. 오류 추적

```python
import traceback

async def handle_call_tool(name: str, arguments: dict):
    try:
        # 도구 실행 로직
        return await self._execute_tool(name, arguments)
    except Exception as e:
        # 상세한 오류 정보 로깅
        logger.error(f"Tool execution failed: {name}")
        logger.error(f"Arguments: {arguments}")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return [
            TextContent(
                type="text",
                text=f"도구 실행 중 오류가 발생했습니다: {str(e)}"
            )
        ]
```

---

## 📚 추가 리소스

### 공식 문서
- [MCP 공식 문서](https://modelcontextprotocol.io)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Claude Desktop MCP 가이드](https://docs.anthropic.com/claude/desktop/mcp)

### 예제 프로젝트
- [MCP 서버 예제](https://github.com/modelcontextprotocol/servers)
- [커뮤니티 MCP 도구](https://github.com/topics/model-context-protocol)

### 도움이 되는 도구들
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector): MCP 서버 디버깅
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk): Python MCP 개발 도구

---

**이제 프롬프트 최적화 기능을 MCP를 통해 다양한 AI 프로젝트에서 활용할 수 있습니다! 🚀** 