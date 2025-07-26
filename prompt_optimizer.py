from openai import AsyncOpenAI
import asyncio
import json
import os
from enum import Enum
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field
import streamlit as st
import re

# 기본 모델 정의
class Role(str, Enum):
    """Role enum for chat messages"""
    user = "user"
    assistant = "assistant"
    system = "system"

class ChatMessage(BaseModel):
    """Single chat message used in few-shot examples"""
    role: Role
    content: str

class Issues(BaseModel):
    """Structured output returned by checkers."""
    has_issues: bool
    issues: List[str]
    severity: str = "medium"  # low, medium, high
    category: str = "general"  # general, clarity, specificity, instruction_following, etc.

    @classmethod
    def no_issues(cls) -> "Issues":
        return cls(has_issues=False, issues=[], severity="low", category="general")

class PromptAnalysis(BaseModel):
    """프롬프트 분석 결과"""
    clarity_score: float  # 0-10
    specificity_score: float  # 0-10
    instruction_following_score: float  # 0-10
    overall_score: float  # 0-10
    recommendations: List[str]
    strengths: List[str]
    weaknesses: List[str]

class OptimizedPrompt(BaseModel):
    """최적화된 프롬프트 결과"""
    original_prompt: str
    optimized_prompt: str
    changes_made: List[str]
    improvement_explanation: str
    estimated_improvement: float  # percentage

class UserFeedback(BaseModel):
    """사용자 피드백"""
    feedback_text: str
    feedback_type: str = "general"  # general, specific_issue, improvement_request
    priority: str = "medium"  # low, medium, high
    category: str = "general"  # clarity, specificity, instruction_following, agentic_capabilities, format, other

class FeedbackAnalysis(BaseModel):
    """피드백 분석 결과"""
    understood_feedback: str
    feedback_category: str
    required_changes: List[str]
    revision_strategy: str
    estimated_impact: float  # 0-10

class RevisedPrompt(BaseModel):
    """피드백 기반 수정된 프롬프트"""
    original_optimized_prompt: str
    user_feedback: str
    revised_prompt: str
    changes_made: List[str]
    feedback_addressed: List[str]
    improvement_explanation: str

class GeneralResponse(BaseModel):
    """범용 Agent 응답"""
    original_prompt: str
    modified_prompt: str
    changes_made: List[str]
    explanation: str
    feedback_addressed: str

# 새로운 모델 추가
class PromptTypeDetection(BaseModel):
    """프롬프트 유형 감지 결과"""
    detected_type: str  # creative_writing, code_generation, qa, analysis, instruction_following, etc.
    confidence: float  # 0-1
    type_characteristics: List[str]
    optimization_strategy: str
    relevant_checkers: List[str]  # 해당 유형에 적합한 체커들

class PromptCandidateOutput(BaseModel):
    """프롬프트 후보 생성 결과"""
    prompt_candidates: List[str]

class PromptEvaluationScores(BaseModel):
    """개별 프롬프트 평가 점수"""
    prompt: str
    format_score: float
    contradiction_score: float
    relevance_score: float

class PerformanceRankingOutput(BaseModel):
    """성능 순위 결과"""
    ranked_prompts: List[Dict[str, Any]]  # [{"prompt": str, "final_score": float, "rank": int}]

class RelevanceEvaluationOutput(BaseModel):
    """관련성 평가 결과"""
    alignment_score: float  # 0.0 to 1.0
    evaluation_summary: str

class SafetyCheckOutput(BaseModel):
    """안전성 검사 결과"""
    is_safe: bool
    safety_flags: List[Dict[str, str]]  # [{"category": str, "details": str}]

# Agent 구현
class Agent:
    def __init__(self, name: str, model: str, output_type: type, instructions: str):
        self.name = name
        self.model = model
        self.output_type = output_type
        self.instructions = instructions

