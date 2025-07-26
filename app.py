import streamlit as st
import asyncio
import json
from typing import List, Dict, Any
import time
from prompt_optimizer import (
    optimize_prompt_comprehensive, 
    revise_prompt_with_feedback,
    run_general_agent,
    ChatMessage, 
    Role
)
from language_config import LANGUAGES, TEXTS

# 페이지 설정
st.set_page_config(
    page_title="GPT-4.1 Prompt Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 언어 설정 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'ko'

def get_text(key: str) -> str:
    """현재 선택된 언어에 따른 텍스트 반환"""
    return TEXTS[st.session_state.language].get(key, key)

# 사이드바 설정
st.sidebar.title(get_text("sidebar_title"))
st.sidebar.markdown("---")

# 언어 선택
st.sidebar.subheader(get_text("language_select"))
selected_language = st.sidebar.selectbox(
    "Select Language / 언어 선택",
    options=list(LANGUAGES.keys()),
    index=0 if st.session_state.language == 'ko' else 1,
    key="language_selector"
)

# 언어 변경 시 세션 상태 업데이트
if LANGUAGES[selected_language] != st.session_state.language:
    st.session_state.language = LANGUAGES[selected_language]
    st.rerun()

st.sidebar.markdown("---")

# OpenAI API 설정
st.sidebar.subheader(get_text("openai_settings"))

# API 키 입력
api_key = st.sidebar.text_input(
    get_text("api_key_input"),
    type="password",
    help=get_text("api_key_help")
)

# GPT 모델 선택
gpt_model = st.sidebar.selectbox(
    get_text("model_select"),
    [
        "gpt-4o-mini",
        "gpt-4o", 
        "gpt-4.1",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ],
    index=0,
    help=get_text("model_help")
)

# API 키 상태 표시
if api_key:
    st.sidebar.success(get_text("api_key_set"))
else:
    st.sidebar.warning(get_text("api_key_warning"))

st.sidebar.markdown("---")

# 연락처 정보
st.sidebar.subheader(get_text("contact_info"))
st.sidebar.markdown(get_text("contact_text"))

st.sidebar.markdown("---")

# OpenAI Cookbook 참고 명시
st.sidebar.subheader(get_text("reference_materials"))
st.sidebar.markdown(get_text("reference_text"))

st.sidebar.markdown("---")

# 버전 정보
st.sidebar.caption(get_text("version"))

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
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

def add_progress_message(message: str):
    """진행 상황 메시지 추가"""
    st.session_state.progress_messages.append({
        'timestamp': time.time(),
        'message': message
    })

def highlight_differences(original: str, modified: str):
    """원본과 수정된 텍스트의 차이점을 하이라이트"""
    import difflib
    import html
    import re
    
    # HTML 이스케이핑
    original_escaped = html.escape(original)
    modified_escaped = html.escape(modified)
    
    # 단어 단위로 분할 (더 안전한 방식)
    original_words = re.findall(r'\S+|\s+', original)
    modified_words = re.findall(r'\S+|\s+', modified)
    
    # 차이점 계산
    try:
        diff = list(difflib.unified_diff(original_words, modified_words, lineterm=''))
        
        # 추가된/제거된 단어들 찾기 (공백 제외)
        added_words = [line[1:].strip() for line in diff if line.startswith('+') and not line.startswith('+++') and line[1:].strip()]
        removed_words = [line[1:].strip() for line in diff if line.startswith('-') and not line.startswith('---') and line[1:].strip()]
        
        highlighted_original = original_escaped
        highlighted_modified = modified_escaped
        
        # 수정된 텍스트에서 새로운 내용 하이라이트 (어두운 테마용)
        for word in added_words[:5]:  # 최대 5개까지만
            if word and len(word) > 2:  # 의미 있는 단어만
                word_escaped = html.escape(word)
                highlighted_modified = highlighted_modified.replace(
                    word_escaped, 
                    f"<mark style='background-color: #2d5a27; color: #81c784; padding: 3px 5px; border-radius: 4px; font-weight: bold;'>{word_escaped}</mark>"
                )
        
        # 원본 텍스트에서 제거된 내용 하이라이트 (어두운 테마용)
        for word in removed_words[:5]:  # 최대 5개까지만
            if word and len(word) > 2:  # 의미 있는 단어만
                word_escaped = html.escape(word)
                highlighted_original = highlighted_original.replace(
                    word_escaped, 
                    f"<mark style='background-color: #5c1e1e; color: #ef5350; padding: 3px 5px; border-radius: 4px; font-weight: bold;'>{word_escaped}</mark>"
                )
                
        return highlighted_original, highlighted_modified
        
    except Exception as e:
        # 오류 발생 시 원본 반환
        return original_escaped, modified_escaped

def add_feedback_progress(message: str):
    """피드백 진행 상황 메시지 추가"""
    st.session_state.feedback_progress.append({
        'timestamp': time.time(),
        'message': message
    })

async def run_optimization(prompt: str, prompt_type: str = None, num_candidates: int = 3, api_key: str = None, model: str = "gpt-4o"):
    """비동기 최적화 실행"""
    st.session_state.progress_messages = []
    
    def progress_callback(message: str):
        add_progress_message(message)
        # Streamlit 상태 업데이트를 위한 rerun은 별도 처리
    
    try:
        results = await optimize_prompt_comprehensive(
            prompt=prompt,
            prompt_type=prompt_type,
            num_candidates=num_candidates,
            progress_callback=progress_callback,
            api_key=api_key,
            model=model
        )
        st.session_state.optimization_results = results
        add_progress_message("✅ 최적화 완료!")
        return results
    except Exception as e:
        add_progress_message(f"❌ 오류 발생: {str(e)}")
        return None

async def run_feedback_revision(optimized_prompt: str, user_feedback: str, api_key: str = None, model: str = "gpt-4o"):
    """피드백 기반 프롬프트 개선 실행"""
    st.session_state.feedback_progress = []
    
    def feedback_progress_callback(message: str):
        add_feedback_progress(message)
    
    try:
        results = await revise_prompt_with_feedback(
            optimized_prompt=optimized_prompt,
            user_feedback=user_feedback,
            progress_callback=feedback_progress_callback,
            api_key=api_key,
            model=model
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
st.title(get_text("main_title"))
st.markdown(get_text("main_description"))

# OpenAI Cookbook 참고 명시
st.info(get_text("reference_info"))

# 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    get_text("tab_input"), 
    get_text("tab_progress"), 
    get_text("tab_analysis"), 
    get_text("tab_optimization"),
    get_text("tab_feedback")
])

