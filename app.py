import streamlit as st
import asyncio
import json
from typing import List, Dict, Any
import time
from prompt_optimizer import (
    optimize_prompt_comprehensive, 
    revise_prompt_with_feedback,
    ChatMessage, 
    Role
)

# 페이지 설정
st.set_page_config(
    page_title="GPT-4.1 Prompt Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
st.sidebar.title("🚀 GPT-4.1 Prompt Optimizer")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 GPT-4.1 가이드 기반")
st.sidebar.markdown("""
이 도구는 [OpenAI GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)를 기반으로 합니다.

**주요 개선 영역:**
- 명확성 (Clarity)
- 구체성 (Specificity) 
- 지시사항 준수 (Instruction Following)
- 에이전틱 능력 (Agentic Capabilities)
""")

# 세션 상태 초기화
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None
if 'progress_messages' not in st.session_state:
    st.session_state.progress_messages = []
if 'few_shot_messages' not in st.session_state:
    st.session_state.few_shot_messages = []
if 'revision_results' not in st.session_state:
    st.session_state.revision_results = None
if 'feedback_progress' not in st.session_state:
    st.session_state.feedback_progress = []

def add_progress_message(message: str):
    """진행 상황 메시지 추가"""
    st.session_state.progress_messages.append({
        'timestamp': time.time(),
        'message': message
    })

def add_feedback_progress(message: str):
    """피드백 진행 상황 메시지 추가"""
    st.session_state.feedback_progress.append({
        'timestamp': time.time(),
        'message': message
    })

async def run_optimization(prompt: str, few_shot_messages: List[ChatMessage] = None):
    """비동기 최적화 실행"""
    st.session_state.progress_messages = []
    
    def progress_callback(message: str):
        add_progress_message(message)
        # Streamlit 상태 업데이트를 위한 rerun은 별도 처리
    
    try:
        results = await optimize_prompt_comprehensive(
            prompt=prompt,
            few_shot_messages=few_shot_messages,
            progress_callback=progress_callback
        )
        st.session_state.optimization_results = results
        add_progress_message("✅ 최적화 완료!")
        return results
    except Exception as e:
        add_progress_message(f"❌ 오류 발생: {str(e)}")
        return None

async def run_feedback_revision(optimized_prompt: str, user_feedback: str):
    """피드백 기반 프롬프트 개선 실행"""
    st.session_state.feedback_progress = []
    
    def feedback_progress_callback(message: str):
        add_feedback_progress(message)
    
    try:
        results = await revise_prompt_with_feedback(
            optimized_prompt=optimized_prompt,
            user_feedback=user_feedback,
            progress_callback=feedback_progress_callback
        )
        st.session_state.revision_results = results
        add_feedback_progress("✅ 피드백 기반 개선 완료!")
        return results
    except Exception as e:
        add_feedback_progress(f"❌ 오류 발생: {str(e)}")
        return None

def display_severity_badge(severity: str):
    """심각도 배지 표시"""
    colors = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🔴"
    }
    return f"{colors.get(severity, '⚪')} {severity.upper()}"

def display_category_badge(category: str):
    """카테고리 배지 표시"""
    emoji_map = {
        "clarity": "📋",
        "specificity": "🎯",
        "instruction_following": "📏",
        "agentic_capabilities": "🤖"
    }
    return f"{emoji_map.get(category, '📝')} {category.replace('_', ' ').title()}"

# 메인 애플리케이션
st.title("🚀 GPT-4.1 Prompt Optimizer")
st.markdown("OpenAI GPT-4.1 가이드라인을 기반으로 한 지능형 프롬프트 최적화 도구")

# 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 프롬프트 입력", 
    "🔍 분석 진행", 
    "📊 분석 결과", 
    "✨ 최적화 결과",
    "🔄 피드백 & 리비전"
])

