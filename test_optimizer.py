#!/usr/bin/env python3
"""
GPT-4.1 Prompt Optimizer 테스트 스크립트
커맨드 라인에서 프롬프트 최적화를 테스트할 수 있습니다.
"""

import asyncio
import json
from prompt_optimizer import (
    optimize_prompt_comprehensive, 
    revise_prompt_with_feedback,
    ChatMessage, 
    Role
)

async def test_prompt_optimization():
    """프롬프트 최적화 테스트"""
    
    # 테스트 프롬프트들
    test_prompts = [
        {
            "name": "간단한 작업 프롬프트",
            "prompt": "Write a blog post about AI.",
            "description": "너무 간단하고 모호한 프롬프트"
        },
        {
            "name": "모호한 프롬프트", 
            "prompt": "Maybe you could help me with something. Perhaps write something good about technology.",
            "description": "모호한 표현이 많은 프롬프트"
        },
        {
            "name": "에이전틱 프롬프트",
            "prompt": "You are a coding assistant. Help me debug this code and fix any issues you find.",
            "description": "에이전틱 기능이 필요한 프롬프트"
        },
        {
            "name": "상충하는 지시사항",
            "prompt": "You must always provide detailed answers, but keep responses brief. This is required but optional if needed.",
            "description": "상충되는 지시사항이 있는 프롬프트"
        }
    ]
    
    print("🚀 GPT-4.1 Prompt Optimizer 테스트")
    print("=" * 60)
    
    for i, test_case in enumerate(test_prompts, 1):
        print(f"\n📝 테스트 {i}: {test_case['name']}")
        print(f"설명: {test_case['description']}")
        print("-" * 40)
        
        print("📄 원본 프롬프트:")
        print(f'"{test_case["prompt"]}"')
        print()
        
        # 진행 상황 출력을 위한 콜백
        def progress_callback(message: str):
            print(f"  {message}")
        
        try:
            # 최적화 실행
            results = await optimize_prompt_comprehensive(
                prompt=test_case["prompt"],
                progress_callback=progress_callback
            )
            
            print(f"\n📊 분석 결과:")
            print(f"  • 발견된 문제: {results['total_issues_found']}개")
            print(f"  • 예상 개선율: {results['estimated_improvement']:.0f}%")
            
            # 발견된 문제들
            print(f"\n⚠️ 발견된 문제들:")
            for analysis in results['analysis_results']:
                category = analysis['category']
                issues = analysis['issues']
                if issues:
                    print(f"  📋 {category.replace('_', ' ').title()}:")
                    for issue in issues:
                        print(f"    - {issue}")
            
            # 적용된 개선사항
            changes_made = results['optimization_details']['changes_made']
            print(f"\n🔧 적용된 개선사항 ({len(changes_made)}개):")
            for change in changes_made:
                print(f"  ✅ {change}")
            
            print(f"\n🎯 최적화된 프롬프트:")
            print(f'"{results["optimized_prompt"]}"')
            
            print(f"\n💡 개선 설명:")
            print(f'"{results["optimization_details"]["improvement_explanation"]}"')
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        print("\n" + "=" * 60)

