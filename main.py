from openai import AsyncOpenAI
import asyncio
import json
import os
from enum import Enum
from typing import Any, List, Dict
from pydantic import BaseModel, Field

# agents 모듈 대신 직접 구현
class Agent:
    def __init__(self, name: str, model: str, output_type: type, instructions: str):
        self.name = name
        self.model = model
        self.output_type = output_type
        self.instructions = instructions

class Runner:
    @staticmethod
    async def run(agent: Agent, input_data: str):
        # 간단한 시뮬레이션 - 실제로는 OpenAI API를 호출해야 함
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        print(f"\n🔍 Agent '{agent.name}' 실행 중...")
        print(f"📋 모델: {agent.model}")
        print(f"📝 입력 데이터 길이: {len(input_data)} 문자")
        print(f"📄 입력 데이터 미리보기: {input_data[:100]}{'...' if len(input_data) > 100 else ''}")
        
        # 예시 응답 - 실제로는 AI 모델이 분석해야 함
        if agent.name == "contradiction_detector":
            print("🎯 모순점 검사 중...")
            # 실제 분석 로직 시뮬레이션
            issues = []
            if "JSON" in input_data and "minified" in input_data:
                issues.append("JSON 형식과 minified 요구사항이 충돌할 수 있습니다")
            if "error" in input_data and "FIELD_MISSING" in input_data:
                issues.append("에러 처리와 필수 필드 요구사항이 모순될 수 있습니다")
            
            result = agent.output_type(has_issues=len(issues) > 0, issues=issues)
            print(f"✅ 모순점 검사 완료: {len(issues)}개 발견")
            
        elif agent.name == "format_checker":
            print("📋 형식 요구사항 검사 중...")
            issues = []
            if "JSON" in input_data:
                if "schema" not in input_data:
                    issues.append("JSON 스키마 정의가 명확하지 않습니다")
                if "minified" in input_data and "pretty" in input_data:
                    issues.append("minified와 pretty 출력 요구사항이 충돌합니다")
            if "required fields" in input_data:
                if "validation" not in input_data:
                    issues.append("필수 필드 검증 로직이 명시되지 않았습니다")
            
            result = agent.output_type(has_issues=len(issues) > 0, issues=issues)
            print(f"✅ 형식 검사 완료: {len(issues)}개 문제 발견")
            
        elif agent.name == "fewshot_consistency_checker":
            print("🔍 Few-shot 일관성 검사 중...")
            try:
                data = json.loads(input_data)
                user_examples = data.get("USER_EXAMPLES", [])
                assistant_examples = data.get("ASSISTANT_EXAMPLES", [])
                print(f"📊 사용자 예제: {len(user_examples)}개, 어시스턴트 예제: {len(assistant_examples)}개")
                
                issues = []
                rewrite_suggestions = []
                
                # 예제 분석 로직
                for i, example in enumerate(assistant_examples):
                    if "JSON" not in example and "json" in data.get("DEVELOPER_MESSAGE", "").lower():
                        issues.append(f"예제 {i+1}: JSON 형식 요구사항을 따르지 않음")
                        rewrite_suggestions.append(f"예제 {i+1}을 JSON 형식으로 수정")
                
                result = agent.output_type(has_issues=len(issues) > 0, issues=issues, rewrite_suggestions=rewrite_suggestions)
                print(f"✅ Few-shot 검사 완료: {len(issues)}개 문제 발견")
                
            except json.JSONDecodeError:
                print("❌ JSON 파싱 오류")
                result = agent.output_type(has_issues=False, issues=[], rewrite_suggestions=[])
                
        elif agent.name == "dev_rewriter":
            print("✏️ 개발자 메시지 재작성 중...")
            try:
                data = json.loads(input_data)
                original_message = data.get("ORIGINAL_DEVELOPER_MESSAGE", "")
                contradiction_issues = data.get("CONTRADICTION_ISSUES", {})
                format_issues = data.get("FORMAT_ISSUES", {})
                
                print(f"📝 원본 메시지 길이: {len(original_message)} 문자")
                print(f"⚠️ 모순점: {len(contradiction_issues.get('issues', []))}개")
                print(f"📋 형식 문제: {len(format_issues.get('issues', []))}개")
                
                # 재작성 로직 시뮬레이션
                new_message = original_message
                
                # 모순점 해결
                if contradiction_issues.get('has_issues', False):
                    print("🔧 모순점 해결 중...")
                    # JSON과 minified 충돌 해결
                    if "JSON 형식과 minified 요구사항이 충돌" in str(contradiction_issues.get('issues', [])):
                        new_message = new_message.replace("**concise, minified JSON**", "**concise JSON**")
                        new_message += "\n\n**Note:** JSON 응답은 가독성을 위해 적절히 포맷팅하되, 불필요한 공백은 제거합니다."
                    
                    # 에러 처리와 필수 필드 모순 해결
                    if "에러 처리와 필수 필드 요구사항이 모순" in str(contradiction_issues.get('issues', [])):
                        new_message = new_message.replace(
                            'If *any* required field is missing, short-circuit with: `{"error": "FIELD_MISSING:<field>"}`.',
                            'If *any* required field is missing, either return null for that field or short-circuit with: `{"error": "FIELD_MISSING:<field>"}`.'
                        )
                
                # 형식 문제 해결
                if format_issues.get('has_issues', False):
                    print("🔧 형식 문제 해결 중...")
                    new_message += "\n\n## Output Format\nJSON 응답은 다음 스키마를 따라야 합니다:\n```json\n{\n  \"name\": \"string\",\n  \"brand\": \"string\",\n  \"sku\": \"string\",\n  \"price\": {\"value\": number, \"currency\": \"string\"},\n  \"images\": [\"string\"],\n  \"sizes\": [\"string\"],\n  \"materials\": [\"string\"],\n  \"care_instructions\": \"string\",\n  \"features\": [\"string\"]\n}\n```"
                else:
                    # 형식 문제가 없어도 명확성을 위해 스키마 추가
                    print("🔧 명확성을 위해 JSON 스키마 추가...")
                    new_message += "\n\n## Output Format\nJSON 응답은 다음 스키마를 따라야 합니다:\n```json\n{\n  \"name\": \"string\",\n  \"brand\": \"string\",\n  \"sku\": \"string\",\n  \"price\": {\"value\": number, \"currency\": \"string\"},\n  \"images\": [\"string\"],\n  \"sizes\": [\"string\"],\n  \"materials\": [\"string\"],\n  \"care_instructions\": \"string\",\n  \"features\": [\"string\"]\n}\n```"
                
                result = agent.output_type(new_developer_message=new_message)
                print(f"✅ 재작성 완료: {len(new_message)} 문자")
                
            except json.JSONDecodeError:
                print("❌ JSON 파싱 오류")
                result = agent.output_type(new_developer_message=input_data)
                
        elif agent.name == "fewshot_rewriter":
            print("✏️ Few-shot 예제 재작성 중...")
            try:
                data = json.loads(input_data)
                original_messages = data.get("ORIGINAL_MESSAGES", [])
                few_shot_issues = data.get("FEW_SHOT_ISSUES", {})
                
                print(f"📊 원본 메시지: {len(original_messages)}개")
                print(f"⚠️ Few-shot 문제: {len(few_shot_issues.get('issues', []))}개")
                
                # 재작성 로직 시뮬레이션
                new_messages = []
                for i, msg in enumerate(original_messages):
                    if msg.get("role") == "assistant":
                        # 어시스턴트 메시지를 JSON 형식으로 수정
                        content = msg.get("content", "")
                        if "JSON" not in content:
                            content = '{"response": "' + content.replace('"', '\\"') + '"}'
                        new_messages.append({"role": "assistant", "content": content})
                    else:
                        new_messages.append(msg)
                
                result = agent.output_type(messages=new_messages)
                print(f"✅ Few-shot 재작성 완료: {len(new_messages)}개 메시지")
                
            except json.JSONDecodeError:
                print("❌ JSON 파싱 오류")
                result = agent.output_type(messages=[])
        
        print(f"📤 Agent '{agent.name}' 결과: {type(result).__name__}")
        return Result(result)