# 탭 1: 프롬프트 입력
with tab1:
    st.header("📝 프롬프트 입력")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("메인 프롬프트")
        user_prompt = st.text_area(
            "최적화할 프롬프트를 입력하세요",
            height=300,
            placeholder="""예시:
Write a blog post about artificial intelligence.

또는

You are a helpful assistant. Help me improve my writing skills.""",
            help="GPT-4.1에 전달할 메인 프롬프트를 입력하세요. 시스템 메시지, 사용자 지시사항 등 모든 형태의 프롬프트가 가능합니다."
        )
    
    with col2:
        st.subheader("프롬프트 유형")
        prompt_type = st.selectbox(
            "프롬프트 유형을 선택하세요",
            [
                "일반 작업",
                "창작 작업", 
                "분석 작업",
                "코딩 작업",
                "에이전틱 워크플로우",
                "교육/학습",
                "기타"
            ]
        )
        
        st.subheader("고급 설정")
        include_agentic = st.checkbox(
            "에이전틱 기능 강화",
            help="GPT-4.1의 에이전틱 워크플로우 기능을 최적화합니다"
        )
        
        optimize_for_tools = st.checkbox(
            "도구 사용 최적화",
            help="함수 호출 및 도구 사용에 최적화합니다"
        )
    
    st.subheader("Few-shot 예제 (선택사항)")
    st.markdown("프롬프트의 성능을 향상시키기 위한 예제를 추가할 수 있습니다.")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("➕ 예제 추가"):
            st.session_state.few_shot_messages.append({
                'role': 'user',
                'content': ''
            })
            st.session_state.few_shot_messages.append({
                'role': 'assistant', 
                'content': ''
            })
    
    with col4:
        if st.button("🗑️ 모든 예제 삭제"):
            st.session_state.few_shot_messages = []
    
    # Few-shot 예제 입력
    if st.session_state.few_shot_messages:
        st.markdown("**Few-shot 예제:**")
        for i in range(0, len(st.session_state.few_shot_messages), 2):
            col_user, col_assistant = st.columns(2)
            
            with col_user:
                st.session_state.few_shot_messages[i]['content'] = st.text_area(
                    f"사용자 메시지 {i//2 + 1}",
                    value=st.session_state.few_shot_messages[i]['content'],
                    key=f"user_{i}",
                    height=100
                )
            
            if i + 1 < len(st.session_state.few_shot_messages):
                with col_assistant:
                    st.session_state.few_shot_messages[i+1]['content'] = st.text_area(
                        f"어시스턴트 응답 {i//2 + 1}",
                        value=st.session_state.few_shot_messages[i+1]['content'],
                        key=f"assistant_{i+1}",
                        height=100
                    )
    
    # 최적화 실행 버튼
    st.markdown("---")
    if st.button("🚀 프롬프트 최적화 시작", type="primary", use_container_width=True):
        if user_prompt.strip():
            # Few-shot 메시지 변환
            few_shot_chat_messages = []
            for msg in st.session_state.few_shot_messages:
                if msg['content'].strip():
                    few_shot_chat_messages.append(
                        ChatMessage(role=Role(msg['role']), content=msg['content'])
                    )
            
            # 비동기 최적화 실행
            with st.spinner("프롬프트 최적화 중..."):
                results = asyncio.run(run_optimization(
                    prompt=user_prompt,
                    few_shot_messages=few_shot_chat_messages if few_shot_chat_messages else None
                ))
            
            if results:
                st.success("✅ 최적화가 완료되었습니다! '분석 결과' 탭에서 확인하세요.")
                st.balloons()
            else:
                st.error("❌ 최적화 중 오류가 발생했습니다.")
        else:
            st.error("⚠️ 프롬프트를 입력해주세요.")

# 탭 2: 분석 진행
with tab2:
    st.header("🔍 분석 진행 상황")
    
    if st.session_state.progress_messages:
        st.subheader("실시간 진행 상황")
        
        # 진행 상황 컨테이너
        progress_container = st.container()
        
        with progress_container:
            for i, msg in enumerate(st.session_state.progress_messages):
                timestamp = time.strftime("%H:%M:%S", time.localtime(msg['timestamp']))
                st.write(f"`{timestamp}` {msg['message']}")
        
        # 진행률 계산 (대략적)
        total_steps = 8  # 예상 총 단계
        current_step = len(st.session_state.progress_messages)
        progress = min(current_step / total_steps, 1.0)
        
        st.progress(progress)
        st.caption(f"진행률: {progress * 100:.0f}%")
        
        # 자동 새로고침
        if progress < 1.0:
            time.sleep(1)
            st.rerun()
    else:
        st.info("💡 '프롬프트 입력' 탭에서 최적화를 시작하세요.")
        
        # 샘플 진행 상황 표시
        st.subheader("예상 분석 단계")
        sample_steps = [
            "🚀 종합적 프롬프트 분석 시작...",
            "🔍 Agent 'clarity_checker' 실행 중...",
            "📋 명확성 분석 중...",
            "✅ 명확성 분석 완료",
            "🎯 구체성 분석 중...",
            "✅ 구체성 분석 완료",
            "📏 지시사항 준수 분석 중...",
            "✅ 지시사항 준수 분석 완료",
            "🤖 에이전틱 능력 분석 중...",
            "✅ 에이전틱 능력 분석 완료",
            "📊 분석 완료: 총 문제 집계",
            "✏️ 프롬프트 최적화 중...",
            "✅ 프롬프트 최적화 완료",
            "✅ 최적화 완료!"
        ]
        
        for step in sample_steps:
            st.text(step)

