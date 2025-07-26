# -*- coding: utf-8 -*-
"""
언어 설정 및 다국어 지원을 위한 설정 파일
Language configuration and multi-language support
"""

# 언어별 텍스트 정의
LANGUAGES = {
    "한국어": "ko",
    "English": "en"
}

TEXTS = {
    "ko": {
        # 페이지 설정
        "page_title": "GPT-4.1 Prompt Optimizer",
        "page_description": "OpenAI GPT-4.1 가이드라인을 기반으로 한 지능형 프롬프트 최적화 도구",
        
        # 사이드바
        "sidebar_title": "🚀 GPT-4.1 Prompt Optimizer",
        "language_select": "🌍 언어 선택",
        "openai_settings": "🔑 OpenAI 설정",
        "api_key_input": "OpenAI API Key",
        "api_key_help": "OpenAI API 키를 입력하세요. 이 키는 로컬에서만 사용되며 저장되지 않습니다.",
        "model_select": "GPT 모델 선택",
        "model_help": "사용할 GPT 모델을 선택하세요.",
        "api_key_set": "✅ API 키가 설정되었습니다",
        "api_key_warning": "⚠️ API 키를 입력해주세요",
        "contact_info": "📧 연락처",
        "contact_text": """
**이메일:** [irreversibly@gmail.com](mailto:irreversibly@gmail.com)

**LinkedIn:** [mingyu-kang-28473493](https://linkedin.com/in/mingyu-kang-28473493)
""",
        "reference_materials": "📖 참고 자료",
        "reference_text": """
이 도구는 [OpenAI Cookbook의 Prompt Optimization 예제](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)를 참고하여 개발되었습니다.

**주요 개선 영역:**
- 명확성 (Clarity)
- 구체성 (Specificity) 
- 지시사항 준수 (Instruction Following)
- 에이전틱 능력 (Agentic Capabilities)
""",
        "version": "버전: 1.0.0",
        
        # 메인 페이지
        "main_title": "🚀 GPT-4.1 Prompt Optimizer",
        "main_description": "OpenAI GPT-4.1 가이드라인을 기반으로 한 지능형 프롬프트 최적화 도구",
        "reference_info": """
📖 **참고 자료**: 이 도구는 [OpenAI Cookbook의 Prompt Optimization 예제](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)를 참고하여 개발되었습니다.
""",
        
        # 탭 제목
        "tab_input": "📝 프롬프트 입력",
        "tab_progress": "🔍 분석 진행",
        "tab_analysis": "📊 분석 결과",
        "tab_optimization": "✨ 최적화 결과",
        "tab_feedback": "🔄 피드백 & 리비전",
        
        # 프롬프트 입력 탭
        "prompt_input_header": "📝 프롬프트 입력",
        "main_prompt": "메인 프롬프트",
        "prompt_placeholder": """예시:
Write a blog post about artificial intelligence.

또는

You are a helpful assistant. Help me improve my writing skills.""",
        "prompt_help": "GPT-4.1에 전달할 메인 프롬프트를 입력하세요. 시스템 메시지, 사용자 지시사항 등 모든 형태의 프롬프트가 가능합니다.",
        "prompt_type": "프롬프트 유형",
        "prompt_type_options": [
            "일반 작업",
            "창작 작업", 
            "분석 작업",
            "코딩 작업",
            "에이전틱 워크플로우",
            "교육/학습",
            "기타"
        ],
        "advanced_settings": "고급 설정",
        "agentic_enhancement": "에이전틱 기능 강화",
        "agentic_help": "GPT-4.1의 에이전틱 워크플로우 기능을 최적화합니다",
        "tool_optimization": "도구 사용 최적화",
        "tool_help": "함수 호출 및 도구 사용에 최적화합니다",
        "few_shot_examples": "Few-shot 예제 (선택사항)",
        "few_shot_description": "프롬프트의 성능을 향상시키기 위한 예제를 추가할 수 있습니다.",
        "add_example": "➕ 예제 추가",
        "delete_examples": "🗑️ 모든 예제 삭제",
        "few_shot_examples_header": "**Few-shot 예제:**",
        "user_message": "사용자 메시지",
        "assistant_response": "어시스턴트 응답",
        "start_optimization": "🚀 프롬프트 최적화 시작",
        "api_key_required": "⚠️ OpenAI API 키를 입력해주세요.",
        "prompt_required": "⚠️ 프롬프트를 입력해주세요.",
        "optimization_complete": "✅ 최적화가 완료되었습니다! '분석 결과' 탭에서 확인하세요.",
        "optimization_error": "❌ 최적화 중 오류가 발생했습니다.",
        
        # 분석 진행 탭
        "analysis_progress_header": "🔍 분석 진행 상황",
        "realtime_progress": "실시간 진행 상황",
        "progress_rate": "진행률",
        "no_progress_info": "💡 '프롬프트 입력' 탭에서 최적화를 시작하세요.",
        "expected_steps": "예상 분석 단계",
        
        # 분석 결과 탭
        "analysis_results_header": "📊 분석 결과",
        "found_issues": "발견된 문제",
        "expected_improvement": "예상 개선율",
        "high_risk_issues": "고위험 문제",
        "applied_improvements": "적용된 개선사항",
        "detailed_analysis": "🔍 상세 분석 결과",
        "no_issues": "문제 없음 ✅",
        "original_prompt_header": "📝 원본 프롬프트",
        "view_original": "원본 프롬프트 보기",
        "no_analysis_info": "💡 분석 결과가 없습니다. 먼저 프롬프트를 최적화해주세요.",
        
        # 최적화 결과 탭
        "optimization_results_header": "✨ 최적화 결과",
        "improvement_summary": "📈 개선사항 요약",
        "performance_improvement": "**예상 성능 개선**",
        "applied_changes": "**적용된 개선사항**",
        "changes_made": "🔧 적용된 변경사항",
        "improvement_explanation": "💡 개선 설명",
        "optimized_prompt_header": "🎯 최적화된 프롬프트",
        "copy_button": "📋 복사",
        "download_button": "💾 다운로드",
        "copy_info": "클립보드 복사는 브라우저에서 직접 수행해주세요.",
        "changes_comparison": "🔄 변경사항 비교",
        "original_prompt": "**원본 프롬프트**",
        "optimized_prompt": "**최적화된 프롬프트**",
        "optimized_few_shot": "💬 최적화된 Few-shot 예제",
        "user": "**사용자**",
        "assistant": "**어시스턴트**",
        "new_optimization": "🔄 새로운 프롬프트 최적화",
        "no_optimization_info": "💡 최적화 결과가 없습니다. 먼저 프롬프트를 최적화해주세요.",
        
        # 피드백 및 리비전 탭
        "feedback_revision_header": "🔄 피드백 & 리비전",
        "current_optimized_prompt": "📝 현재 최적화된 프롬프트",
        "view_current_prompt": "현재 최적화된 프롬프트 보기",
        "provide_feedback": "💬 피드백 제공",
        "feedback_placeholder": """예시 피드백:
• 프롬프트가 너무 복잡해 보입니다. 더 간단하게 만들어주세요.
• 도구 사용에 대한 지침이 부족합니다.
• 응답이 너무 짧을 것 같습니다. 더 상세한 답변을 요구해주세요.
• 특정 형식으로 출력하도록 명시해주세요.
• 계획 수립 단계를 추가해주세요.""",
        "feedback_help": "구체적인 피드백을 제공할수록 더 나은 개선 결과를 얻을 수 있습니다.",
        "feedback_category": "피드백 카테고리",
        "feedback_type": "피드백 유형을 선택하세요",
        "feedback_types": [
            "일반적인 개선사항",
            "명확성 개선",
            "구체성 개선", 
            "지시사항 수정",
            "에이전틱 능력 개선",
            "형식 개선",
            "기타"
        ],
        "priority": "우선순위",
        "priority_options": ["낮음", "보통", "높음"],
        "quick_feedback": "빠른 피드백",
        "feedback_complex": "너무 복잡함",
        "feedback_tools": "도구 사용 개선",
        "feedback_length": "응답 길이 조정",
        "feedback_planning": "계획 수립 추가",
        "start_feedback_improvement": "🚀 피드백 기반 개선 시작",
        "feedback_required": "⚠️ 피드백을 입력해주세요.",
        "feedback_complete": "✅ 피드백 기반 개선이 완료되었습니다!",
        "feedback_error": "❌ 피드백 기반 개선 중 오류가 발생했습니다.",
        "improvement_progress": "🔍 개선 진행 상황",
        "feedback_improvement_results": "📊 피드백 기반 개선 결과",
        "applied_changes_count": "적용된 변경사항",
        "processed_feedback": "처리된 피드백",
        "improvement_score": "개선 점수",
        "processed_feedback_list": "💬 처리된 피드백",
        "final_improved_prompt": "🎯 최종 개선된 프롬프트",
        "before_after_comparison": "🔄 개선 전후 비교",
        "before_optimization": "**개선 전 (최적화된 프롬프트)**",
        "after_feedback": "**개선 후 (피드백 반영)**",
        "additional_feedback": "🔄 추가 피드백 제공",
        "improvement_complete": "✅ 개선 완료",
        "improvement_finished": "🎉 프롬프트 개선이 완료되었습니다!",
        "go_to_input": "📝 프롬프트 최적화하러 가기",
        "no_feedback_info": "💡 최적화 결과가 없습니다. 먼저 '프롬프트 입력' 탭에서 프롬프트를 최적화해주세요.",
        
        # 진행 메시지
        "progress_start": "🚀 종합적 프롬프트 분석 시작...",
        "progress_clarity": "📋 명확성 분석 중...",
        "progress_specificity": "🎯 구체성 분석 중...",
        "progress_instruction": "📏 지시사항 준수 분석 중...",
        "progress_agentic": "🤖 에이전틱 능력 분석 중...",
        "progress_complete": "✅ 최적화 완료!",
        
        # 빠른 피드백 텍스트
        "quick_feedback_complex": "프롬프트가 너무 복잡합니다. 더 간단하고 명확하게 만들어주세요.",
        "quick_feedback_tools": "도구 사용에 대한 더 명확한 지침을 추가해주세요.",
        "quick_feedback_length": "더 상세하고 구체적인 응답을 제공하도록 개선해주세요.",
        "quick_feedback_planning": "단계별 계획 수립 및 반성적 사고 과정을 추가해주세요.",
        
        # 추가 메시지
        "optimizing_prompt": "프롬프트 최적화 중...",
        "improvement_finished_msg": "🎉 프롬프트 개선이 완료되었습니다!"
    },
    
    "en": {
        # Page settings
        "page_title": "GPT-4.1 Prompt Optimizer",
        "page_description": "Intelligent prompt optimization tool based on OpenAI GPT-4.1 guidelines",
        
        # Sidebar
        "sidebar_title": "🚀 GPT-4.1 Prompt Optimizer",
        "language_select": "🌍 Language",
        "openai_settings": "🔑 OpenAI Settings",
        "api_key_input": "OpenAI API Key",
        "api_key_help": "Enter your OpenAI API key. This key is only used locally and not stored.",
        "model_select": "Select GPT Model",
        "model_help": "Choose the GPT model to use.",
        "api_key_set": "✅ API key is set",
        "api_key_warning": "⚠️ Please enter your API key",
        "contact_info": "📧 Contact",
        "contact_text": """
**Email:** [irreversibly@gmail.com](mailto:irreversibly@gmail.com)

**LinkedIn:** [mingyu-kang-28473493](https://linkedin.com/in/mingyu-kang-28473493)
""",
        "reference_materials": "📖 References",
        "reference_text": """
This tool was developed based on [OpenAI Cookbook's Prompt Optimization example](https://cookbook.openai.com/examples/gpt4-1_prompting_guide).

**Key Improvement Areas:**
- Clarity
- Specificity
- Instruction Following
- Agentic Capabilities
""",
        "version": "Version: 1.0.0",
        
        # Main page
        "main_title": "🚀 GPT-4.1 Prompt Optimizer",
        "main_description": "Intelligent prompt optimization tool based on OpenAI GPT-4.1 guidelines",
        "reference_info": """
📖 **Reference**: This tool was developed based on [OpenAI Cookbook's Prompt Optimization example](https://cookbook.openai.com/examples/gpt4-1_prompting_guide).
""",
        
        # Tab titles
        "tab_input": "📝 Prompt Input",
        "tab_progress": "🔍 Analysis Progress",
        "tab_analysis": "📊 Analysis Results",
        "tab_optimization": "✨ Optimization Results",
        "tab_feedback": "🔄 Feedback & Revision",
        
        # Prompt input tab
        "prompt_input_header": "📝 Prompt Input",
        "main_prompt": "Main Prompt",
        "prompt_placeholder": """Example:
Write a blog post about artificial intelligence.

or

You are a helpful assistant. Help me improve my writing skills.""",
        "prompt_help": "Enter the main prompt to send to GPT-4.1. Any form of prompt is possible including system messages, user instructions, etc.",
        "prompt_type": "Prompt Type",
        "prompt_type_options": [
            "General Task",
            "Creative Task", 
            "Analysis Task",
            "Coding Task",
            "Agentic Workflow",
            "Education/Learning",
            "Other"
        ],
        "advanced_settings": "Advanced Settings",
        "agentic_enhancement": "Agentic Enhancement",
        "agentic_help": "Optimizes GPT-4.1's agentic workflow capabilities",
        "tool_optimization": "Tool Usage Optimization",
        "tool_help": "Optimizes for function calling and tool usage",
        "few_shot_examples": "Few-shot Examples (Optional)",
        "few_shot_description": "You can add examples to improve prompt performance.",
        "add_example": "➕ Add Example",
        "delete_examples": "🗑️ Delete All Examples",
        "few_shot_examples_header": "**Few-shot Examples:**",
        "user_message": "User Message",
        "assistant_response": "Assistant Response",
        "start_optimization": "🚀 Start Prompt Optimization",
        "api_key_required": "⚠️ Please enter your OpenAI API key.",
        "prompt_required": "⚠️ Please enter a prompt.",
        "optimization_complete": "✅ Optimization completed! Check the 'Analysis Results' tab.",
        "optimization_error": "❌ An error occurred during optimization.",
        
        # Analysis progress tab
        "analysis_progress_header": "🔍 Analysis Progress",
        "realtime_progress": "Real-time Progress",
        "progress_rate": "Progress Rate",
        "no_progress_info": "💡 Start optimization in the 'Prompt Input' tab.",
        "expected_steps": "Expected Analysis Steps",
        
        # Analysis results tab
        "analysis_results_header": "📊 Analysis Results",
        "found_issues": "Issues Found",
        "expected_improvement": "Expected Improvement",
        "high_risk_issues": "High Risk Issues",
        "applied_improvements": "Applied Improvements",
        "detailed_analysis": "🔍 Detailed Analysis Results",
        "no_issues": "No Issues ✅",
        "original_prompt_header": "📝 Original Prompt",
        "view_original": "View Original Prompt",
        "no_analysis_info": "💡 No analysis results. Please optimize a prompt first.",
        
        # Optimization results tab
        "optimization_results_header": "✨ Optimization Results",
        "improvement_summary": "📈 Improvement Summary",
        "performance_improvement": "**Expected Performance Improvement**",
        "applied_changes": "**Applied Improvements**",
        "changes_made": "🔧 Applied Changes",
        "improvement_explanation": "💡 Improvement Explanation",
        "optimized_prompt_header": "🎯 Optimized Prompt",
        "copy_button": "📋 Copy",
        "download_button": "💾 Download",
        "copy_info": "Please copy directly in your browser.",
        "changes_comparison": "🔄 Changes Comparison",
        "original_prompt": "**Original Prompt**",
        "optimized_prompt": "**Optimized Prompt**",
        "optimized_few_shot": "💬 Optimized Few-shot Examples",
        "user": "**User**",
        "assistant": "**Assistant**",
        "new_optimization": "🔄 New Prompt Optimization",
        "no_optimization_info": "💡 No optimization results. Please optimize a prompt first.",
        
        # Feedback and revision tab
        "feedback_revision_header": "🔄 Feedback & Revision",
        "current_optimized_prompt": "📝 Current Optimized Prompt",
        "view_current_prompt": "View Current Optimized Prompt",
        "provide_feedback": "💬 Provide Feedback",
        "feedback_placeholder": """Example feedback:
• The prompt seems too complex. Please make it simpler.
• Guidelines for tool usage are lacking.
• The response seems too short. Please request more detailed answers.
• Please specify output in a specific format.
• Please add planning steps.""",
        "feedback_help": "The more specific feedback you provide, the better improvement results you'll get.",
        "feedback_category": "Feedback Category",
        "feedback_type": "Select feedback type",
        "feedback_types": [
            "General Improvements",
            "Clarity Improvement",
            "Specificity Improvement", 
            "Instruction Modification",
            "Agentic Capability Improvement",
            "Format Improvement",
            "Other"
        ],
        "priority": "Priority",
        "priority_options": ["Low", "Medium", "High"],
        "quick_feedback": "Quick Feedback",
        "feedback_complex": "Too Complex",
        "feedback_tools": "Improve Tool Usage",
        "feedback_length": "Adjust Response Length",
        "feedback_planning": "Add Planning",
        "start_feedback_improvement": "🚀 Start Feedback-based Improvement",
        "feedback_required": "⚠️ Please enter feedback.",
        "feedback_complete": "✅ Feedback-based improvement completed!",
        "feedback_error": "❌ An error occurred during feedback-based improvement.",
        "improvement_progress": "🔍 Improvement Progress",
        "feedback_improvement_results": "📊 Feedback-based Improvement Results",
        "applied_changes_count": "Applied Changes",
        "processed_feedback": "Processed Feedback",
        "improvement_score": "Improvement Score",
        "processed_feedback_list": "💬 Processed Feedback",
        "final_improved_prompt": "🎯 Final Improved Prompt",
        "before_after_comparison": "🔄 Before/After Comparison",
        "before_optimization": "**Before (Optimized Prompt)**",
        "after_feedback": "**After (Feedback Applied)**",
        "additional_feedback": "🔄 Provide Additional Feedback",
        "improvement_complete": "✅ Improvement Complete",
        "improvement_finished": "🎉 Prompt improvement completed!",
        "go_to_input": "📝 Go to Prompt Optimization",
        "no_feedback_info": "💡 No optimization results. Please optimize a prompt first in the 'Prompt Input' tab.",
        
        # Progress messages
        "progress_start": "🚀 Starting comprehensive prompt analysis...",
        "progress_clarity": "📋 Analyzing clarity...",
        "progress_specificity": "🎯 Analyzing specificity...",
        "progress_instruction": "📏 Analyzing instruction following...",
        "progress_agentic": "🤖 Analyzing agentic capabilities...",
        "progress_complete": "✅ Optimization complete!",
        
        # Quick feedback texts
        "quick_feedback_complex": "The prompt is too complex. Please make it simpler and clearer.",
        "quick_feedback_tools": "Please add clearer guidelines for tool usage.",
        "quick_feedback_length": "Please improve to provide more detailed and specific responses.",
        "quick_feedback_planning": "Please add step-by-step planning and reflective thinking processes.",
        
        # Additional messages
        "optimizing_prompt": "Optimizing prompt...",
        "improvement_finished_msg": "🎉 Prompt improvement completed!"
    }
} 