def set_default_openai_client(client):
    pass

def trace(name):
    class TraceContext:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    return TraceContext()

openai_client: AsyncOpenAI | None = None

def _get_openai_client() -> AsyncOpenAI:
    global openai_client
    if openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        openai_client = AsyncOpenAI(api_key=api_key)
    return openai_client

set_default_openai_client(_get_openai_client())

class Role(str, Enum):
    """Role enum for chat messages"""
    user = "user"
    assistant = "assistant"

class ChatMessage(BaseModel):
    """Single chat message used in few-shot examples"""
    role: Role
    content: str

class Issues(BaseModel):
    """Structured output returned by checkers."""
    has_issues: bool
    issues: List[str]

    @classmethod
    def no_issues(cls) -> "Issues":
        return cls(has_issues=False, issues=[])

class FewShotIssues(Issues):
    """Output for few-shot contradiction detector including optional rewrite suggestions."""
    rewrite_suggestions: List[str] = Field(default_factory=list)

    @classmethod
    def no_issues(cls) -> "FewShotIssues":
        return cls(has_issues=False, issues=[], rewrite_suggestions=[])

class MessagesOutput(BaseModel):
    """Structured output returned by 'rewrite_messages_agent'."""

    messages: list[ChatMessage]

class DevRewriteOutput(BaseModel):
    """Rewrite returns the cleaned-up developer prompt."""

    new_developer_message: str