# 탭 3: 분석 결과
with tab3:
    st.header("📊 분석 결과")
    
    if st.session_state.optimization_results:
        results = st.session_state.optimization_results
        
        # 요약 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "발견된 문제",
                results.get('total_issues_found', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "예상 개선율",
                f"{results.get('estimated_improvement', 0):.0f}%",
                delta=f"+{results.get('estimated_improvement', 0):.0f}%"
            )
        
        with col3:
            analysis_results = results.get('analysis_results', [])
            high_severity = sum(1 for r in analysis_results if r.get('severity') == 'high')
            st.metric(
                "고위험 문제",
                high_severity,
                delta=f"-{high_severity}" if high_severity > 0 else None
            )
        
        with col4:
            changes_made = results.get('optimization_details', {}).get('changes_made', [])
            st.metric(
                "적용된 개선사항",
                len(changes_made),
                delta=f"+{len(changes_made)}"
            )
        
        st.markdown("---")
        
        # 상세 분석 결과
        st.subheader("🔍 상세 분석 결과")
        
        for i, analysis in enumerate(analysis_results):
            category = analysis.get('category', 'general')
            severity = analysis.get('severity', 'medium')
            issues = analysis.get('issues', [])
            
            if issues:
                with st.expander(f"{display_category_badge(category)} - {display_severity_badge(severity)} ({len(issues)}개 문제)"):
                    for j, issue in enumerate(issues, 1):
                        st.write(f"{j}. {issue}")
            else:
                st.success(f"{display_category_badge(category)} - 문제 없음 ✅")
        
        # 원본 프롬프트 표시
        st.subheader("📝 원본 프롬프트")
        with st.expander("원본 프롬프트 보기"):
            st.code(results.get('original_prompt', ''), language='text')
    
    else:
        st.info("💡 분석 결과가 없습니다. 먼저 프롬프트를 최적화해주세요.")