# 탭 1: 프롬프트 입력
with tab1:
    st.header(get_text("prompt_input_header"))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(get_text("main_prompt"))
        user_prompt = st.text_area(
            get_text("main_prompt"),
            height=300,
            placeholder=get_text("prompt_placeholder"),
            help=get_text("prompt_help")
        )
        
        # 최적화 실행 버튼을 왼쪽 열 하단에 배치
        st.markdown("---")
        if st.button(get_text("start_optimization"), type="primary", use_container_width=True, key="start_optimization_btn"):
            if not api_key:
                st.error(get_text("api_key_required"))
            elif user_prompt.strip():
                # 비동기 최적화 실행
                with st.spinner(get_text("optimizing_prompt")):
                    results = asyncio.run(run_optimization(
                        prompt=user_prompt,
                        prompt_type=selected_type,
                        num_candidates=num_candidates,
                        api_key=api_key,
                        model=gpt_model
                    ))
                
                if results:
                    st.success(get_text("optimization_complete"))
                    st.balloons()
                else:
                    st.error(get_text("optimization_error"))
            else:
                st.error(get_text("prompt_required"))
    
    with col2:
        st.subheader(get_text("prompt_type"))
        
        # 프롬프트 유형 선택 (자동 감지 옵션 포함)
        prompt_type_options = [
            "자동 감지",
            "창의적 글쓰기 (creative_writing)",
            "코드 생성 (code_generation)",
            "질문 답변 (qa)",
            "분석 (analysis)",
            "지시사항 수행 (instruction_following)"
        ]
        
        selected_prompt_type = st.selectbox(
            "프롬프트 유형을 선택하세요",
            prompt_type_options,
            help="프롬프트 유형을 선택하면 해당 유형에 최적화된 전략이 적용됩니다. '자동 감지'를 선택하면 AI가 프롬프트를 분석하여 유형을 판단합니다."
        )
        
        # 선택된 유형을 영어 키로 변환
        prompt_type_map = {
            "자동 감지": None,
            "창의적 글쓰기 (creative_writing)": "creative_writing",
            "코드 생성 (code_generation)": "code_generation",
            "질문 답변 (qa)": "qa",
            "분석 (analysis)": "analysis",
            "지시사항 수행 (instruction_following)": "instruction_following"
        }
        
        selected_type = prompt_type_map.get(selected_prompt_type)
        
        st.markdown("---")
        
        # 프롬프트 후보 생성 개수 설정
        st.subheader("🔄 프롬프트 최적화 전략")
        
        num_candidates = st.slider(
            "생성할 프롬프트 변형 개수",
            min_value=2,
            max_value=5,
            value=3,
            help="더 많은 변형을 생성하면 더 다양한 최적화 옵션을 탐색할 수 있지만, 처리 시간이 늘어납니다."
        )
        
        # 고급 최적화 전략 표시
        with st.expander("📊 최적화 전략 상세"):
            st.info("""
            **프롬프트 최적화 프로세스:**
            
            1. **프롬프트 유형 감지**: AI가 프롬프트의 목적과 특성을 분석
            2. **후보 생성**: 다양한 변형 프롬프트 생성
            3. **평가 및 채점**: 
               - 모순 검사 (Contradiction Check)
               - 형식 검증 (Format Validation)
               - 안전성 검사 (Safety & Bias Check)
               - 관련성 평가 (Relevance Evaluation)
            4. **순위 매기기**: 종합 점수 기반 최적 프롬프트 선택
            5. **최종 최적화**: 선택된 프롬프트 추가 개선
            """)
        
        # 예시 프롬프트 제공
        st.markdown("---")
        st.subheader("💡 예시 프롬프트")
        
        example_prompts = {
            "창의적 글쓰기": "한국의 전통 음식에 대한 흥미로운 이야기를 써주세요. 역사적 배경과 현대적 의미를 포함해주세요.",
            "코드 생성": "Python으로 간단한 할 일 목록 앱을 만들어주세요. 추가, 삭제, 완료 표시 기능이 필요합니다.",
            "질문 답변": "인공지능이 인간의 창의성을 대체할 수 있을까요? 장단점을 분석해주세요.",
            "분석": "최근 5년간 전기차 시장의 성장 추세를 분석하고 향후 전망을 제시해주세요.",
            "지시사항 수행": "다음 텍스트를 요약하고, 핵심 포인트 3가지를 bullet point로 정리해주세요: [텍스트]"
        }
        
        selected_example = st.selectbox(
            "예시 선택",
            ["직접 입력"] + list(example_prompts.keys())
        )
        
        if selected_example != "직접 입력" and st.button("예시 사용", key="use_example"):
            # 예시를 메인 프롬프트 입력란에 설정하는 방법은 
            # Streamlit의 제약으로 인해 세션 상태를 통해 처리해야 함
            st.info(f"선택한 예시: {example_prompts[selected_example]}")
            st.markdown("👆 위 예시를 복사하여 왼쪽 프롬프트 입력란에 붙여넣으세요.")

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
        
        # 프롬프트 유형 감지 결과 표시
        if results.get('type_detection'):
            st.info(f"""
            🔍 **감지된 프롬프트 유형**: {results['detected_type']} 
            (신뢰도: {results['type_detection']['confidence']:.2%})
            """)
        
        # 요약 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "생성된 후보",
                len(results.get('prompt_candidates', [])),
                delta=None
            )
        
        with col2:
            st.metric(
                "예상 개선율",
                f"{results.get('estimated_improvement', 0):.0f}%",
                delta=f"+{results.get('estimated_improvement', 0):.0f}%"
            )
        
        with col3:
            # 최고 점수 표시
            ranking_results = results.get('ranking_results', {})
            if ranking_results and ranking_results.get('ranked_prompts'):
                best_score = ranking_results['ranked_prompts'][0].get('final_score', 0)
                st.metric(
                    "최고 점수",
                    f"{best_score:.2f}",
                    delta=None
                )
            else:
                st.metric("최고 점수", "N/A", delta=None)
        
        with col4:
            changes_made = results.get('optimization_details', {}).get('changes_made', [])
            st.metric(
                "적용된 개선사항",
                len(changes_made),
                delta=f"+{len(changes_made)}"
            )
        
        st.markdown("---")
        
        # 프롬프트 후보 및 평가 결과
        st.subheader("🔄 프롬프트 후보 생성 및 평가")
        
        if results.get('prompt_candidates'):
            # 각 후보의 평가 점수를 표 형태로 표시
            candidate_evaluations = results.get('candidate_evaluations', [])
            
            for idx, (candidate, evaluation) in enumerate(zip(results['prompt_candidates'], candidate_evaluations)):
                with st.expander(f"후보 {idx + 1} - 종합 점수: {evaluation.get('contradiction_score', 0) * 0.3 + evaluation.get('format_score', 0) * 0.3 + evaluation.get('safety_score', 0) * 0.4:.2f}"):
                    # 점수 표시
                    score_col1, score_col2, score_col3 = st.columns(3)
                    with score_col1:
                        st.metric("모순 점수", f"{evaluation.get('contradiction_score', 0):.2f}")
                    with score_col2:
                        st.metric("형식 점수", f"{evaluation.get('format_score', 0):.2f}")
                    with score_col3:
                        st.metric("안전성 점수", f"{evaluation.get('safety_score', 0):.2f}")
                    
                    # 프롬프트 내용
                    st.markdown("**프롬프트 내용:**")
                    st.code(candidate, language='text')
        
        st.markdown("---")
        
        # 순위 결과
        st.subheader("🏆 최적화 순위")
        
        ranking_results = results.get('ranking_results', {})
        if ranking_results and ranking_results.get('ranked_prompts'):
            for rank_info in ranking_results['ranked_prompts'][:3]:  # 상위 3개만 표시
                rank = rank_info.get('rank', 0)
                score = rank_info.get('final_score', 0)
                prompt = rank_info.get('prompt', '')
                
                if rank == 1:
                    st.success(f"🥇 **1위** (점수: {score:.2f})")
                elif rank == 2:
                    st.info(f"🥈 **2위** (점수: {score:.2f})")
                else:
                    st.warning(f"🥉 **3위** (점수: {score:.2f})")
                
                st.code(prompt, language='text')
    else:
        st.info("💡 분석 결과가 없습니다. 먼저 프롬프트를 최적화해주세요.")