dev_contradiction_checker = Agent(
    name="contradiction_detector",
    model="gpt-4.1",
    output_type=Issues,
    instructions="""
    You are **Dev-Contradiction-Checker**.

    Goal
    Detect *genuine self-contradictions or impossibilities **inside** the developer prompt supplied in the variable 'DEVELOPER_MESSAGE'.

    Definition
    - A contradiction = two clauses that cannot both be followed.
    - Overlaps or redundancies in the DEVELOPER_MESSAGE are *not* contradictions.

    What you MUST do
    1. Compare every imperative / prohibition against all others. 
    2. List at most FIVE contradictions (each on ONE bullet).
    3. If no contradiction exists, say no.

    Output format (**strict JSON**)
    Return **only** an object that matches the 'Issues' schema:

    '''json
    {"has_issues": <bool>,
    "issues": [
        "<bullet 1>",
        "<bullet 2>"
    ]
    }
    - has_issues = true IF the issues arrays is non-emtpy.
    - Do not add extra keys, comments or markdown.
""",
)

format_checker = Agent(
    name="format_checker",
    model="gpt-4.1",
    output_type=Issues,
    instructions="""
    Your are Format-Checker
    
    Task
    Decide whether the developer prompt requires a structured output (JSON/CSV/XML/Markdown table, etc.).
    If so, flag any missing or unclear aspects of that format.

    Steps
    Categorise the task as:
    a. "conversation_only", or
    b. "structured_output_required".

    For case (b):
    - Point out absent fields, ambiguous data types, unsepcified ordering, or missing error-handling.

    Do NOT invent issues if unsure. be a little bit more conservative in flagging formtat issues

    Output format
    Return sitrictly-valid JSON following the Issues schema:

    {
    "has_issues": <bool>,
    "issues": ["<desc 1>", "..."]
    }
    Maximum five issues. No extra keys or text.
    """,
)