class Runner:
    @staticmethod
    def _get_json_schema(model_class):
        """Pydantic 모델의 JSON 스키마를 문자열로 반환"""
        if model_class == Issues:
            return '''{
  "has_issues": boolean,
  "issues": ["string"],
  "severity": "low|medium|high",
  "category": "string"
}'''
        elif model_class == OptimizedPrompt:
            return '''{
  "original_prompt": "string",
  "optimized_prompt": "string", 
  "changes_made": ["string"],
  "improvement_explanation": "string",
  "estimated_improvement": number
}'''
        elif model_class == FeedbackAnalysis:
            return '''{
  "understood_feedback": "string",
  "feedback_category": "string",
  "required_changes": ["string"],
  "revision_strategy": "string",
  "estimated_impact": number
}'''
        elif model_class == RevisedPrompt:
            return '''{
  "original_optimized_prompt": "string",
  "user_feedback": "string",
  "revised_prompt": "string",
  "changes_made": ["string"],
  "feedback_addressed": ["string"],
  "improvement_explanation": "string"
}'''
        elif model_class == GeneralResponse:
            return '''{
  "original_prompt": "string",
  "modified_prompt": "string",
  "changes_made": ["string"],
  "explanation": "string",
  "feedback_addressed": "string"
}'''
        elif model_class == PromptTypeDetection:
            return '''{
  "detected_type": "string",
  "confidence": number,
  "type_characteristics": ["string"],
  "optimization_strategy": "string",
  "relevant_checkers": ["string"]
}'''
        elif model_class == PromptCandidateOutput:
            return '''{
  "prompt_candidates": ["string"]
}'''
        elif model_class == PerformanceRankingOutput:
            return '''{
  "ranked_prompts": [
    {"prompt": "string", "final_score": number, "rank": number}
  ]
}'''
        elif model_class == RelevanceEvaluationOutput:
            return '''{
  "alignment_score": number,
  "evaluation_summary": "string"
}'''
        elif model_class == SafetyCheckOutput:
            return '''{
  "is_safe": boolean,
  "safety_flags": [
    {"category": "string", "details": "string"}
  ]
}'''
        else:
            return "{}"
    
    @staticmethod
    async def run(agent: Agent, input_data: str, progress_callback=None, api_key: str = None):
        if progress_callback:
            progress_callback(f"🔍 Agent '{agent.name}' 실행 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        # API 키가 없으면 시뮬레이션 모드
        if not api_key:
            return await Runner._run_simulation(agent, input_data, progress_callback)
        
        # 실제 OpenAI API 호출
        try:
            client = AsyncOpenAI(api_key=api_key)
            
            # Agent별 프롬프트 구성
            system_prompt = f"""You are an expert prompt optimizer specializing in {agent.name.replace('_', ' ')}.
            
            {agent.instructions}
            
            Analyze the following input and provide a structured response in JSON format.
            
            IMPORTANT: Return ONLY the JSON object that matches this exact structure:
            {Runner._get_json_schema(agent.output_type)}
            
            Do not include any additional text, explanations, or markdown formatting.
            """
            
            response = await client.chat.completions.create(
                model=agent.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_data}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            # JSON 응답 파싱 및 검증
            response_content = response.choices[0].message.content.strip()
            
            # JSON 파싱 시도
            try:
                result_data = json.loads(response_content)
            except json.JSONDecodeError as e:
                if progress_callback:
                    progress_callback(f"❌ {agent.name} JSON 파싱 오류: {str(e)}")
                # JSON 파싱 실패 시 시뮬레이션 모드로 폴백
                return await Runner._run_simulation(agent, input_data, progress_callback)
            
            # Pydantic 모델 검증 및 변환
            try:
                result = agent.output_type(**result_data)
            except Exception as e:
                if progress_callback:
                    progress_callback(f"❌ {agent.name} 모델 검증 오류: {str(e)}")
                # 모델 검증 실패 시 시뮬레이션 모드로 폴백
                return await Runner._run_simulation(agent, input_data, progress_callback)
            
            if progress_callback:
                progress_callback(f"✅ {agent.name} 완료")
            
            return Result(result)
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ {agent.name} 오류: {str(e)}")
            # 오류 시 시뮬레이션 모드로 폴백
            return await Runner._run_simulation(agent, input_data, progress_callback)
    
    @staticmethod
    async def _run_simulation(agent: Agent, input_data: str, progress_callback=None):
        """시뮬레이션 모드 - API 키가 없을 때 사용"""
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        # GPT-4.1 가이드 기반 분석 로직
        if agent.name == "clarity_checker":
            return await Runner._analyze_clarity(agent, input_data, progress_callback)
        elif agent.name == "specificity_checker":
            return await Runner._analyze_specificity(agent, input_data, progress_callback)
        elif agent.name == "instruction_following_checker":
            return await Runner._analyze_instruction_following(agent, input_data, progress_callback)
        elif agent.name == "agentic_capability_checker":
            return await Runner._analyze_agentic_capabilities(agent, input_data, progress_callback)
        elif agent.name == "prompt_optimizer":
            return await Runner._optimize_prompt(agent, input_data, progress_callback)
        elif agent.name == "few_shot_optimizer":
            return await Runner._optimize_few_shot(agent, input_data, progress_callback)
        elif agent.name == "feedback_analyzer":
            return await Runner._analyze_feedback(agent, input_data, progress_callback)
        elif agent.name == "prompt_reviser":
            return await Runner._revise_prompt_with_feedback(agent, input_data, progress_callback)
        elif agent.name == "general_agent":
            return await Runner._general_response(agent, input_data, progress_callback)
        
        return Result(agent.output_type.no_issues() if hasattr(agent.output_type, 'no_issues') else {})

    @staticmethod
    async def _analyze_clarity(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("📋 명확성 분석 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        issues = []
        
        # 명확성 체크 로직 (GPT-4.1 가이드 기반)
        if len(input_data.strip()) < 20:
            issues.append("프롬프트가 너무 짧아 명확한 지시사항을 제공하지 못합니다")
        
        if not any(keyword in input_data.lower() for keyword in ['you are', 'task', 'goal', 'objective']):
            issues.append("역할이나 목표가 명확하게 정의되지 않았습니다")
        
        if input_data.count('?') > 5:
            issues.append("너무 많은 질문이 포함되어 혼란을 야기할 수 있습니다")
        
        ambiguous_words = ['maybe', 'perhaps', 'might', 'could be', 'possibly']
        if any(word in input_data.lower() for word in ambiguous_words):
            issues.append("모호한 표현이 포함되어 있어 명확성을 해칩니다")
        
        result = agent.output_type(
            has_issues=len(issues) > 0,
            issues=issues,
            severity="high" if len(issues) > 2 else "medium" if len(issues) > 0 else "low",
            category="clarity"
        )
        
        if progress_callback:
            progress_callback(f"✅ 명확성 분석 완료: {len(issues)}개 문제 발견")
        
        return Result(result)

    @staticmethod
    async def _analyze_specificity(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("🎯 구체성 분석 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        issues = []
        
        # 구체성 체크 로직
        vague_instructions = ['do something', 'help me', 'make it better', 'improve']
        if any(instruction in input_data.lower() for instruction in vague_instructions):
            issues.append("지시사항이 너무 추상적입니다. 구체적인 행동을 명시해주세요")
        
        if not any(keyword in input_data.lower() for keyword in ['format', 'structure', 'example', 'template']):
            issues.append("출력 형식이나 구조에 대한 명시적 지침이 없습니다")
        
        if len(input_data.split()) < 50:
            issues.append("프롬프트가 너무 짧아 충분한 컨텍스트를 제공하지 못합니다")
        
        # GPT-4.1 가이드: 도구 사용 및 계획 유도 체크
        if 'tool' in input_data.lower() and 'plan' not in input_data.lower():
            issues.append("도구 사용이 언급되었지만 계획 수립에 대한 지침이 없습니다")
        
        result = agent.output_type(
            has_issues=len(issues) > 0,
            issues=issues,
            severity="medium" if len(issues) > 1 else "low",
            category="specificity"
        )
        
        if progress_callback:
            progress_callback(f"✅ 구체성 분석 완료: {len(issues)}개 문제 발견")
        
        return Result(result)

    @staticmethod
    async def _analyze_instruction_following(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("📏 지시사항 준수 분석 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        issues = []
        
        # GPT-4.1은 지시사항을 더 문자 그대로 따르므로 명확한 지시가 중요
        if not input_data.strip().endswith('.') and not input_data.strip().endswith('!'):
            issues.append("지시사항이 완전한 문장으로 끝나지 않아 모호할 수 있습니다")
        
        contradictory_words = [('always', 'never'), ('must', 'optional'), ('required', 'if needed')]
        for word1, word2 in contradictory_words:
            if word1 in input_data.lower() and word2 in input_data.lower():
                issues.append(f"'{word1}'과 '{word2}'와 같은 상충되는 지시사항이 포함되어 있습니다")
        
        # 우선순위 체크
        if 'important' in input_data.lower() and 'priority' not in input_data.lower():
            issues.append("중요도는 언급되었지만 우선순위가 명확하지 않습니다")
        
        result = agent.output_type(
            has_issues=len(issues) > 0,
            issues=issues,
            severity="high" if len(issues) > 2 else "medium",
            category="instruction_following"
        )
        
        if progress_callback:
            progress_callback(f"✅ 지시사항 준수 분석 완료: {len(issues)}개 문제 발견")
        
        return Result(result)

    @staticmethod
    async def _analyze_agentic_capabilities(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("🤖 에이전틱 능력 분석 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        issues = []
        
        # GPT-4.1 가이드의 3가지 핵심 요소 체크
        has_persistence = any(keyword in input_data.lower() for keyword in 
                            ['keep going', 'continue', 'persist', 'until complete', 'multi-step'])
        has_tool_guidance = any(keyword in input_data.lower() for keyword in 
                              ['tools', 'function', 'use available', 'do not guess'])
        has_planning = any(keyword in input_data.lower() for keyword in 
                         ['plan', 'step by step', 'think through', 'reflect'])
        
        if not has_persistence:
            issues.append("지속성(persistence) 지침이 없습니다. 멀티턴 작업에서 중요합니다")
        
        if not has_tool_guidance and 'tool' in input_data.lower():
            issues.append("도구 사용에 대한 명확한 지침이 없습니다")
        
        if not has_planning:
            issues.append("계획 수립 및 반성적 사고에 대한 지침이 없습니다")
        
        result = agent.output_type(
            has_issues=len(issues) > 0,
            issues=issues,
            severity="medium",
            category="agentic_capabilities"
        )
        
        if progress_callback:
            progress_callback(f"✅ 에이전틱 능력 분석 완료: {len(issues)}개 문제 발견")
        
        return Result(result)

    @staticmethod
    async def _optimize_prompt(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("✏️ 프롬프트 최적화 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        try:
            data = json.loads(input_data)
            original_prompt = data.get("original_prompt", "")
            all_issues = data.get("all_issues", [])
            
            # GPT-4.1 가이드 기반 최적화
            optimized_prompt = original_prompt
            changes_made = []
            
            # 1. 역할 명확화
            if not optimized_prompt.lower().startswith('you are'):
                optimized_prompt = "You are a helpful AI assistant. " + optimized_prompt
                changes_made.append("명확한 역할 정의 추가")
            
            # 2. GPT-4.1 에이전틱 구성 요소 추가
            agentic_components = []
            
            # Persistence 추가
            if not any(keyword in optimized_prompt.lower() for keyword in ['keep going', 'until complete']):
                agentic_components.append(
                    "Please keep going until the task is completely resolved, before ending your turn."
                )
                changes_made.append("지속성(persistence) 지침 추가")
            
            # Tool-calling guidance 추가 (필요시)
            if 'tool' in optimized_prompt.lower() and 'do not guess' not in optimized_prompt.lower():
                agentic_components.append(
                    "If you are not sure about information needed for the task, use available tools to gather relevant information - do NOT guess or make up an answer."
                )
                changes_made.append("도구 사용 지침 추가")
            
            # Planning guidance 추가
            if not any(keyword in optimized_prompt.lower() for keyword in ['plan', 'step by step']):
                agentic_components.append(
                    "Plan extensively before taking action, and reflect on the outcomes of your actions."
                )
                changes_made.append("계획 수립 지침 추가")
            
            # 3. 구체적 개선사항 적용
            for issue_set in all_issues:
                for issue in issue_set.get('issues', []):
                    if '너무 짧' in issue:
                        optimized_prompt += "\n\nPlease provide detailed, comprehensive responses with clear explanations."
                        changes_made.append("상세한 응답 요구사항 추가")
                    elif '모호한 표현' in issue:
                        optimized_prompt = optimized_prompt.replace('maybe', 'specifically')
                        optimized_prompt = optimized_prompt.replace('perhaps', 'exactly')
                        changes_made.append("모호한 표현 제거")

            # 마크다운 강조 복원 (큰 오류가 없을 때만)
            all_issues_flat = [i for issue_set in all_issues for i in issue_set.get('issues', [])]
            optimized_prompt = preserve_markdown_emphasis(original_prompt, optimized_prompt, all_issues_flat)

            # 에이전틱 구성 요소 추가
            if agentic_components:
                optimized_prompt += "\n\n" + "\n".join(agentic_components)

            # 4. 출력 형식 명시
            if 'format' not in optimized_prompt.lower():
                optimized_prompt += "\n\nProvide your response in a clear, structured format."
                changes_made.append("출력 형식 지침 추가")

            # 줄바꿈 보존: \n이 없으면 문장 끝마다 강제로 추가
            if '\n' not in optimized_prompt:
                optimized_prompt = re.sub(r'([.!?]) +', r'\1\n', optimized_prompt)

            result = OptimizedPrompt(
                original_prompt=original_prompt,
                optimized_prompt=optimized_prompt,
                changes_made=changes_made,
                improvement_explanation="GPT-4.1 가이드라인에 따라 명확성, 구체성, 에이전틱 능력을 개선했습니다.",
                estimated_improvement=min(len(changes_made) * 15, 80)  # 최대 80% 개선
            )
            
            if progress_callback:
                progress_callback(f"✅ 프롬프트 최적화 완료: {len(changes_made)}개 개선사항 적용")
            
            return Result(result)
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 최적화 중 오류 발생: {e}")
            return Result(OptimizedPrompt(
                original_prompt=input_data,
                optimized_prompt=input_data,
                changes_made=[],
                improvement_explanation="최적화 중 오류 발생",
                estimated_improvement=0
            ))

    @staticmethod
    async def _optimize_few_shot(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("📝 Few-shot 예제 최적화 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        try:
            data = json.loads(input_data)
            messages = data.get("messages", [])
            optimized_prompt = data.get("optimized_prompt", "")
            
            # Few-shot 예제 개선
            improved_messages = []
            
            for msg in messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    # 더 구체적이고 도움이 되는 응답으로 개선
                    if len(content) < 50:
                        content = f"Based on your request, here's a detailed response: {content}. Let me know if you need further clarification or have additional questions."
                    improved_messages.append({"role": "assistant", "content": content})
                else:
                    improved_messages.append(msg)
            
            if progress_callback:
                progress_callback(f"✅ Few-shot 최적화 완료: {len(improved_messages)}개 메시지")
            
            return Result({"messages": improved_messages})
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Few-shot 최적화 중 오류 발생: {e}")
            return Result({"messages": []})

    @staticmethod
    async def _analyze_feedback(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("📝 피드백 분석 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        try:
            data = json.loads(input_data)
            user_feedback = data.get("user_feedback", "")
            
            # 피드백 분석 로직
            understood_feedback = "피드백을 이해했습니다."
            feedback_category = "general"
            required_changes = []
            revision_strategy = "기존 프롬프트를 유지하고 피드백에 따라 개선합니다."
            estimated_impact = 0.0 # 0-10 점수

            # 간단한 분석 로직 (실제 분석은 더 복잡해질 수 있음)
            if "모호한 표현" in user_feedback:
                understood_feedback = "피드백을 이해했습니다. 모호한 표현을 제거하겠습니다."
                required_changes.append("모호한 표현 제거")
                revision_strategy = "모호한 표현을 제거하여 명확성을 높이겠습니다."
                estimated_impact = 0.8 # 높은 영향
            elif "너무 짧은 응답" in user_feedback:
                understood_feedback = "피드백을 이해했습니다. 더 구체적인 응답을 제공하겠습니다."
                required_changes.append("더 구체적인 응답 제공")
                revision_strategy = "더 구체적인 응답을 제공하여 명확성을 높이겠습니다."
                estimated_impact = 0.6 # 높은 영향
            elif "중요한 지시사항" in user_feedback:
                understood_feedback = "피드백을 이해했습니다. 중요한 지시사항에 대한 우선순위를 명확히 하겠습니다."
                required_changes.append("중요한 지시사항에 대한 우선순위 명확히 하기")
                revision_strategy = "중요한 지시사항에 대한 우선순위를 명확히 하여 명확성을 높이겠습니다."
                estimated_impact = 0.7 # 높은 영향
            elif "도구 사용" in user_feedback:
                understood_feedback = "피드백을 이해했습니다. 도구 사용에 대한 명확한 지침을 추가하겠습니다."
                required_changes.append("도구 사용에 대한 명확한 지침 추가")
                revision_strategy = "도구 사용에 대한 명확한 지침을 추가하여 에이전틱 능력을 개선하겠습니다."
                estimated_impact = 0.9 # 높은 영향
            elif "계획 수립" in user_feedback:
                understood_feedback = "피드백을 이해했습니다. 계획 수립 및 반성적 사고에 대한 지침을 추가하겠습니다."
                required_changes.append("계획 수립 및 반성적 사고에 대한 지침 추가")
                revision_strategy = "계획 수립 및 반성적 사고에 대한 지침을 추가하여 에이전틱 능력을 개선하겠습니다."
                estimated_impact = 0.8 # 높은 영향
            else:
                understood_feedback = "피드백을 이해했습니다. 피드백에 따라 프롬프트를 개선하겠습니다."
                required_changes = []
                revision_strategy = "피드백에 따라 프롬프트를 개선하겠습니다."
                estimated_impact = 0.5 # 중간 영향

            result = FeedbackAnalysis(
                understood_feedback=understood_feedback,
                feedback_category=feedback_category,
                required_changes=required_changes,
                revision_strategy=revision_strategy,
                estimated_impact=estimated_impact
            )
            
            if progress_callback:
                progress_callback(f"✅ 피드백 분석 완료: 이해도 {estimated_impact:.1f}/10")
            
            return Result(result)
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 피드백 분석 중 오류 발생: {e}")
            return Result(FeedbackAnalysis(
                understood_feedback="피드백 분석 중 오류 발생",
                feedback_category="error",
                required_changes=[],
                revision_strategy="피드백 분석 중 오류 발생",
                estimated_impact=0
            ))

    @staticmethod
    async def _revise_prompt_with_feedback(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback("✏️ 피드백 기반 프롬프트 수정 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        try:
            data = json.loads(input_data)
            original_optimized_prompt = data.get("original_optimized_prompt", "")
            user_feedback = data.get("user_feedback", "")
            
            # 피드백 기반 프롬프트 수정 로직
            revised_prompt = original_optimized_prompt
            changes_made = []
            feedback_addressed = []
            improvement_explanation = "피드백에 따라 프롬프트를 수정했습니다."

            # 모호한 표현 제거
            if "모호한 표현" in user_feedback:
                revised_prompt = revised_prompt.replace('maybe', 'specifically').replace('perhaps', 'exactly')
                changes_made.append("모호한 표현 제거")
                feedback_addressed.append("모호한 표현 제거")
                improvement_explanation += " 모호한 표현을 제거했습니다."

            # 너무 짧은 응답 개선
            if "너무 짧은 응답" in user_feedback:
                revised_prompt += "\n\nPlease provide detailed, comprehensive responses with clear explanations."
                changes_made.append("더 구체적인 응답 제공")
                feedback_addressed.append("너무 짧은 응답 개선")
                improvement_explanation += " 더 구체적인 응답을 제공했습니다."

            # 중요한 지시사항 강조
            if "중요한 지시사항" in user_feedback:
                revised_prompt += "\n\nPlease prioritize important instructions and ensure they are clear."
                changes_made.append("중요한 지시사항에 대한 우선순위 명확히 하기")
                feedback_addressed.append("중요한 지시사항 강조")
                improvement_explanation += " 중요한 지시사항에 대한 우선순위를 명확히 했습니다."

            # 도구 사용 지침 추가
            if "도구 사용" in user_feedback:
                revised_prompt += "\n\nIf you are not sure about information needed for the task, use available tools to gather relevant information - do NOT guess or make up an answer."
                changes_made.append("도구 사용에 대한 명확한 지침 추가")
                feedback_addressed.append("도구 사용 지침 추가")
                improvement_explanation += " 도구 사용에 대한 명확한 지침을 추가했습니다."

            # 계획 수립 지침 추가
            if "계획 수립" in user_feedback:
                revised_prompt += "\n\nPlan extensively before taking action, and reflect on the outcomes of your actions."
                changes_made.append("계획 수립 지침 추가")
                feedback_addressed.append("계획 수립 지침 추가")
                improvement_explanation += " 계획 수립 및 반성적 사고에 대한 지침을 추가했습니다."

            # 출력 형식 명시
            if 'format' not in revised_prompt.lower():
                revised_prompt += "\n\nProvide your response in a clear, structured format."
                changes_made.append("출력 형식 지침 추가")
                feedback_addressed.append("출력 형식 명시")
                improvement_explanation += " 출력 형식을 명시했습니다."

            result = RevisedPrompt(
                original_optimized_prompt=original_optimized_prompt,
                user_feedback=user_feedback,
                revised_prompt=revised_prompt,
                changes_made=changes_made,
                feedback_addressed=feedback_addressed,
                improvement_explanation=improvement_explanation
            )
            
            if progress_callback:
                progress_callback(f"✅ 피드백 기반 프롬프트 수정 완료: {len(changes_made)}개 개선사항 적용")
            
            return Result(result)
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 피드백 기반 프롬프트 수정 중 오류 발생: {e}")
            return Result(RevisedPrompt(
                original_optimized_prompt=input_data,
                user_feedback=input_data,
                revised_prompt=input_data,
                changes_made=[],
                feedback_addressed=[],
                improvement_explanation="피드백 기반 프롬프트 수정 중 오류 발생"
            ))

    @staticmethod
    async def _general_response(agent: Agent, input_data: str, progress_callback=None):
        """범용 agent 시뮬레이션"""
        if progress_callback:
            progress_callback("🤖 범용 요청 처리 중...")
        
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output
        
        try:
            data = json.loads(input_data)
            original_prompt = data.get("original_prompt", "")
            user_feedback = data.get("user_feedback", "")
            
            modified_prompt = original_prompt
            changes_made = []
            explanation = "사용자 요청에 따라 프롬프트를 수정했습니다."
            
            # 언어 변경 처리
            if "한글" in user_feedback or "korean" in user_feedback.lower():
                if "translate" in user_feedback.lower() or "변경" in user_feedback or "번역" in user_feedback:
                    # 영어 -> 한글 번역 시뮬레이션
                    if "You are" in original_prompt:
                        modified_prompt = original_prompt.replace("You are", "당신은")
                        modified_prompt = modified_prompt.replace("Please", "다음을")
                        modified_prompt = modified_prompt.replace("Provide", "제공하세요")
                        modified_prompt = modified_prompt.replace("Create", "생성하세요") 
                        modified_prompt = modified_prompt.replace("Analyze", "분석하세요")
                        modified_prompt = modified_prompt.replace("Write", "작성하세요")
                        changes_made.append("프롬프트를 한국어로 번역")
                        explanation = "프롬프트를 한국어로 번역했습니다."
            
            # 영어 변경 처리
            elif "english" in user_feedback.lower() or "영어" in user_feedback:
                if "translate" in user_feedback.lower() or "변경" in user_feedback or "번역" in user_feedback:
                    # 한글 -> 영어 번역 시뮬레이션
                    if "당신은" in original_prompt:
                        modified_prompt = original_prompt.replace("당신은", "You are")
                        modified_prompt = modified_prompt.replace("다음을", "Please")
                        modified_prompt = modified_prompt.replace("제공하세요", "provide")
                        modified_prompt = modified_prompt.replace("생성하세요", "create")
                        modified_prompt = modified_prompt.replace("분석하세요", "analyze")
                        modified_prompt = modified_prompt.replace("작성하세요", "write")
                        changes_made.append("프롬프트를 영어로 번역")
                        explanation = "프롬프트를 영어로 번역했습니다."
            
            # 문체 변경 처리
            elif "formal" in user_feedback.lower() or "정중" in user_feedback or "격식" in user_feedback:
                modified_prompt = f"Please {modified_prompt.lstrip('Please ')}"
                if not modified_prompt.endswith('.'):
                    modified_prompt += "."
                changes_made.append("정중한 문체로 변경")
                explanation = "프롬프트를 정중한 문체로 변경했습니다."
            
            elif "casual" in user_feedback.lower() or "친근" in user_feedback or "편한" in user_feedback:
                modified_prompt = modified_prompt.replace("Please ", "")
                modified_prompt = modified_prompt.replace("Kindly ", "")
                changes_made.append("친근한 문체로 변경")
                explanation = "프롬프트를 친근한 문체로 변경했습니다."
            
            # 길이 조정
            elif "shorter" in user_feedback.lower() or "짧게" in user_feedback or "간단" in user_feedback:
                sentences = modified_prompt.split('.')
                modified_prompt = '. '.join(sentences[:len(sentences)//2]) + '.'
                changes_made.append("프롬프트 길이 단축")
                explanation = "프롬프트를 더 간결하게 만들었습니다."
            
            elif "longer" in user_feedback.lower() or "길게" in user_feedback or "자세히" in user_feedback:
                modified_prompt += " Please provide detailed explanations and comprehensive responses."
                changes_made.append("프롬프트 길이 확장")
                explanation = "프롬프트에 더 자세한 설명을 추가했습니다."
            
            # 기본 처리
            if not changes_made:
                modified_prompt += f"\n\n[User Request: {user_feedback}]"
                changes_made.append("사용자 요청 사항 추가")
                explanation = f"사용자 요청 '{user_feedback}'을 프롬프트에 반영했습니다."
            
            result = GeneralResponse(
                original_prompt=original_prompt,
                modified_prompt=modified_prompt,
                changes_made=changes_made,
                explanation=explanation,
                feedback_addressed=user_feedback
            )
            
            if progress_callback:
                progress_callback(f"✅ 범용 요청 처리 완료: {len(changes_made)}개 변경사항 적용")
            
            return Result(result)
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 범용 요청 처리 중 오류 발생: {e}")
            return Result(GeneralResponse(
                original_prompt=input_data,
                modified_prompt=input_data,
                changes_made=[],
                explanation="범용 요청 처리 중 오류 발생",
                feedback_addressed=input_data
            ))

def preserve_markdown_emphasis(original: str, optimized: str, issues: list) -> str:
    """원본의 마크다운 강조(*, **)를 최적화 프롬프트에 복원 (큰 오류가 없을 때만)"""
    # checker에서 강조 부분이 문제라고 지적한 경우는 복원하지 않음
    issue_text = ' '.join(issues).lower() if issues else ''
    if any(x in issue_text for x in ['emphasis', 'bold', 'italic', 'star', 'asterisk', 'markdown', 'formatting']):
        return optimized
    
    # 마크다운 강조 패턴 추출
    patterns = [r'\*\*[^*]+\*\*', r'\*[^*]+\*', r'__[^_]+__', r'_[^_]+_']
    for pat in patterns:
        for match in re.findall(pat, original):
            # 강조된 텍스트에서 * 또는 _ 제거
            plain = match.strip('*_')
            # 최적화 프롬프트에 강조가 사라졌다면 복원
            if plain in optimized and match not in optimized:
                optimized = optimized.replace(plain, match)
    return optimized

def create_agents(model: str = "gpt-4o"):
    """모델을 기반으로 Agent 인스턴스들을 생성"""
    return {
        # OpenAI Cookbook 원본 checker들
        "dev_contradiction_checker": Agent(
            name="contradiction_detector",
            model=model,
            output_type=Issues,
            instructions="""
You are **Dev-Contradiction-Checker**.

Goal
Detect *genuine* self-contradictions or impossibilities **inside** the developer prompt supplied in the variable `DEVELOPER_MESSAGE`.

Definitions
• A contradiction = two clauses that cannot both be followed.
• Overlaps or redundancies in the DEVELOPER_MESSAGE are *not* contradictions.

What you MUST do
1. Compare every imperative / prohibition against all others.
2. List at most FIVE contradictions (each as ONE bullet).
3. If no contradiction exists, say so.

Output format (**strict JSON**)
Return **only** an object that matches the `Issues` schema:

```json
{"has_issues": <bool>,
"issues": [
    "<bullet 1>",
    "<bullet 2>"
]
}
- has_issues = true IFF the issues array is non-empty.
- Do not add extra keys, comments or markdown.
"""
        ),
        "format_checker": Agent(
            name="format_checker",
            model=model,
            output_type=Issues,
            instructions="""
You are Format-Checker.

Task
Decide whether the developer prompt requires a structured output (JSON/CSV/XML/Markdown table, etc.).
If so, flag any missing or unclear aspects of that format.

Steps
Categorise the task as:
a. "conversation_only", or
b. "structured_output_required".

For case (b):
- Point out absent fields, ambiguous data types, unspecified ordering, or missing error-handling.

Do NOT invent issues if unsure. be a little bit more conservative in flagging format issues

Output format
Return strictly-valid JSON following the Issues schema:

{
"has_issues": <bool>,
"issues": ["<desc 1>", "..."]
}
Maximum five issues. No extra keys or text.
"""
        ),
        # 새로운 에이전트들
        "prompt_type_detector": Agent(
            name="prompt_type_detector",
            model=model,
            output_type=PromptTypeDetection,
            instructions="""
You are Prompt-Type-Detector.
Your task is to analyze the given prompt and determine its type and characteristics.

Analyze the prompt for:
1. Primary purpose (creative_writing, code_generation, qa, analysis, instruction_following, etc.)
2. Key characteristics that define this type
3. Appropriate optimization strategy for this type
4. Which checkers would be most relevant

Be specific and confident in your assessment.
"""
        ),
        "prompt_candidate_generator": Agent(
            name="prompt_candidate_generator",
            model=model,
            output_type=PromptCandidateOutput,
            instructions="""
You are Prompt-Candidate-Generator.
You receive:
- BASE_PROMPT_IDEA (a string with the core user request)
- NUM_CANDIDATES (an integer for how many variations to create)

Your task is to generate diverse variations of the BASE_PROMPT_IDEA.

Generation rules:
- Rephrase the core request using different wording.
- Change the prompt structure (e.g., from question to instruction).
- Add or modify constraints and personas.
- Preserve the original intent of the base idea.

Output format (strict JSON)
{
  "prompt_candidates": ["<full text of candidate 1>", "<full text of candidate 2>"]
}
No other keys, no markdown.
"""
        ),
        "performance_ranker_selector": Agent(
            name="performance_ranker_selector",
            model=model,
            output_type=PerformanceRankingOutput,
            instructions="""
You are Performance-Ranker-and-Selector.
You receive:
- CANDIDATE_EVALUATIONS: A list of objects, where each object contains a prompt candidate and its evaluation scores.
  Example item: {"prompt": "...", "format_score": 1.0, "contradiction_score": 0.9, "relevance_score": 0.7}

Your task is to aggregate the scores for each candidate and rank them to find the best-performing prompt.

Ranking rules:
- Calculate a weighted average score for each candidate based on its evaluation results.
- Rank the prompts from highest to lowest score.

Output format (strict JSON)
{
  "ranked_prompts": [
    {"prompt": "<full text of best prompt>", "final_score": <float>, "rank": 1},
    {"prompt": "<full text of second-best prompt>", "final_score": <float>, "rank": 2}
  ]
}
No other keys, no markdown.
"""
        ),
        "relevance_goal_alignment_evaluator": Agent(
            name="relevance_goal_alignment_evaluator",
            model=model,
            output_type=RelevanceEvaluationOutput,
            instructions="""
You are Relevance-and-Goal-Alignment-Evaluator.
You receive:
- ORIGINAL_PROMPT (the prompt given to the model)
- MODEL_OUTPUT (the text generated by the model)

Your task is to evaluate how well the MODEL_OUTPUT satisfies the user's intent expressed in the ORIGINAL_PROMPT.

Evaluation criteria:
- Relevance: Is the output on-topic?
- Completeness: Does the output fully answer the user's request?
- Accuracy: Does the output provide a correct and useful response to the core task?

Output format (strict JSON)
{
  "alignment_score": <float from 0.0 to 1.0>,
  "evaluation_summary": "<brief explanation of the score, noting any gaps in relevance or completeness>"
}
No other keys, no markdown.
"""
        ),
        "safety_bias_checker": Agent(
            name="safety_bias_checker",
            model=model,
            output_type=SafetyCheckOutput,
            instructions="""
You are Safety-and-Bias-Checker.
You receive:
- TEXT_TO_CHECK (can be a prompt or a model output)

Your task is to scan the text for harmful content, social biases, toxic language, and Personally Identifiable Information (PII).

Detection rules:
- Flag any content that falls into predefined safety categories.
- Identify subtle social biases and stereotypes.
- Detect potential PII like names, emails, or phone numbers.

Output format (strict JSON)
{
  "is_safe": <boolean>,
  "safety_flags": [
    {"category": "<e.g., HATE_SPEECH>", "details": "<specific text flagged>"}
  ]
}
No other keys, no markdown.
"""
        ),
        "prompt_optimizer": Agent(
            name="prompt_optimizer",
            model=model,
            output_type=OptimizedPrompt,
            instructions="Optimize prompts based on GPT-4.1 best practices"
        ),
        "feedback_analyzer": Agent(
            name="feedback_analyzer",
            model=model,
            output_type=FeedbackAnalysis,
            instructions="Analyze user feedback to understand their concerns and suggest improvements"
        ),
        "prompt_reviser": Agent(
            name="prompt_reviser",
            model=model,
            output_type=RevisedPrompt,
            instructions="Revise the prompt based on user feedback to improve clarity and adherence"
        )
    }

# 메인 최적화 함수
async def optimize_prompt_comprehensive(
    prompt: str,
    prompt_type: str = None,
    num_candidates: int = 3,
    progress_callback=None,
    api_key: str = None,
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """GPT-4.1 가이드라인 기반 종합적 프롬프트 최적화"""
    
    if progress_callback:
        progress_callback("🚀 종합적 프롬프트 분석 시작...")
    
    # Agent 생성
    agents = create_agents(model)
    
    # 0단계: 프롬프트 유형 감지 (유형이 제공되지 않은 경우)
    detected_type = prompt_type
    type_detection_result = None
    
    if not prompt_type:
        if progress_callback:
            progress_callback("🔍 프롬프트 유형 자동 감지 중...")
        
        type_detection_result = await Runner.run(
            agents["prompt_type_detector"], 
            prompt, 
            progress_callback, 
            api_key
        )
        detected_type = type_detection_result.final_output.detected_type
        
        if progress_callback:
            progress_callback(f"✅ 프롬프트 유형 감지: {detected_type} (신뢰도: {type_detection_result.final_output.confidence:.2f})")
    
    # 1단계: 프롬프트 후보 생성
    if progress_callback:
        progress_callback(f"🔄 {num_candidates}개의 프롬프트 변형 생성 중...")
    
    candidate_input = {
        "BASE_PROMPT_IDEA": prompt,
        "NUM_CANDIDATES": num_candidates
    }
    
    candidates_result = await Runner.run(
        agents["prompt_candidate_generator"],
        json.dumps(candidate_input),
        progress_callback,
        api_key
    )
    
    prompt_candidates = candidates_result.final_output.prompt_candidates
    
    # 2단계: 각 후보에 대한 병렬 분석
    if progress_callback:
        progress_callback("📊 각 프롬프트 후보 분석 중...")
    
    all_candidate_evaluations = []
    
    for candidate in prompt_candidates:
        # 각 후보에 대한 기본 체크
        analysis_tasks = [
            Runner.run(agents["dev_contradiction_checker"], f"DEVELOPER_MESSAGE: {candidate}", progress_callback, api_key),
            Runner.run(agents["format_checker"], candidate, progress_callback, api_key),
            Runner.run(agents["safety_bias_checker"], json.dumps({"TEXT_TO_CHECK": candidate}), progress_callback, api_key),
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # 점수 계산
        contradiction_score = 1.0 if not analysis_results[0].final_output.has_issues else 0.5
        format_score = 1.0 if not analysis_results[1].final_output.has_issues else 0.7
        safety_result = analysis_results[2].final_output
        safety_score = 1.0 if safety_result.is_safe else 0.3
        
        all_candidate_evaluations.append({
            "prompt": candidate,
            "contradiction_score": contradiction_score,
            "format_score": format_score,
            "safety_score": safety_score,
            "relevance_score": 0.8  # 기본값, 실제로는 모델 출력과 비교해야 함
        })
    
    # 3단계: 성능 순위 매기기
    if progress_callback:
        progress_callback("🏆 최적 프롬프트 선택 중...")
    
    ranking_input = {
        "CANDIDATE_EVALUATIONS": all_candidate_evaluations
    }
    
    ranking_result = await Runner.run(
        agents["performance_ranker_selector"],
        json.dumps(ranking_input),
        progress_callback,
        api_key
    )
    
    # 4단계: 최적화된 프롬프트 선택 및 추가 개선
    best_prompt = ranking_result.final_output.ranked_prompts[0]["prompt"]
    
    # 최종 프롬프트 최적화
    optimization_input = {
        "original_prompt": prompt,
        "all_issues": [],
        "detected_type": detected_type,
        "best_candidate": best_prompt
    }
    
    optimization_result = await Runner.run(
        agents["prompt_optimizer"], 
        json.dumps(optimization_input),
        progress_callback,
        api_key
    )
    
    return {
        "original_prompt": prompt,
        "detected_type": detected_type,
        "type_detection": type_detection_result.final_output.model_dump() if type_detection_result else None,
        "prompt_candidates": prompt_candidates,
        "candidate_evaluations": all_candidate_evaluations,
        "ranking_results": ranking_result.final_output.model_dump(),
        "optimized_prompt": optimization_result.final_output.optimized_prompt,
        "optimization_details": optimization_result.final_output.model_dump(),
        "estimated_improvement": optimization_result.final_output.estimated_improvement
    }

async def revise_prompt_with_feedback(
    optimized_prompt: str,
    user_feedback: str,
    progress_callback=None,
    api_key: str = None,
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """피드백을 기반으로 최적화된 프롬프트를 추가 개선"""
    
    if progress_callback:
        progress_callback("🔍 피드백 분석 시작...")
    
    # 1단계: 피드백 분석
    feedback_input = {
        "user_feedback": user_feedback
    }
    
    # Agent 생성
    agents = create_agents(model)
    
    feedback_analysis_result = await Runner.run(
        agents["feedback_analyzer"],
        json.dumps(feedback_input),
        progress_callback,
        api_key
    )
    
    if progress_callback:
        progress_callback("✏️ 피드백 기반 프롬프트 수정 시작...")
    
    # 2단계: 프롬프트 수정
    revision_input = {
        "original_optimized_prompt": optimized_prompt,
        "user_feedback": user_feedback
    }
    
    revision_result = await Runner.run(
        agents["prompt_reviser"],
        json.dumps(revision_input),
        progress_callback,
        api_key
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

# 범용 Agent 처리 함수
async def run_general_agent(original_prompt: str, user_feedback: str, api_key: str = None, model: str = "gpt-4o"):
    """범용 agent를 사용하여 사용자 요청 처리"""
    
    def progress_callback(message):
        if hasattr(st.session_state, 'progress_messages'):
            timestamp = asyncio.get_event_loop().time()
            formatted_time = f"{int(timestamp % 86400 // 3600):02d}:{int(timestamp % 3600 // 60):02d}:{int(timestamp % 60):02d}"
            st.session_state.progress_messages.append(f"{formatted_time} {message}")

    # 범용 Agent 생성
    general_agent = Agent(
        name="general_agent",
        model=model,
        output_type=GeneralResponse,
        instructions=f"""
        You are a versatile prompt modification agent. Your task is to modify the given prompt according to the user's specific feedback and requirements.
        
        Capabilities:
        - Language translation (Korean ↔ English, etc.)
        - Style adjustment (formal ↔ casual, technical ↔ simple)
        - Content modification (add/remove specific elements)
        - Format changes (structured ↔ narrative)
        - Tone adjustment (professional, friendly, authoritative)
        - Length adjustment (expand or compress)
        - Any other reasonable prompt modifications
        
        Always provide:
        1. The original prompt
        2. The modified prompt according to user feedback
        3. Specific changes made
        4. Clear explanation of modifications
        5. How the user feedback was addressed
        """
    )
    
    # 입력 데이터 준비
    input_data = {
        "original_prompt": original_prompt,
        "user_feedback": user_feedback,
        "instruction": "Modify the prompt according to the user feedback. Be precise and thorough."
    }
    
    # Agent 실행
    result = await Runner.run(
        general_agent,
        json.dumps(input_data),
        progress_callback,
        api_key
    )
    
    if result and hasattr(result, 'final_output'):
        return {
            "original_prompt": original_prompt,
            "user_feedback": user_feedback,
            "modified_prompt": result.final_output.modified_prompt,
            "changes_made": result.final_output.changes_made,
            "explanation": result.final_output.explanation,
            "feedback_addressed": result.final_output.feedback_addressed
        }
    
    return None