# 탭 4: 최적화 결과
with tab4:
    st.header("✨ 최적화 결과")
    
    if st.session_state.optimization_results:
        results = st.session_state.optimization_results
        optimization_details = results.get('optimization_details', {})
        
        # 변경사항 비교 (위로 이동)
        st.subheader("🔄 변경사항 비교")
        
        original_prompt = results.get('original_prompt', '')
        optimized_prompt = results.get('optimized_prompt', '')
        changes_made = optimization_details.get('changes_made', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📝 원본 프롬프트**")
            # Streamlit code 블록 사용 (어두운 배경 자동 적용)
            st.code(original_prompt, language='text', line_numbers=False)
        
        with col2:
            st.markdown("**✨ 최적화된 프롬프트**")
            # Streamlit code 블록 사용 (어두운 배경 자동 적용)
            st.code(optimized_prompt, language='text', line_numbers=False)
        
        # 차이점 하이라이트 섹션
        with st.expander("🔍 차이점 하이라이트 보기 (실험적 기능)"):
            st.info("💡 이 기능은 실험적이며, 복잡한 텍스트에서는 정확하지 않을 수 있습니다.")
            
            try:
                highlighted_original, highlighted_modified = highlight_differences(original_prompt, optimized_prompt)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**원본 (빨간색: 제거됨)**")
                    if highlighted_original != original_prompt:
                        st.markdown(f"""
                        <div style="background-color: #2d3748; border: 1px solid #4a5568; border-radius: 8px; padding: 15px; height: 250px; overflow-y: auto; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; white-space: pre-wrap; color: #e2e8f0; line-height: 1.6; font-size: 13px;">
                        {highlighted_original}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.code(original_prompt, language='text')
                
                with col2:
                    st.markdown("**최적화됨 (초록색: 추가됨)**")
                    if highlighted_modified != optimized_prompt:
                        st.markdown(f"""
                        <div style="background-color: #2d3748; border: 1px solid #4a5568; border-radius: 8px; padding: 15px; height: 250px; overflow-y: auto; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; white-space: pre-wrap; color: #e2e8f0; line-height: 1.6; font-size: 13px;">
                        {highlighted_modified}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.code(optimized_prompt, language='text')
                        
            except Exception as e:
                st.error(f"차이점 분석 중 오류가 발생했습니다: {str(e)}")
                
                # 폴백: 일반 코드 블록으로 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**원본**")
                    st.code(original_prompt, language='text')
                with col2:
                    st.markdown("**최적화됨**")
                    st.code(optimized_prompt, language='text')
        
        # 하이라이트된 변경사항 설명
        if changes_made:
            st.markdown("### 🎯 주요 변경사항")
            for i, change in enumerate(changes_made, 1):
                st.markdown(f"""
                <div style="background-color: #ffeb3b33; padding: 10px; border-left: 4px solid #ffeb3b; margin: 5px 0;">
                    <strong>{i}. ✅ {change}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # 개선사항 요약 (분석결과와 통합)
        st.subheader("📈 종합 분석 및 개선 요약")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.info(f"**예상 성능 개선**: {optimization_details.get('estimated_improvement', 0):.0f}%")
            
        with col2:
            st.success(f"**적용된 개선사항**: {len(changes_made)}개")
            
        with col3:
            # 분석 결과에서 발견된 총 문제 개수
            if hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
                analysis_results = st.session_state.analysis_results
                total_issues = sum(len(result.get('issues', [])) for result in analysis_results.get('analysis_details', []))
                st.warning(f"**해결된 문제**: {total_issues}개")
            else:
                st.info("**분석 정보**: 없음")
        
        # 개선 설명
        improvement_explanation = optimization_details.get('improvement_explanation', '')
        if improvement_explanation:
            st.subheader("💡 개선 설명")
            st.write(improvement_explanation)
        
        st.markdown("---")
        
        # 최종 프롬프트와 버튼들
        st.subheader("📥 최적화된 프롬프트")
        
        # 프롬프트와 버튼을 나란히 배치
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_area(
                "최적화된 프롬프트",
                value=optimized_prompt,
                height=250,
                disabled=False,
                help="이 영역에서 텍스트를 선택하여 복사할 수 있습니다.",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**📋 내보내기**")
            if st.button("📋 복사", use_container_width=True, key="copy_final_prompt"):
                st.success("📝 왼쪽 텍스트를 선택하여 복사하세요!")
            
            st.download_button(
                label="💾 다운로드",
                data=optimized_prompt,
                file_name="optimized_prompt.txt",
                mime="text/plain",
                use_container_width=True
            )

        
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
        if st.button(get_text("new_optimization"), type="secondary", use_container_width=True, key="new_optimization_btn"):
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
            st.subheader(get_text("quick_feedback"))
            if st.button(get_text("feedback_complex"), use_container_width=True, key="quick_complex"):
                st.session_state.quick_feedback = get_text("quick_feedback_complex")
            
            if st.button(get_text("feedback_tools"), use_container_width=True, key="quick_tools"):
                st.session_state.quick_feedback = get_text("quick_feedback_tools")
            
            if st.button(get_text("feedback_length"), use_container_width=True, key="quick_length"):
                st.session_state.quick_feedback = get_text("quick_feedback_length")
            
            if st.button(get_text("feedback_planning"), use_container_width=True, key="quick_planning"):
                st.session_state.quick_feedback = get_text("quick_feedback_planning")
        
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
        if st.button(get_text("start_feedback_improvement"), type="primary", use_container_width=True, key="start_feedback_btn"):
            if not api_key:
                st.error(get_text("api_key_required"))
            elif user_feedback.strip():
                with st.spinner("Analyzing feedback and improving prompt..." if st.session_state.language == 'en' else "피드백을 분석하고 프롬프트를 개선 중..."):
                    
                    # 범용 요청 키워드 감지
                    general_keywords = ["한글", "영어", "korean", "english", "translate", "번역", "변경", "formal", "casual", "shorter", "longer", "정중", "친근", "짧게", "길게", "간단", "자세히"]
                    is_general_request = any(keyword in user_feedback.lower() for keyword in general_keywords)
                    
                    if is_general_request:
                        # 범용 Agent 사용
                        general_results = asyncio.run(run_general_agent(
                            original_prompt=current_prompt,
                            user_feedback=user_feedback,
                            api_key=api_key,
                            model=gpt_model
                        ))
                        
                        if general_results:
                            # 범용 결과를 기존 형식으로 변환
                            st.session_state.revision_results = {
                                "original_optimized_prompt": general_results["original_prompt"],
                                "user_feedback": general_results["user_feedback"],
                                "revised_prompt": general_results["modified_prompt"],
                                "changes_made": general_results["changes_made"],
                                "explanation": general_results["explanation"],
                                "feedback_addressed": [general_results["feedback_addressed"]],
                                "revision_details": {
                                    "changes_made": general_results["changes_made"],
                                    "feedback_addressed": [general_results["feedback_addressed"]]
                                }
                            }
                            st.success(get_text("feedback_complete"))
                            st.balloons()
                        else:
                            st.error(get_text("feedback_error"))
                    else:
                        # 기존 분석 기반 시스템 사용
                        results = asyncio.run(run_feedback_revision(
                            optimized_prompt=current_prompt,
                            user_feedback=user_feedback,
                            api_key=api_key,
                            model=gpt_model
                        ))
                        
                        if results:
                            st.success(get_text("feedback_complete"))
                            st.balloons()
                        else:
                            st.error(get_text("feedback_error"))
            else:
                st.error(get_text("feedback_required"))
        
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
                if st.button("📋 복사", use_container_width=True, key="copy_optimized_prompt"):
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
                if st.button(get_text("additional_feedback"), use_container_width=True, key="additional_feedback_btn"):
                    # 현재 개선된 프롬프트를 새로운 기준으로 설정
                    st.session_state.optimization_results['optimized_prompt'] = revised_prompt
                    st.session_state.revision_results = None
                    st.session_state.feedback_progress = []
                    st.rerun()
            
            with col2:
                if st.button(get_text("improvement_complete"), type="primary", use_container_width=True, key="improvement_complete_btn"):
                    st.success(get_text("improvement_finished_msg"))
                    st.balloons()
        
    else:
        st.info("💡 최적화 결과가 없습니다. 먼저 '프롬프트 입력' 탭에서 프롬프트를 최적화해주세요.")
        
        # 프롬프트 최적화로 이동하는 버튼
        if st.button(get_text("go_to_input"), use_container_width=True, key="go_to_input_btn"):
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