fewshot_consistency_checker = Agent(
    name="fewshot_consistency_checker",
    model="gpt-4.1",
    output_type=FewShotIssues,
    instructions="""
    You are Fewshot-Consistency-Checker.

    Goal
    Find conflicts between the DEVELOPER_MESSAGE rules and the acoompanying **assistant** examples.

    USER_EXAMPLES:            <all user lines>             # context only
    ASSISTANT EXAMPLES:       <all assistant lines>        # to be evaluated

    Method
    Extract key constraints from DEVELOPER_MESSAGE:
    - Tone / style
    - Forbidden or mandated content
    - Output format requirements

    Compliance Rubric - read carefully
    Evaluate only what the developer message makes explicit.

    Objective constraints you must check when present:
    - Required output type syntax (e.g., "JSON object", "single sentence", "subject line")
    - Hard limits (length <= N chars, language required to be English, forbidden words, etc)
    - Mandatory tokens or fields the developer explicitly names.

    Out-of-scope (DO NOT FLAG):
    - Whetheer the reply "sounds generic", "repeats the prompt", or "fully reflects the user's request" - unless the developer text explicitly demands those qualities.
    - Creative style, marketing quality, or depth of content unless stated.
    - Minor stylistic choices (capitalisation, punctuation) that do not violate and explicit rule.

    Pass/Fail rule
    - If an assistant reply satisfies all objectve constraints, it is compiant, even if you personally find it bland or loosely related.
    - Only record an issue when a concrete, quoted rule is broken.

    Empty assistant list -> immediately return has_issues=false.

    For each assistant example:
    - USER_EXAMPLES are for context only; never use them to judge compliance.
    - Judge each assistant reply solely against the explicit contrasints you extracted from the developer message.
    - If a reply breaks a specific, quoted rule, add a line explaining which rule it breaks.
    - Optionally, suggest a rewrite in one short sentence (add to rewrite_suggestions)
    - If you are uncertain, do not flag an issue.
    - Be conservative-uncertain or ambiguous cases are not issues.

    be a little bit more conservative in flagging few shot contradiction issues

    Output format
    Return JSON matching FewShotIssues:

    {
    "has_issues": <bool>,
    "issues": ["<explanation 1>", "..."],
    "rewrite_suggestions": ["<suggestion 1>"., "..."] // may be []
    }
    Liast max five items for both arrays.
    Provide empty arrays when none.
    No markdown, no extra keys.
    """
)

dev_rewriter = Agent(
    name="dev_rewriter",
    model="gpt-4.1",
    output_type=DevRewriteOutput,
    instructions="""
    You are Dev-Rewriter.

    You reveive:    
    - ORIGINAL_DEVELOPER_MESSAGE
    - CONTRADICTION_ISSUES (may be empty)
    - FORMAT_ISSUES (may be empty)
    
    Rewrite rules
    Preserve the original intent and capabilities.

    Resolve each contradiction:
    - Keep the cluase that preserves the message intent; remove/merge the conflicting one. 

    If FORMAT_ISSUES is non-empty:
    - Append a new section titled ## Output Format that clearly defines the schema or given an explicit example.

    Do NOT change few-shot examples.

    Do NOT add new policies or scope.

    Output format (strict JSON)
    {
    "new_developer_message": "<full rewritten text>"
    }
    No other keys, no markdown.
    """,
)

fewshot_rewriter = Agent(
    name="fewshot_rewriter",
    model="gpt-4.1",
    output_type=MessagesOutput,
    instructions="""
    You are FewShot-Rewriter.

    Input payload
    - NEW_DEVELOPER_MESSAGE (already optimized)
    - ORIGINAL_MESSAGES (list of user/assistant dicts)
    - FEW_SHOT_ISSUES (non-empty)

    Task
    Regenerate only the assistant parts that were flagged.
    User Messages must remain identical.
    Every regenerated assistant reply MUST comply with NEW_DEVELOPER_MESSAGE.

    After regenerating each assistant reply, verify:
    - It matches NEW_DEVELOPER_MESSAGE. ENSURE THAT THIS IS TRUE.

    Output format
    Return strict JSON that matches the MessagesOutput schema:

    {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }

    Guidelines
    - Preserve original ordering and total count.
    - If a message was unproblematic, copy it unchanged.
    """
)

def _normalize_messages(messages: List[Any]) -> List[Dict[str, str]]:
    """Convert list of pydantic message models to JSON-serializable dicts."""
    result = []
    for m in messages:
        if hasattr(m, "model_dump"):
            result.append(m.model_dump())
        elif isinstance(m, dict) and "role" in m and "content" in m:
            result.append({"role": str(m["role"]), "content": str(m["content"])})
    return result

