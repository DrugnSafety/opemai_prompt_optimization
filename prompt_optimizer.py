from openai import AsyncOpenAI
import asyncio
import json
import os
from enum import Enum
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field
import streamlit as st

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

# Agent 구현
class Agent:
    def __init__(self, name: str, model: str, output_type: type, instructions: str):
        self.name = name
        self.model = model
        self.output_type = output_type
        self.instructions = instructions

class Runner:
    @staticmethod
    async def run(agent: Agent, input_data: str, progress_callback=None):
        if progress_callback:
            progress_callback(f"🔍 Agent '{agent.name}' 실행 중...")
        
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
            
            # 에이전틱 구성 요소 추가
            if agentic_components:
                optimized_prompt += "\n\n" + "\n".join(agentic_components)
            
            # 4. 출력 형식 명시
            if 'format' not in optimized_prompt.lower():
                optimized_prompt += "\n\nProvide your response in a clear, structured format."
                changes_made.append("출력 형식 지침 추가")
            
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

# Agent 인스턴스 생성
clarity_checker = Agent(
    name="clarity_checker",
    model="gpt-4.1",
    output_type=Issues,
    instructions="Analyze prompt clarity based on GPT-4.1 guidelines"
)

specificity_checker = Agent(
    name="specificity_checker", 
    model="gpt-4.1",
    output_type=Issues,
    instructions="Analyze prompt specificity and concrete instructions"
)

instruction_following_checker = Agent(
    name="instruction_following_checker",
    model="gpt-4.1", 
    output_type=Issues,
    instructions="Check for contradictory or unclear instructions"
)

agentic_capability_checker = Agent(
    name="agentic_capability_checker",
    model="gpt-4.1",
    output_type=Issues,
    instructions="Analyze agentic workflow capabilities based on GPT-4.1 guide"
)

prompt_optimizer = Agent(
    name="prompt_optimizer",
    model="gpt-4.1",
    output_type=OptimizedPrompt,
    instructions="Optimize prompts based on GPT-4.1 best practices"
)

few_shot_optimizer = Agent(
    name="few_shot_optimizer",
    model="gpt-4.1",
    output_type=dict,
    instructions="Optimize few-shot examples for better performance"
)

feedback_analyzer = Agent(
    name="feedback_analyzer",
    model="gpt-4.1",
    output_type=FeedbackAnalysis,
    instructions="Analyze user feedback to understand their concerns and suggest improvements"
)

prompt_reviser = Agent(
    name="prompt_reviser",
    model="gpt-4.1",
    output_type=RevisedPrompt,
    instructions="Revise the prompt based on user feedback to improve clarity and adherence"
)

# 메인 최적화 함수
async def optimize_prompt_comprehensive(
    prompt: str,
    few_shot_messages: List[ChatMessage] = None,
    progress_callback=None
) -> Dict[str, Any]:
    """GPT-4.1 가이드라인 기반 종합적 프롬프트 최적화"""
    
    if progress_callback:
        progress_callback("🚀 종합적 프롬프트 분석 시작...")
    
    # 1단계: 병렬 분석
    analysis_tasks = [
        Runner.run(clarity_checker, prompt, progress_callback),
        Runner.run(specificity_checker, prompt, progress_callback),
        Runner.run(instruction_following_checker, prompt, progress_callback),
        Runner.run(agentic_capability_checker, prompt, progress_callback),
    ]
    
    analysis_results = await asyncio.gather(*analysis_tasks)
    
    # 2단계: 결과 집계
    all_issues = [result.final_output.model_dump() for result in analysis_results]
    total_issues = sum(len(issues['issues']) for issues in all_issues)
    
    if progress_callback:
        progress_callback(f"📊 분석 완료: 총 {total_issues}개 문제 발견")
    
    # 3단계: 프롬프트 최적화
    optimization_input = {
        "original_prompt": prompt,
        "all_issues": all_issues
    }
    
    optimization_result = await Runner.run(
        prompt_optimizer, 
        json.dumps(optimization_input),
        progress_callback
    )
    
    # 4단계: Few-shot 최적화 (있는 경우)
    final_messages = few_shot_messages or []
    if few_shot_messages:
        few_shot_input = {
            "messages": [msg.model_dump() for msg in few_shot_messages],
            "optimized_prompt": optimization_result.final_output.optimized_prompt
        }
        few_shot_result = await Runner.run(
            few_shot_optimizer,
            json.dumps(few_shot_input),
            progress_callback
        )
        final_messages = few_shot_result.final_output.get("messages", [])
    
    return {
        "original_prompt": prompt,
        "optimized_prompt": optimization_result.final_output.optimized_prompt,
        "analysis_results": all_issues,
        "optimization_details": optimization_result.final_output.model_dump(),
        "optimized_messages": final_messages,
        "total_issues_found": total_issues,
        "estimated_improvement": optimization_result.final_output.estimated_improvement
    }

async def revise_prompt_with_feedback(
    optimized_prompt: str,
    user_feedback: str,
    progress_callback=None
) -> Dict[str, Any]:
    """피드백을 기반으로 최적화된 프롬프트를 추가 개선"""
    
    if progress_callback:
        progress_callback("🔍 피드백 분석 시작...")
    
    # 1단계: 피드백 분석
    feedback_input = {
        "user_feedback": user_feedback
    }
    
    feedback_analysis_result = await Runner.run(
        feedback_analyzer,
        json.dumps(feedback_input),
        progress_callback
    )
    
    if progress_callback:
        progress_callback("✏️ 피드백 기반 프롬프트 수정 시작...")
    
    # 2단계: 프롬프트 수정
    revision_input = {
        "original_optimized_prompt": optimized_prompt,
        "user_feedback": user_feedback
    }
    
    revision_result = await Runner.run(
        prompt_reviser,
        json.dumps(revision_input),
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