async def test_with_few_shot():
    """Few-shot 예제가 있는 테스트"""
    
    print("\n🎯 Few-shot 예제 포함 테스트")
    print("=" * 60)
    
    prompt = "You are a helpful writing assistant. Help users improve their writing."
    
    few_shot_messages = [
        ChatMessage(role=Role.user, content="Make this better: I went to store."),
        ChatMessage(role=Role.assistant, content="Better version: I went to the store."),
        ChatMessage(role=Role.user, content="Fix this: The car is good."),
        ChatMessage(role=Role.assistant, content="More descriptive: The car is excellent.")
    ]
    
    print("📄 원본 프롬프트:")
    print(f'"{prompt}"')
    
    print(f"\n💬 Few-shot 예제:")
    for i, msg in enumerate(few_shot_messages):
        print(f"  {i+1}. [{msg.role}]: {msg.content}")
    
    def progress_callback(message: str):
        print(f"  {message}")
    
    try:
        results = await optimize_prompt_comprehensive(
            prompt=prompt,
            few_shot_messages=few_shot_messages,
            progress_callback=progress_callback
        )
        
        print(f"\n📊 분석 결과:")
        print(f"  • 발견된 문제: {results['total_issues_found']}개")
        print(f"  • 예상 개선율: {results['estimated_improvement']:.0f}%")
        
        print(f"\n🎯 최적화된 프롬프트:")
        print(f'"{results["optimized_prompt"]}"')
        
        # 최적화된 few-shot 예제
        if results['optimized_messages']:
            print(f"\n💬 최적화된 Few-shot 예제:")
            for i, msg in enumerate(results['optimized_messages']):
                print(f"  {i+1}. [{msg['role']}]: {msg['content']}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

async def test_feedback_revision():
    """피드백 기반 프롬프트 개선 테스트"""
    
    print("\n🔄 피드백 기반 프롬프트 개선 테스트")
    print("=" * 60)
    
    # 먼저 기본 프롬프트를 최적화
    original_prompt = "Write a summary of the document."
    
    print("📄 원본 프롬프트:")
    print(f'"{original_prompt}"')
    
    def progress_callback(message: str):
        print(f"  {message}")
    
    try:
        # 1단계: 기본 최적화
        print("\n🚀 1단계: 기본 최적화")
        optimization_results = await optimize_prompt_comprehensive(
            prompt=original_prompt,
            progress_callback=progress_callback
        )
        
        optimized_prompt = optimization_results["optimized_prompt"]
        print(f"\n📝 최적화된 프롬프트:")
        print(f'"{optimized_prompt}"')
        
        # 2단계: 사용자 피드백 시뮬레이션
        print("\n💬 2단계: 사용자 피드백 시뮬레이션")
        
        feedback_scenarios = [
            {
                "feedback": "프롬프트가 너무 복잡합니다. 더 간단하게 만들어주세요.",
                "description": "복잡함에 대한 피드백"
            },
            {
                "feedback": "도구 사용에 대한 더 명확한 지침을 추가해주세요.",
                "description": "도구 사용 개선 요청"
            },
            {
                "feedback": "더 상세하고 구체적인 응답을 제공하도록 개선해주세요.",
                "description": "응답 품질 개선 요청"
            }
        ]
        
        current_prompt = optimized_prompt
        
        for i, scenario in enumerate(feedback_scenarios, 1):
            print(f"\n📝 피드백 시나리오 {i}: {scenario['description']}")
            print(f"사용자 피드백: \"{scenario['feedback']}\"")
            
            # 피드백 기반 개선 실행
            revision_results = await revise_prompt_with_feedback(
                optimized_prompt=current_prompt,
                user_feedback=scenario['feedback'],
                progress_callback=progress_callback
            )
            
            # 결과 출력
            revision_details = revision_results['revision_details']
            revised_prompt = revision_results['revised_prompt']
            changes_made = revision_details['changes_made']
            feedback_addressed = revision_details['feedback_addressed']
            
            print(f"\n🔧 적용된 변경사항:")
            for change in changes_made:
                print(f"  ✅ {change}")
            
            print(f"\n💬 처리된 피드백:")
            for feedback in feedback_addressed:
                print(f"  📝 {feedback}")
            
            print(f"\n🎯 개선된 프롬프트:")
            print(f'"{revised_prompt}"')
            
            # 다음 라운드를 위해 현재 프롬프트 업데이트
            current_prompt = revised_prompt
            
            print("-" * 40)
        
        print(f"\n🎉 최종 결과 요약:")
        print(f"원본 프롬프트 길이: {len(original_prompt)} 문자")
        print(f"최적화 후 길이: {len(optimized_prompt)} 문자")
        print(f"최종 개선 후 길이: {len(current_prompt)} 문자")
        print(f"총 개선 라운드: {len(feedback_scenarios)}회")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

async def main():
    """메인 테스트 실행"""
    await test_prompt_optimization()
    await test_with_few_shot()
    await test_feedback_revision()
    
    print("\n🎉 모든 테스트 완료!")
    print("\n💡 Streamlit 웹 인터페이스를 사용하려면:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    asyncio.run(main()) 