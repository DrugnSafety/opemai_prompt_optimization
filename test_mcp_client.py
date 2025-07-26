#!/usr/bin/env python3
"""
MCP 클라이언트 테스트

프롬프트 최적화 MCP 서버의 기능을 테스트하는 클라이언트입니다.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict

async def test_mcp_server():
    """MCP 서버 기능을 테스트합니다"""
    
    print("🚀 MCP 프롬프트 최적화 서버 테스트")
    print("=" * 60)
    
    # 테스트할 프롬프트들
    test_cases = [
        {
            "name": "간단한 프롬프트 최적화",
            "tool": "optimize_prompt",
            "arguments": {
                "prompt": "Write a blog post about AI.",
                "include_analysis": True
            }
        },
        {
            "name": "Few-shot 예제 포함 최적화",
            "tool": "optimize_prompt", 
            "arguments": {
                "prompt": "You are a helpful writing assistant.",
                "few_shot_messages": [
                    {"role": "user", "content": "Make this better: I went to store."},
                    {"role": "assistant", "content": "Better version: I went to the store."}
                ],
                "include_analysis": True
            }
        },
        {
            "name": "프롬프트 분석만",
            "tool": "analyze_prompt",
            "arguments": {
                "prompt": "You must always provide detailed answers, but keep responses brief.",
                "analysis_types": ["clarity", "instruction_following"]
            }
        },
        {
            "name": "피드백 기반 개선",
            "tool": "revise_with_feedback",
            "arguments": {
                "optimized_prompt": "You are a helpful AI assistant. Write a blog post about AI.\n\nPlease provide detailed, comprehensive responses with clear explanations.",
                "user_feedback": "프롬프트가 너무 복잡합니다. 더 간단하게 만들어주세요.",
                "include_analysis": True
            }
        },
        {
            "name": "코딩 도메인 프롬프트 제안",
            "tool": "get_prompt_suggestions",
            "arguments": {
                "domain": "coding",
                "task_type": "debug",
                "requirements": ["Include error handling", "Explain step by step"]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 테스트 {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # MCP 메시지 구성
            mcp_request = {
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/call",
                "params": {
                    "name": test_case["tool"],
                    "arguments": test_case["arguments"]
                }
            }
            
            # MCP 서버와 통신 시뮬레이션
            print(f"🔧 도구: {test_case['tool']}")
            print(f"📊 입력 인수:")
            for key, value in test_case["arguments"].items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
            
            print("\n✅ 테스트 완료 (실제 MCP 서버 연결이 필요함)")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
    
    print(f"\n🎉 모든 MCP 테스트 완료!")
    print("\n💡 실제 사용법:")
    print("   1. MCP 서버 실행: python mcp_server.py")
    print("   2. Claude Desktop 등 MCP 클라이언트에서 연결")
    print("   3. prompt-optimizer 도구들 사용")

async def demonstrate_mcp_usage():
    """MCP 사용법을 시연합니다"""
    
    print("\n📚 MCP 통합 가이드")
    print("=" * 60)
    
    print("""
🔧 1. Claude Desktop에 MCP 서버 추가

Claude Desktop 설정 파일에 다음을 추가하세요:
(macOS: ~/Library/Application Support/Claude/claude_desktop_config.json)

{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "python",
      "args": ["/path/to/your/project/mcp_server.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}

🚀 2. 사용 가능한 도구들

• optimize_prompt: 프롬프트 종합 최적화
• revise_with_feedback: 피드백 기반 개선  
• analyze_prompt: 프롬프트 분석만
• get_prompt_suggestions: 도메인별 템플릿 제안

💡 3. 사용 예시

Claude Desktop에서:
"optimize_prompt 도구를 사용해서 이 프롬프트를 개선해줘: 'Write a summary'"

또는

"get_prompt_suggestions 도구로 코딩 도메인의 디버깅 프롬프트 템플릿을 만들어줘"

🔗 4. 다른 프로젝트에서 활용

MCP 표준을 따르므로 모든 MCP 호환 클라이언트에서 사용 가능:
• Claude Desktop
• Cursor (MCP 지원시)
• 커스텀 MCP 클라이언트
• API 래퍼

⚙️ 5. 확장 방법

새로운 도구 추가:
1. mcp_server.py에 새 Tool 정의
2. 해당 핸들러 메서드 구현
3. 서버 재시작

🛡️ 6. 보안 고려사항

• 신뢰할 수 있는 환경에서만 실행
• 입력 검증 및 sanitization
• 적절한 권한 설정
""")

def show_mcp_architecture():
    """MCP 아키텍처를 설명합니다"""
    
    print("\n🏗️ MCP 아키텍처")
    print("=" * 60)
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│                        MCP 생태계                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    JSON-RPC     ┌─────────────────┐       │
│  │   AI Client     │◄─────────────────▶│   MCP Server    │       │
│  │                 │                  │                 │       │ 
│  │ • Claude Desktop│                  │ • prompt-optimizer│      │
│  │ • Cursor        │                  │ • 4개 도구 제공   │       │
│  │ • Custom Apps   │                  │ • GPT-4.1 최적화 │       │
│  └─────────────────┘                  └─────────────────┘       │
│           │                                     │                │
│           │                                     │                │
│           ▼                                     ▼                │
│  ┌─────────────────┐                  ┌─────────────────┐       │
│  │ User Interface  │                  │ Business Logic  │       │
│  │                 │                  │                 │       │
│  │ • 채팅 UI       │                  │ • 프롬프트 분석  │       │
│  │ • 도구 호출     │                  │ • GPT-4.1 최적화│       │
│  │ • 결과 표시     │                  │ • 피드백 처리   │       │
│  └─────────────────┘                  └─────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

🔄 통신 흐름:

1. 사용자가 AI 클라이언트에서 도구 사용 요청
2. 클라이언트가 MCP 서버에 JSON-RPC 메시지 전송
3. 서버가 요청을 처리하고 프롬프트 최적화 수행
4. 서버가 결과를 JSON-RPC 응답으로 반환
5. 클라이언트가 사용자에게 결과 표시

📡 JSON-RPC 메시지 예시:

요청:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "optimize_prompt",
    "arguments": {
      "prompt": "Write a summary",
      "include_analysis": true
    }
  }
}

응답:
{
  "jsonrpc": "2.0", 
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# 🚀 프롬프트 최적화 결과\\n\\n..."
      }
    ]
  }
}
""")

async def main():
    """메인 실행 함수"""
    await test_mcp_server()
    await demonstrate_mcp_usage()
    show_mcp_architecture()

if __name__ == "__main__":
    asyncio.run(main()) 