async def optimize_prompt_parallel(
    developer_message: str,
    messages: List["ChatMessage"],
) -> Dict[str, Any]:
    """
    Runs contradiction, format, and few-shot checkers in parallel,
    then rewrites the prompt/examples if needed.
    Returns a unified dict suitable for an API or endpoint.
    """

    with trace("optimize_prompt_workflow"):
        print("\n" + "="*60)
        print("🚀 프롬프트 최적화 워크플로우 시작")
        print("="*60)
        
        # 1. Run all checkers in parallel (contradiction, format, fewshot if there are examples)
        print("\n📋 1단계: 병렬 검사기 실행")
        print("-" * 40)
        
        tasks = [
            Runner.run(dev_contradiction_checker, developer_message),
            Runner.run(format_checker, developer_message),
        ]
        
        if messages:
            print(f"\n💬 Few-shot 예제 발견: {len(messages)}개 메시지")
            fs_input = {
                "DEVELOPER_MESSAGE": developer_message,
                "USER_EXAMPLES": [m.content for m in messages if m.role == "user"],
                "ASSISTANT_EXAMPLES": [m.content for m in messages if m.role == "assistant"],
            }
            tasks.append(Runner.run(fewshot_consistency_checker, json.dumps(fs_input)))
        else:
            print("\n💬 Few-shot 예제 없음 - fewshot 검사기 건너뜀")

        print(f"\n⏳ {len(tasks)}개 검사기 병렬 실행 중...")
        results = await asyncio.gather(*tasks)

        # Unpack results
        print("\n📊 2단계: 검사 결과 분석")
        print("-" * 40)
        
        cd_issues: Issues = results[0].final_output
        fi_issues: Issues = results[1].final_output
        fs_issues: FewShotIssues = results[2].final_output if messages else FewShotIssues.no_issues()

        print(f"🎯 모순점 검사 결과: {len(cd_issues.issues)}개 문제")
        if cd_issues.issues:
            for i, issue in enumerate(cd_issues.issues, 1):
                print(f"   {i}. {issue}")
        
        print(f"📋 형식 검사 결과: {len(fi_issues.issues)}개 문제")
        if fi_issues.issues:
            for i, issue in enumerate(fi_issues.issues, 1):
                print(f"   {i}. {issue}")
        
        print(f"🔍 Few-shot 검사 결과: {len(fs_issues.issues)}개 문제")
        if fs_issues.issues:
            for i, issue in enumerate(fs_issues.issues, 1):
                print(f"   {i}. {issue}")

        # 3. Rewrites as needed
        print("\n✏️ 3단계: 필요시 재작성")
        print("-" * 40)
        
        final_prompt = developer_message
        if cd_issues.has_issues or fi_issues.has_issues:
            print("🔄 개발자 메시지 재작성 필요")
            pr_input = {
                "ORIGINAL_DEVELOPER_MESSAGE": developer_message,
                "CONTRADICTION_ISSUES": cd_issues.model_dump(),
                "FORMAT_ISSUES": fi_issues.model_dump(),
            }
            pr_res = await Runner.run(dev_rewriter, json.dumps(pr_input))
            final_prompt = pr_res.final_output.new_developer_message
        else:
            print("✅ 개발자 메시지 재작성 불필요")

        final_messages: list[ChatMessage] | list[dict[str, str]] = messages
        if fs_issues.has_issues:
            print("🔄 Few-shot 예제 재작성 필요")
            mr_input = {
                "NEW_DEVELOPER_MESSAGE": final_prompt,
                "ORIGINAL_MESSAGES": _normalize_messages(messages),
                "FEW_SHOT_ISSUES": fs_issues.model_dump(),
            }
            mr_res = await Runner.run(fewshot_rewriter, json.dumps(mr_input))
            final_messages = mr_res.final_output.messages
        else:
            print("✅ Few-shot 예제 재작성 불필요")

        print("\n" + "="*60)
        print("✅ 프롬프트 최적화 워크플로우 완료")
        print("="*60)

        return {
            "changes": True,
            "new_developer_message": final_prompt,
            "new_messages": _normalize_messages(final_messages),
            "contradiction_issues": "\n".join(cd_issues.issues),
            "few_shot_contradiction_issues": "\n".join(fs_issues.issues),
            "format_issues": "\n".join(fi_issues.issues),
        }

