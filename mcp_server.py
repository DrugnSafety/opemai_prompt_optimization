#!/usr/bin/env python3
"""
MCP Server for Prompt Optimizer

이 MCP 서버는 프롬프트 최적화 기능을 다른 AI 프로젝트에서 
쉽게 사용할 수 있도록 표준화된 도구를 제공합니다.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# 우리의 프롬프트 최적화 모듈 임포트
from prompt_optimizer import (
    optimize_prompt_comprehensive,
    revise_prompt_with_feedback,
    ChatMessage,
    Role
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompt-optimizer-mcp")

class PromptOptimizerMCPServer:
    """프롬프트 최적화를 위한 MCP 서버"""
    
    def __init__(self):
        self.server = Server("prompt-optimizer")
        self.setup_tools()
    
    def setup_tools(self):
        """MCP 도구들을 설정합니다"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """사용 가능한 도구 목록을 반환합니다"""
            return [
                Tool(
                    name="optimize_prompt",
                    description="GPT-4.1 가이드라인에 따라 프롬프트를 종합적으로 분석하고 최적화합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "최적화할 프롬프트 텍스트"
                            },
                            "few_shot_messages": {
                                "type": "array",
                                "description": "Few-shot 예제 메시지들 (선택사항)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "role": {
                                            "type": "string",
                                            "enum": ["user", "assistant"],
                                            "description": "메시지 역할"
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "메시지 내용"
                                        }
                                    },
                                    "required": ["role", "content"]
                                }
                            },
                            "include_analysis": {
                                "type": "boolean",
                                "description": "상세한 분석 결과를 포함할지 여부 (기본값: true)",
                                "default": True
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="revise_with_feedback",
                    description="사용자 피드백을 바탕으로 최적화된 프롬프트를 추가 개선합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "optimized_prompt": {
                                "type": "string",
                                "description": "이미 최적화된 프롬프트"
                            },
                            "user_feedback": {
                                "type": "string",
                                "description": "사용자의 피드백"
                            },
                            "include_analysis": {
                                "type": "boolean",
                                "description": "피드백 분석 결과를 포함할지 여부 (기본값: true)",
                                "default": True
                            }
                        },
                        "required": ["optimized_prompt", "user_feedback"]
                    }
                ),
                Tool(
                    name="analyze_prompt",
                    description="프롬프트를 분석하여 문제점만 찾아냅니다 (최적화하지 않음)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "분석할 프롬프트 텍스트"
                            },
                            "analysis_types": {
                                "type": "array",
                                "description": "수행할 분석 유형들",
                                "items": {
                                    "type": "string",
                                    "enum": ["clarity", "specificity", "instruction_following", "agentic_capabilities"]
                                },
                                "default": ["clarity", "specificity", "instruction_following", "agentic_capabilities"]
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="get_prompt_suggestions",
                    description="특정 도메인이나 목적에 맞는 프롬프트 템플릿 및 제안사항을 제공합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "프롬프트 도메인 (예: coding, writing, analysis, creative, customer_service)",
                                "enum": ["coding", "writing", "analysis", "creative", "customer_service", "education", "general"]
                            },
                            "task_type": {
                                "type": "string",
                                "description": "작업 유형 (예: debug, review, generate, summarize, translate)"
                            },
                            "requirements": {
                                "type": "array",
                                "description": "특별 요구사항들",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["domain"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[TextContent | ImageContent | EmbeddedResource]:
            """도구 호출을 처리합니다"""
            
            if arguments is None:
                arguments = {}
            
            try:
                if name == "optimize_prompt":
                    return await self._handle_optimize_prompt(arguments)
                elif name == "revise_with_feedback":
                    return await self._handle_revise_with_feedback(arguments)
                elif name == "analyze_prompt":
                    return await self._handle_analyze_prompt(arguments)
                elif name == "get_prompt_suggestions":
                    return await self._handle_get_prompt_suggestions(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error handling tool {name}: {str(e)}")
                return [
                    TextContent(
                        type="text",
                        text=f"오류가 발생했습니다: {str(e)}"
                    )
                ]
    
    async def _handle_optimize_prompt(self, arguments: dict) -> list[TextContent]:
        """프롬프트 최적화 도구 처리"""
        prompt = arguments.get("prompt", "")
        few_shot_messages = arguments.get("few_shot_messages", [])
        include_analysis = arguments.get("include_analysis", True)
        
        if not prompt:
            return [TextContent(type="text", text="프롬프트가 제공되지 않았습니다.")]
        
        # Few-shot 메시지 변환
        chat_messages = []
        for msg in few_shot_messages:
            role = Role.user if msg["role"] == "user" else Role.assistant
            chat_messages.append(ChatMessage(role=role, content=msg["content"]))
        
        # 프롬프트 최적화 실행
        result = await optimize_prompt_comprehensive(
            prompt=prompt,
            few_shot_messages=chat_messages if chat_messages else None
        )
        
        # 결과 포맷팅
        response = self._format_optimization_result(result, include_analysis)
        
        return [TextContent(type="text", text=response)]
    
    async def _handle_revise_with_feedback(self, arguments: dict) -> list[TextContent]:
        """피드백 기반 개선 도구 처리"""
        optimized_prompt = arguments.get("optimized_prompt", "")
        user_feedback = arguments.get("user_feedback", "")
        include_analysis = arguments.get("include_analysis", True)
        
        if not optimized_prompt or not user_feedback:
            return [TextContent(type="text", text="최적화된 프롬프트와 피드백이 모두 필요합니다.")]
        
        # 피드백 기반 개선 실행
        result = await revise_prompt_with_feedback(
            optimized_prompt=optimized_prompt,
            user_feedback=user_feedback
        )
        
        # 결과 포맷팅
        response = self._format_revision_result(result, include_analysis)
        
        return [TextContent(type="text", text=response)]
    
    async def _handle_analyze_prompt(self, arguments: dict) -> list[TextContent]:
        """프롬프트 분석 도구 처리"""
        prompt = arguments.get("prompt", "")
        analysis_types = arguments.get("analysis_types", ["clarity", "specificity", "instruction_following", "agentic_capabilities"])
        
        if not prompt:
            return [TextContent(type="text", text="프롬프트가 제공되지 않았습니다.")]
        
        # 분석만 수행 (최적화 없이)
        result = await optimize_prompt_comprehensive(
            prompt=prompt,
            few_shot_messages=None
        )
        
        # 분석 결과만 포맷팅
        response = self._format_analysis_only(result, analysis_types)
        
        return [TextContent(type="text", text=response)]
    
    async def _handle_get_prompt_suggestions(self, arguments: dict) -> list[TextContent]:
        """프롬프트 제안 도구 처리"""
        domain = arguments.get("domain", "general")
        task_type = arguments.get("task_type", "")
        requirements = arguments.get("requirements", [])
        
        # 도메인별 프롬프트 템플릿 생성
        suggestions = self._generate_prompt_suggestions(domain, task_type, requirements)
        
        return [TextContent(type="text", text=suggestions)]
    
    def _format_optimization_result(self, result: dict, include_analysis: bool) -> str:
        """최적화 결과를 포맷팅합니다"""
        output = []
        
        output.append("# 🚀 프롬프트 최적화 결과")
        output.append("")
        
        # 요약 정보
        output.append("## 📊 최적화 요약")
        output.append(f"- **발견된 문제**: {result.get('total_issues_found', 0)}개")
        output.append(f"- **예상 개선율**: {result.get('estimated_improvement', 0):.0f}%")
        output.append("")
        
        # 최적화된 프롬프트
        output.append("## ✨ 최적화된 프롬프트")
        output.append("```")
        output.append(result.get('optimized_prompt', ''))
        output.append("```")
        output.append("")
        
        if include_analysis:
            # 상세 분석 결과
            analysis_results = result.get('analysis_results', [])
            if analysis_results:
                output.append("## 🔍 발견된 문제점")
                for i, issue in enumerate(analysis_results, 1):
                    output.append(f"{i}. {issue}")
                output.append("")
            
            # Few-shot 예제 (있는 경우)
            optimized_messages = result.get('optimized_messages', [])
            if optimized_messages:
                output.append("## 💬 최적화된 Few-shot 예제")
                for i, msg in enumerate(optimized_messages, 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    output.append(f"{i}. **{role}**: {content}")
                output.append("")
        
        return "\n".join(output)
    
    def _format_revision_result(self, result: dict, include_analysis: bool) -> str:
        """개선 결과를 포맷팅합니다"""
        output = []
        
        output.append("# 🔄 피드백 기반 프롬프트 개선 결과")
        output.append("")
        
        revision_details = result.get('revision_details', {})
        changes_made = revision_details.get('changes_made', [])
        feedback_addressed = revision_details.get('feedback_addressed', [])
        
        # 요약 정보
        output.append("## 📊 개선 요약")
        output.append(f"- **적용된 변경사항**: {len(changes_made)}개")
        output.append(f"- **처리된 피드백**: {len(feedback_addressed)}개")
        output.append("")
        
        # 개선된 프롬프트
        output.append("## ✨ 개선된 프롬프트")
        output.append("```")
        output.append(result.get('revised_prompt', ''))
        output.append("```")
        output.append("")
        
        if include_analysis:
            # 적용된 변경사항
            if changes_made:
                output.append("## 🔧 적용된 변경사항")
                for i, change in enumerate(changes_made, 1):
                    output.append(f"{i}. {change}")
                output.append("")
            
            # 처리된 피드백
            if feedback_addressed:
                output.append("## 💬 처리된 피드백")
                for i, feedback in enumerate(feedback_addressed, 1):
                    output.append(f"{i}. {feedback}")
                output.append("")
            
            # 개선 설명
            improvement_explanation = revision_details.get('improvement_explanation', '')
            if improvement_explanation:
                output.append("## 💡 개선 설명")
                output.append(improvement_explanation)
                output.append("")
        
        return "\n".join(output)
    
    def _format_analysis_only(self, result: dict, analysis_types: list) -> str:
        """분석 결과만 포맷팅합니다"""
        output = []
        
        output.append("# 🔍 프롬프트 분석 결과")
        output.append("")
        
        # 요약 정보
        output.append("## 📊 분석 요약")
        output.append(f"- **분석 유형**: {', '.join(analysis_types)}")
        output.append(f"- **발견된 문제**: {result.get('total_issues_found', 0)}개")
        output.append("")
        
        # 발견된 문제점
        analysis_results = result.get('analysis_results', [])
        if analysis_results:
            output.append("## ⚠️ 발견된 문제점")
            for i, issue in enumerate(analysis_results, 1):
                output.append(f"{i}. {issue}")
            output.append("")
        else:
            output.append("## ✅ 분석 결과")
            output.append("발견된 문제가 없습니다. 프롬프트가 잘 작성되었습니다!")
            output.append("")
        
        return "\n".join(output)
    
    def _generate_prompt_suggestions(self, domain: str, task_type: str, requirements: list) -> str:
        """도메인별 프롬프트 제안을 생성합니다"""
        output = []
        
        output.append(f"# 🎯 {domain.title()} 도메인 프롬프트 제안")
        output.append("")
        
        # 도메인별 템플릿
        templates = {
            "coding": {
                "base": "You are an expert software developer and code reviewer.",
                "guidelines": [
                    "Always provide detailed explanations for code changes",
                    "Include error handling and edge cases",
                    "Follow best practices and coding standards",
                    "Suggest performance improvements when applicable"
                ],
                "examples": {
                    "debug": "Analyze this code and identify any bugs, performance issues, or security vulnerabilities. Provide specific fixes with explanations.",
                    "review": "Review this code for best practices, readability, and maintainability. Suggest improvements with detailed explanations.",
                    "generate": "Generate clean, well-documented code that follows best practices. Include error handling and comments explaining the logic."
                }
            },
            "writing": {
                "base": "You are a professional writing assistant and editor.",
                "guidelines": [
                    "Maintain the original tone and style unless specified",
                    "Provide specific suggestions for improvement",
                    "Explain grammar and style recommendations",
                    "Consider the target audience"
                ],
                "examples": {
                    "edit": "Review this text for grammar, clarity, and style. Provide specific suggestions for improvement while maintaining the original tone.",
                    "generate": "Write [type of content] that is engaging, well-structured, and appropriate for [target audience]. Focus on clarity and impact.",
                    "summarize": "Create a concise summary that captures the key points and main arguments while maintaining the essential meaning."
                }
            },
            "analysis": {
                "base": "You are an expert analyst with deep analytical thinking skills.",
                "guidelines": [
                    "Provide structured, logical analysis",
                    "Support conclusions with evidence",
                    "Consider multiple perspectives",
                    "Identify patterns and trends"
                ],
                "examples": {
                    "analyze": "Analyze this data/situation thoroughly. Identify key patterns, trends, and insights. Provide actionable recommendations based on your findings.",
                    "compare": "Compare and contrast these options/concepts. Analyze the strengths, weaknesses, and implications of each approach.",
                    "evaluate": "Evaluate this proposal/solution critically. Consider feasibility, risks, benefits, and potential outcomes."
                }
            }
        }
        
        # 선택된 도메인의 템플릿 가져오기
        template = templates.get(domain, {
            "base": "You are a helpful AI assistant.",
            "guidelines": [
                "Provide clear and accurate information",
                "Be helpful and responsive to user needs",
                "Ask clarifying questions when needed"
            ],
            "examples": {}
        })
        
        # 기본 템플릿
        output.append("## 🏗️ 기본 템플릿")
        output.append("```")
        output.append(template["base"])
        output.append("")
        output.append("# Guidelines:")
        for guideline in template["guidelines"]:
            output.append(f"- {guideline}")
        
        # 요구사항 추가
        if requirements:
            output.append("")
            output.append("# Additional Requirements:")
            for req in requirements:
                output.append(f"- {req}")
        
        output.append("")
        output.append("Please keep going until the task is completely resolved, before ending your turn.")
        output.append("Plan extensively before taking action, and reflect on the outcomes of your actions.")
        output.append("```")
        output.append("")
        
        # 작업 유형별 예제
        if task_type and task_type in template["examples"]:
            output.append(f"## 💡 '{task_type}' 작업을 위한 특화 프롬프트")
            output.append("```")
            output.append(template["base"])
            output.append("")
            output.append(template["examples"][task_type])
            output.append("```")
            output.append("")
        
        # 추가 제안
        output.append("## 📝 추가 개선 제안")
        output.append("1. **명확한 출력 형식 지정**: 원하는 출력 형식(JSON, 마크다운, 구조화된 텍스트 등)을 명시하세요")
        output.append("2. **예제 제공**: Few-shot 예제를 추가하여 기대하는 응답 스타일을 명확히 하세요")
        output.append("3. **제약사항 명시**: 길이 제한, 사용할 언어, 피해야 할 내용 등을 명확히 하세요")
        output.append("4. **컨텍스트 제공**: 작업의 배경, 목적, 대상 독자 등의 컨텍스트를 제공하세요")
        output.append("")
        
        return "\n".join(output)
    
    async def run(self):
        """MCP 서버를 실행합니다"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="prompt-optimizer",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """메인 실행 함수"""
    server = PromptOptimizerMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 