# 탭 4: 최적화 결과
with tab4:
    st.header("✨ 최적화 결과")
    
    if st.session_state.optimization_results:
        results = st.session_state.optimization_results
        optimization_details = results.get('optimization_details', {})
        
        # 개선사항 요약
        st.subheader("📈 개선사항 요약")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info(f"**예상 성능 개선**: {optimization_details.get('estimated_improvement', 0):.0f}%")
            
        with col2:
            changes_made = optimization_details.get('changes_made', [])
            st.success(f"**적용된 개선사항**: {len(changes_made)}개")
        
        # 적용된 변경사항
        if changes_made:
            st.subheader("🔧 적용된 변경사항")
            for i, change in enumerate(changes_made, 1):
                st.write(f"{i}. ✅ {change}")
        
        # 개선 설명
        improvement_explanation = optimization_details.get('improvement_explanation', '')
        if improvement_explanation:
            st.subheader("💡 개선 설명")
            st.write(improvement_explanation)
        
        st.markdown("---")
        
        # 최적화된 프롬프트
        st.subheader("🎯 최적화된 프롬프트")
        optimized_prompt = results.get('optimized_prompt', '')
        
        # 복사 버튼과 함께 표시
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_area(
                "최적화된 프롬프트",
                value=optimized_prompt,
                height=300,
                disabled=True
            )
        
        with col2:
            if st.button("📋 복사", use_container_width=True):
                st.write("클립보드 복사는 브라우저에서 직접 수행해주세요.")
            
            # 다운로드 버튼
            st.download_button(
                label="💾 다운로드",
                data=optimized_prompt,
                file_name="optimized_prompt.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # 비교 보기
        st.subheader("🔄 변경사항 비교")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**원본 프롬프트**")
            st.code(results.get('original_prompt', ''), language='text')
        
        with col2:
            st.markdown("**최적화된 프롬프트**")
            st.code(optimized_prompt, language='text')
        
        # Few-shot 예제 최적화 (있는 경우)
        optimized_messages = results.get('optimized_messages', [])
        if optimized_messages:
            st.subheader("💬 최적화된 Few-shot 예제")
            
            for i, msg in enumerate(optimized_messages):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                if role == 'user':
                    st.markdown(f"**사용자 {i//2 + 1}:**")
                    st.info(content)
                elif role == 'assistant':
                    st.markdown(f"**어시스턴트 {(i+1)//2}:**")
                    st.success(content)
        
        # 재시작 버튼
        st.markdown("---")
        if st.button("🔄 새로운 프롬프트 최적화", type="secondary", use_container_width=True):
            st.session_state.optimization_results = None
            st.session_state.progress_messages = []
            st.session_state.few_shot_messages = []
            st.rerun()
    
    else:
        st.info("💡 최적화 결과가 없습니다. 먼저 프롬프트를 최적화해주세요.")

# 탭 5: 피드백 & 리비전
with tab5:
    st.header("🔄 피드백 & 리비전")
    
    if st.session_state.optimization_results:
        # 현재 최적화된 프롬프트 표시
        st.subheader("📝 현재 최적화된 프롬프트")
        current_prompt = st.session_state.optimization_results.get('optimized_prompt', '')
        
        with st.expander("현재 최적화된 프롬프트 보기", expanded=False):
            st.code(current_prompt, language='text')
        
        st.markdown("---")
        
        # 피드백 입력 섹션
        st.subheader("💬 피드백 제공")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_feedback = st.text_area(
                "최적화된 프롬프트에 대한 피드백을 작성해주세요",
                height=150,
                placeholder="""예시 피드백:
• 프롬프트가 너무 복잡해 보입니다. 더 간단하게 만들어주세요.
• 도구 사용에 대한 지침이 부족합니다.
• 응답이 너무 짧을 것 같습니다. 더 상세한 답변을 요구해주세요.
• 특정 형식으로 출력하도록 명시해주세요.
• 계획 수립 단계를 추가해주세요.""",
                help="구체적인 피드백을 제공할수록 더 나은 개선 결과를 얻을 수 있습니다."
            )
        
        with col2:
            st.subheader("피드백 카테고리")
            feedback_category = st.selectbox(
                "피드백 유형을 선택하세요",
                [
                    "일반적인 개선사항",
                    "명확성 개선",
                    "구체성 개선", 
                    "지시사항 수정",
                    "에이전틱 능력 개선",
                    "형식 개선",
                    "기타"
                ]
            )
            
            feedback_priority = st.selectbox(
                "우선순위",
                ["낮음", "보통", "높음"]
            )
            
            # 피드백 예시 버튼들
            st.subheader("빠른 피드백")
            if st.button("너무 복잡함", use_container_width=True):
                st.session_state.quick_feedback = "프롬프트가 너무 복잡합니다. 더 간단하고 명확하게 만들어주세요."
            
            if st.button("도구 사용 개선", use_container_width=True):
                st.session_state.quick_feedback = "도구 사용에 대한 더 명확한 지침을 추가해주세요."
            
            if st.button("응답 길이 조정", use_container_width=True):
                st.session_state.quick_feedback = "더 상세하고 구체적인 응답을 제공하도록 개선해주세요."
            
            if st.button("계획 수립 추가", use_container_width=True):
                st.session_state.quick_feedback = "단계별 계획 수립 및 반성적 사고 과정을 추가해주세요."
        
        # 빠른 피드백이 선택된 경우 자동 입력
        if 'quick_feedback' in st.session_state and st.session_state.quick_feedback:
            user_feedback = st.text_area(
                "최적화된 프롬프트에 대한 피드백을 작성해주세요",
                value=st.session_state.quick_feedback,
                height=150,
                key="feedback_with_quick"
            )
            st.session_state.quick_feedback = None  # 초기화
        
        # 피드백 기반 개선 실행
        if st.button("🚀 피드백 기반 개선 시작", type="primary", use_container_width=True):
            if user_feedback.strip():
                with st.spinner("피드백을 분석하고 프롬프트를 개선 중..."):
                    results = asyncio.run(run_feedback_revision(
                        optimized_prompt=current_prompt,
                        user_feedback=user_feedback
                    ))
                
                if results:
                    st.success("✅ 피드백 기반 개선이 완료되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 피드백 기반 개선 중 오류가 발생했습니다.")
            else:
                st.error("⚠️ 피드백을 입력해주세요.")
        
        # 진행 상황 표시
        if st.session_state.feedback_progress:
            st.subheader("🔍 개선 진행 상황")
            
            with st.container():
                for msg in st.session_state.feedback_progress:
                    timestamp = time.strftime("%H:%M:%S", time.localtime(msg['timestamp']))
                    st.write(f"`{timestamp}` {msg['message']}")
        
        # 리비전 결과 표시
        if st.session_state.revision_results:
            st.markdown("---")
            st.subheader("📊 피드백 기반 개선 결과")
            
            # 개선 요약
            col1, col2, col3 = st.columns(3)
            
            revision_details = st.session_state.revision_results.get('revision_details', {})
            changes_made = revision_details.get('changes_made', [])
            feedback_addressed = revision_details.get('feedback_addressed', [])
            
            with col1:
                st.metric("적용된 변경사항", len(changes_made))
            
            with col2:
                st.metric("처리된 피드백", len(feedback_addressed))
            
            with col3:
                # 개선도 계산 (변경사항 수 기반)
                improvement_score = min(len(changes_made) * 20, 100)
                st.metric("개선 점수", f"{improvement_score}%")
            
            # 적용된 변경사항
            if changes_made:
                st.subheader("🔧 적용된 변경사항")
                for i, change in enumerate(changes_made, 1):
                    st.write(f"{i}. ✅ {change}")
            
            # 처리된 피드백
            if feedback_addressed:
                st.subheader("💬 처리된 피드백")
                for i, feedback in enumerate(feedback_addressed, 1):
                    st.write(f"{i}. 📝 {feedback}")
            
            # 개선 설명
            improvement_explanation = revision_details.get('improvement_explanation', '')
            if improvement_explanation:
                st.subheader("💡 개선 설명")
                st.info(improvement_explanation)
            
            # 최종 개선된 프롬프트
            st.subheader("🎯 최종 개선된 프롬프트")
            revised_prompt = st.session_state.revision_results.get('revised_prompt', '')
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.text_area(
                    "최종 개선된 프롬프트",
                    value=revised_prompt,
                    height=300,
                    disabled=True
                )
            
            with col2:
                if st.button("📋 복사", use_container_width=True):
                    st.write("클립보드 복사는 브라우저에서 직접 수행해주세요.")
                
                st.download_button(
                    label="💾 다운로드",
                    data=revised_prompt,
                    file_name="revised_prompt.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            # Before/After 비교
            st.subheader("🔄 개선 전후 비교")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**개선 전 (최적화된 프롬프트)**")
                st.code(current_prompt, language='text')
            
            with col2:
                st.markdown("**개선 후 (피드백 반영)**")
                st.code(revised_prompt, language='text')
            
            # 추가 피드백 버튼
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 추가 피드백 제공", use_container_width=True):
                    # 현재 개선된 프롬프트를 새로운 기준으로 설정
                    st.session_state.optimization_results['optimized_prompt'] = revised_prompt
                    st.session_state.revision_results = None
                    st.session_state.feedback_progress = []
                    st.rerun()
            
            with col2:
                if st.button("✅ 개선 완료", type="primary", use_container_width=True):
                    st.success("🎉 프롬프트 개선이 완료되었습니다!")
                    st.balloons()
        
    else:
        st.info("💡 최적화 결과가 없습니다. 먼저 '프롬프트 입력' 탭에서 프롬프트를 최적화해주세요.")
        
        # 프롬프트 최적화로 이동하는 버튼
        if st.button("📝 프롬프트 최적화하러 가기", use_container_width=True):
            st.switch_page("프롬프트 입력")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🚀 GPT-4.1 Prompt Optimizer | 
    <a href='https://cookbook.openai.com/examples/gpt4-1_prompting_guide' target='_blank'>OpenAI GPT-4.1 Guide</a> 기반
    </p>
</div>
""", unsafe_allow_html=True) 