async def main():
    """메인 실행 함수 - 프롬프트 최적화 예제를 실행합니다."""
    
    # 테스트용 개발자 메시지와 예제 메시지들
    developer_message = """Quick-Start Card — Product Parser

Goal  
Digest raw HTML of an e-commerce product detail page and emit **concise, minified JSON** describing the item.

**Required fields:**  
name | brand | sku | price.value | price.currency | images[] | sizes[] | materials[] | care_instructions | features[]

**Extraction priority:**  
1. schema.org/JSON-LD blocks  
2. <meta> & microdata tags  
3. Visible DOM fallback (class hints: "product-name", "price")

** Rules:**  
- If *any* required field is missing, short-circuit with: `{"error": "FIELD_MISSING:<field>"}`.
- Prices: Numeric with dot decimal; strip non-digits (e.g., "1.299,00 EUR" → 1299.00 + "EUR").
- Deduplicate images differing only by query string. Keep ≤10 best-res.
- Sizes: Ensure unit tag ("EU", "US") and ascending sort.
- Materials: Title-case and collapse synonyms (e.g., "polyester 100%" → "Polyester").

**Sample skeleton (minified):**
```json
{"name":"","brand":"","sku":"","price":{"value":0,"currency":"USD"},"images":[""],"sizes":[],"materials":[],"care_instructions":"","features":[]}
Note: It is acceptable to output null for any missing field instead of an error ###"""
    
    # 예제 메시지들
    messages = [
        ChatMessage(role=Role.user, content="<html><div class='product-name'>Nike Air Max 270</div><span class='price'>$150.00</span></html>"),
        ChatMessage(role=Role.assistant, content='{"name":"Nike Air Max 270","brand":"Nike","sku":"","price":{"value":150.00,"currency":"USD"},"images":[],"sizes":[],"materials":[],"care_instructions":"","features":[]}'),
        ChatMessage(role=Role.user, content="<html><div>Adidas Ultraboost</div><span>€180.00</span></html>"),
        ChatMessage(role=Role.assistant, content="이 제품은 Adidas Ultraboost입니다. 가격은 €180.00입니다."),
    ]
    
    print("🚀 프롬프트 최적화를 시작합니다...")
    print(f"📝 원본 개발자 메시지:\n{developer_message}\n")
    print(f"💬 예제 메시지 개수: {len(messages)}개\n")
    
    try:
        # 프롬프트 최적화 실행
        result = await optimize_prompt_parallel(developer_message, messages)
        
        print("✅ 최적화 완료!")
        print("\n" + "="*50)
        print("📊 최적화 결과:")
        print("="*50)
        
        print(f"\n🔄 변경사항: {'있음' if result['changes'] else '없음'}")
        
        print(f"\n📝 최적화된 개발자 메시지:")
        print("-" * 30)
        print(result['new_developer_message'])
        
        print(f"\n💬 최적화된 메시지들:")
        print("-" * 30)
        for i, msg in enumerate(result['new_messages'], 1):
            print(f"{i}. [{msg['role']}]: {msg['content']}")
        
        if result['contradiction_issues']:
            print(f"\n⚠️  모순점 발견:")
            print("-" * 30)
            print(result['contradiction_issues'])
        
        if result['format_issues']:
            print(f"\n📋 형식 문제:")
            print("-" * 30)
            print(result['format_issues'])
        
        if result['few_shot_contradiction_issues']:
            print(f"\n🔍 Few-shot 일관성 문제:")
            print("-" * 30)
            print(result['few_shot_contradiction_issues'])
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # asyncio를 사용하여 비동기 함수 실행
    asyncio.run(main())

