import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ssl
import urllib.request
import io
import time
import random

# [SSL 디버깅 패치] 모든 네트워크 요청 시 인증서 검증 해제
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx)))

# 1. 전역 시스템 환경 및 페이지 테마 설정
st.set_page_config(page_title="비즈뿌리오 광고 효율 대시보드", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
/* 전역 라이트 클린 배경 및 컨테이너 여백 */
.stApp {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}

.block-container { 
    padding-top: 1.5rem !important; 
    padding-bottom: 2.5rem !important; 
    max-width: 1400px;
}

/* 타이포그래피 */
h1 { 
    font-weight: 800 !important; 
    color: #0F172A !important; 
    letter-spacing: -0.03em !important;
    font-size: 2.1rem !important;
}

h3 { 
    font-weight: 700 !important; 
    color: #1E293B !important; 
    margin-top: 1rem !important;
    font-size: 1.25rem !important;
}

h4 {
    font-weight: 700 !important;
    color: #334155 !important;
    margin-bottom: 0.8rem !important;
}

p, label, span {
    color: #475569 !important;
}

/* ---------------- 사이드바 내비게이션 스타일링 ---------------- */
[data-testid="stSidebar"] {
    background-color: #4F46E5 !important;
    border-right: none !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* 사이드바 커스텀 연도 선택 라디오 버튼 (배너/탭 스타일) */
[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    background-color: rgba(255, 255, 255, 0.12);
    padding: 8px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    gap: 10px;
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background-color: transparent;
    padding: 12px 18px;
    border-radius: 12px;
    border: none;
    margin: 0;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 600;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
    background-color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] span {
    color: #4F46E5 !important;
    font-weight: 800 !important;
}

/* ---------------- 메인 화면 UI 요소 ---------------- */
/* 상단 히어로 인사이트 배너 */
.hero-banner {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%) !important;
    border-radius: 20px !important;
    padding: 1.3rem 1.8rem !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1.5rem !important;
    border: 1px solid #FCD34D !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.12) !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.hero-title {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #78350F !important;
    margin: 0 !important;
}

.hero-subtitle {
    font-size: 0.92rem !important;
    color: #92400E !important;
    margin-top: 0.25rem !important;
}

.hero-tag {
    background-color: #4F46E5 !important;
    color: #FFFFFF !important;
    font-size: 0.88rem !important;
    padding: 8px 18px !important;
    border-radius: 20px !important;
    font-weight: 800 !important;
    display: inline-block !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3) !important;
    white-space: nowrap !important;
}

/* 핵심 4대 지표 전용 4열 맞춤 그리드 컨테이너 */
.kpi-board-core {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}

.kpi-card-core {
    border-radius: 20px;
    padding: 1.4rem;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: all 0.2s ease-in-out;
}

.kpi-card-core:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.card-indigo { background-color: #6366F1; color: #FFFFFF; }
.card-emerald { background-color: #10B981; color: #FFFFFF; }
.card-amber { background-color: #F59E0B; color: #FFFFFF; }
.card-cyan { background-color: #06B6D4; color: #FFFFFF; }

.kpi-card-core .kpi-label { 
    font-size: 0.88rem; 
    color: rgba(255, 255, 255, 0.9) !important; 
    font-weight: 700; 
}

.kpi-card-core .kpi-val { 
    font-size: 1.85rem; 
    font-weight: 800; 
    color: #FFFFFF !important; 
    line-height: 1.2; 
    letter-spacing: -0.02em;
}

/* 영업사원 개별 요약 4열 카드 */
.rep-kpi-board {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
    margin-top: 0.8rem;
    margin-bottom: 1.2rem;
}

.rep-kpi-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1rem 0.8rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.rep-kpi-card .kpi-label {
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    color: #64748B !important;
    white-space: nowrap !important;
    margin-bottom: 0.3rem !important;
}

.rep-kpi-val { 
    font-size: 1.22rem !important; 
    font-weight: 800 !important; 
    color: #4F46E5; 
    line-height: 1.2; 
    white-space: nowrap !important;
}

/* 라디오 버튼 커스텀 UI (칩 버튼) */
div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > label {
    display: none;
}

div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div {
    background-color: #F1F5F9;
    padding: 6px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    gap: 8px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
}

div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background-color: #FFFFFF;
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    margin: 0;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 95px;
    text-align: center;
    justify-content: center;
}

div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background-color: #E2E8F0;
}

div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
    background-color: #0F172A !important;
    border-color: #0F172A !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.15);
}

div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] span {
    color: #FFFFFF !important;
    font-weight: 700;
}

/* 데이터 프레임 Custom */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* 버튼 */
.stButton > button {
    background-color: rgba(255, 255, 255, 0.2) !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
}
</style>""", unsafe_allow_html=True)

schema_mapping = {
    '연도': 'str', '월': 'str',
    '전체광고비': 'float', '네이버광고비': 'float', '구글광고비': 'float',
    '리드수': 'float', '리드CPA': 'float', '계약건수': 'float',
    '예상매출': 'float', '신규당월매출': 'float', '신규당월GP': 'float',
    '신규누적매출': 'float', '신규누적GP': 'float',
    '광고비ROAS': 'float'
}
numeric_cols = [col for col, dtype in schema_mapping.items() if dtype == 'float']

# ★ [마케팅 전체 통합 시트 CSV URL]
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSWL4QJl1FZtEc2Jh7ymw9fcC17z-Huu5o0bQMVvEge3l9IZL4T90dWiEGDxwL0QeAPayEBElVmCBjt/pub?gid=972179887&single=true&output=csv"

# ★ [영업사원별 성과 탭 CSV URL]
SHEET_REP_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSWL4QJl1FZtEc2Jh7ymw9fcC17z-Huu5o0bQMVvEge3l9IZL4T90dWiEGDxwL0QeAPayEBElVmCBjt/pub?gid=2140907297&single=true&output=csv"

@st.cache_data(ttl=5)
def load_google_sheet_data(url):
    if not url or url.strip() == "": return None
    cache_buster = f"&_cb={int(time.time())}"
    req = urllib.request.Request(url + cache_buster, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = response.read()
    try:
        return pd.read_csv(io.BytesIO(data), on_bad_lines='skip')
    except:
        return pd.read_csv(io.BytesIO(data), engine='python', on_bad_lines='skip')

try:
    raw_data = load_google_sheet_data(SHEET_CSV_URL)
    raw_data.columns = [str(c).strip().replace(" ", "") for c in raw_data.columns]
    
    for col, dtype in schema_mapping.items():
        if col not in raw_data.columns:
            raw_data[col] = 0.0 if dtype == 'float' else ''
            
    for col in numeric_cols:
        if col != '광고비ROAS':
            raw_data[col] = raw_data[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            raw_data[col] = pd.to_numeric(raw_data[col], errors='coerce').fillna(0.0)

    def smart_parse_roas(val):
        if pd.isna(val) or val == '': return 0.0
        if isinstance(val, str): val = val.replace('%', '').replace(',', '').strip()
        try:
            num = float(val)
            if 0 < num <= 10.0: return num * 100
            return num
        except:
            return 0.0

    raw_data['광고비ROAS'] = raw_data['광고비ROAS'].apply(smart_parse_roas)
    raw_data['연도'] = raw_data['연도'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    
    def format_month_str(val):
        s = str(val).replace('.0', '').strip()
        num_match = pd.Series([s]).str.extract(r'(\d+)')[0].iloc[0]
        if pd.notna(num_match):
            return f"{num_match}월"
        return s

    raw_data['월_num'] = raw_data['월'].astype(str).str.extract(r'(\d+)').astype(float).fillna(0)
    raw_data['월'] = raw_data['월'].apply(format_month_str)
    raw_data = raw_data.sort_values(by=['연도', '월_num'])

    st.sidebar.markdown("### 💼 bizppurio")
    st.sidebar.markdown("<p style='font-size:0.85rem; opacity:0.8;'>광고 & 영업 성과 비교</p>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.2); margin:0.8rem 0 1.2rem 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-weight:700; font-size:0.9rem;'>📅 연도별 성과 분석 선택</p>", unsafe_allow_html=True)

    year_mode = st.sidebar.radio(
        "분석 연도 선택",
        options=["📅 2025년 성과", "📅 2026년 성과", "📊 통합 비교 (YoY)"]
    )
    
    st.sidebar.markdown("<br><hr style='border:none; border-top:1px solid rgba(255,255,255,0.2); margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 데이터 실시간 동기화"):
        st.cache_data.clear()
        st.rerun()

    is_yoy_mode = "통합 비교" in year_mode
    selected_yr = "2025" if "2025년" in year_mode else "2026"

    def calculate_core_metrics(df, target_year):
        df_year = df[df['연도'] == str(target_year)]
        if df_year.empty: return {'spend': 0, 'leads': 0, 'contracts': 0, 'revenue': 0}
        
        spend = df_year['전체광고비'].sum()
        leads = df_year['리드수'].sum()
        contracts = df_year['계약건수'].sum()
        revenue = df_year['신규누적매출'].sum()
        
        return {'spend': spend, 'leads': leads, 'contracts': contracts, 'revenue': revenue}

    if is_yoy_mode:
        m_curr = calculate_core_metrics(raw_data, "2026")
        title_tag = "2026년 기준"
    else:
        m_curr = calculate_core_metrics(raw_data, selected_yr)
        title_tag = f"{selected_yr}년 기준"

    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <div class="hero-title">👋 비즈뿌리오 광고 & 영업 통합 대시보드</div>
            <div class="hero-subtitle">선택하신 [{year_mode}]의 핵심 마케팅 리드, 계약 성사 건수 및 파이프라인 전환 지표입니다.</div>
        </div>
        <div style="text-align:right; flex-shrink: 0; margin-left: 1rem;">
            <div class="hero-tag">{title_tag}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 핵심 4대 지표 KPI 카운터
    core_html = f"""<div class="kpi-board-core">
        <div class="kpi-card-core card-indigo">
            <div class="kpi-label">총 광고비 집행액</div>
            <div class="kpi-val">{m_curr['spend']:,.0f}원</div>
        </div>
        <div class="kpi-card-core card-amber">
            <div class="kpi-label">유입 리드 수</div>
            <div class="kpi-val">{m_curr['leads']:,.0f}건</div>
        </div>
        <div class="kpi-card-core card-emerald">
            <div class="kpi-label">최종 계약 성사 건수</div>
            <div class="kpi-val">{m_curr['contracts']:,.0f}건</div>
        </div>
        <div class="kpi-card-core card-cyan">
            <div class="kpi-label">누적 신규 매출액</div>
            <div class="kpi-val">{m_curr['revenue']:,.0f}원</div>
        </div>
    </div>"""
    st.markdown(core_html, unsafe_allow_html=True)

    st.markdown("### 📊 인바운드 리드 실적")
    col_fin1, col_fin2 = st.columns(2)
    
    df_single = raw_data[raw_data['연도'] == selected_yr]
    
    with col_fin1:
        st.markdown("#### 📈 매출 & 영업이익(GP) 추이")
        if not df_single.empty:
            fig_fin = go.Figure()
            # 만원 단위 변환 (/ 10,000) 및 마우스 오버 툴팁 보완
            fig_fin.add_trace(go.Scatter(
                x=df_single['월'], 
                y=df_single['신규당월매출'] / 10000, 
                name='당월확정매출', 
                line=dict(color='#0284C7', width=3),
                hovertemplate='%{x}: %{y:,.1f}만원<extra></extra>'
            ))
            fig_fin.add_trace(go.Scatter(
                x=df_single['월'], 
                y=df_single['신규당월GP'] / 10000, 
                name='당월GP(이익)', 
                line=dict(color='#059669', width=2.5, dash='dash'),
                hovertemplate='%{x}: %{y:,.1f}만원<extra></extra>'
            ))
            fig_fin.update_layout(
                height=250, margin=dict(t=10, b=10, l=10, r=10), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0F172A'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False), 
                yaxis=dict(tickformat=',.0f', ticksuffix='만원', gridcolor='#E2E8F0')
            )
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.info("선택한 연도의 재무 데이터가 없습니다.")

    with col_fin2:
        st.markdown("#### 🎯 단가 효율성 (CPA) 추이")
        if not df_single.empty:
            df_cpa = df_single.copy()
            df_cpa['리드CPA'] = (df_cpa['전체광고비'] / df_cpa['리드수']).fillna(0)
            df_cpa['계약CPA'] = (df_cpa['전체광고비'] / df_cpa['계약건수']).fillna(0)
            
            fig_cpa = go.Figure()
            fig_cpa.add_trace(go.Scatter(
                x=df_cpa['월'], 
                y=df_cpa['리드CPA'], 
                name='리드CPA', 
                line=dict(color='#D97706', width=2.5),
                hovertemplate='%{x}: %{y:,.0f}원<extra></extra>'
            ))
            fig_cpa.add_trace(go.Scatter(
                x=df_cpa['월'], 
                y=df_cpa['계약CPA'], 
                name='계약CPA', 
                line=dict(color='#DC2626', width=2.5),
                hovertemplate='%{x}: %{y:,.0f}원<extra></extra>'
            ))
            fig_cpa.update_layout(
                height=250, margin=dict(t=10, b=10, l=10, r=10), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0F172A'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False), 
                yaxis=dict(tickformat=',.0f', ticksuffix='원', gridcolor='#E2E8F0')
            )
            st.plotly_chart(fig_cpa, use_container_width=True)
        else:
            st.info("선택한 연도의 CPA 효율 데이터가 없습니다.")

    st.markdown("<hr style='border:none; border-top:2px solid #E2E8F0; margin: 2rem 0;'>", unsafe_allow_html=True)

    st.markdown("### 🧑‍💼 영업 담당자 별 성과 요약")
    st.markdown("<p style='font-size:0.88rem; margin-top:-0.4rem; color:#64748B;'>상단 랭킹 요약 및 개별 영업담당자 이름을 클릭하세요.</p>", unsafe_allow_html=True)

    rep_raw_data = load_google_sheet_data(SHEET_REP_CSV_URL)
    is_real_rep_data = False
    
    if rep_raw_data is not None and not rep_raw_data.empty:
        rep_raw_data.columns = [str(c).strip().replace(" ", "") for c in rep_raw_data.columns]
        req_cols = ['연도', '월', '영업담당자', '할당리드수', '계약건수']
        if all(col in rep_raw_data.columns for col in req_cols):
            df_rep_all = rep_raw_data.copy()
            df_rep_all['연도'] = df_rep_all['연도'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_rep_all['월'] = df_rep_all['월'].apply(format_month_str)
            
            df_rep_all['할당리드수'] = df_rep_all['할당리드수'].astype(str).str.replace(',', '').str.replace('건', '').str.strip()
            df_rep_all['할당리드수'] = pd.to_numeric(df_rep_all['할당리드수'], errors='coerce').fillna(0)
            
            df_rep_all['계약건수'] = df_rep_all['계약건수'].astype(str).str.replace(',', '').str.replace('건', '').str.strip()
            df_rep_all['계약건수'] = pd.to_numeric(df_rep_all['계약건수'], errors='coerce').fillna(0)
            
            # 계약매출액 컬럼 감지 및 자동 처리
            rev_col = [c for c in df_rep_all.columns if '매출' in c]
            if rev_col:
                rev_series = df_rep_all[rev_col[0]].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
                df_rep_all['계약매출액'] = pd.to_numeric(rev_series, errors='coerce').fillna(0)
            else:
                df_rep_all['계약매출액'] = 0.0

            df_rep_all['계약전환율(%)'] = (df_rep_all['계약건수'] / df_rep_all['할당리드수'] * 100).fillna(0).round(1)
            is_real_rep_data = True

    if not is_real_rep_data:
        st.warning("⚠️ 영업사원 구글 시트 데이터를 읽어오는 데 실패했거나 필수 열 제목이 일치하지 않습니다.")
        rep_data = []
        months_list = [f"{m}월" for m in range(1, 13)]
        reps_2025 = ["김성태", "장지윤", "김재현", "한희나", "윤병학", "윤종훈", "김현진", "신응섭", "이호형", "문석현", "안윤정"]
        reps_2026 = ["김성태", "장지윤", "김재현", "한희나", "이혜정", "윤종훈", "김현진", "신응섭", "이호형", "문석현", "안윤정"]
        
        random.seed(42)
        for yr, r_list in [("2025", reps_2025), ("2026", reps_2026)]:
            for rep in r_list:
                for m in months_list:
                    assigned_leads = random.randint(10, 35)
                    closed_contracts = int(assigned_leads * random.uniform(0.10, 0.40))
                    rev = closed_contracts * random.randint(1500000, 3500000)
                    rep_data.append({
                        '연도': yr,
                        '월': m,
                        '영업담당자': rep,
                        '할당리드수': assigned_leads,
                        '계약건수': closed_contracts,
                        '계약매출액': rev,
                        '계약전환율(%)': round((closed_contracts / assigned_leads) * 100, 1)
                    })
        df_rep_all = pd.DataFrame(rep_data)

    if is_yoy_mode:
        df_rep_filtered_year = df_rep_all[df_rep_all['연도'].isin(['2025', '2026'])].copy()
    else:
        df_rep_filtered_year = df_rep_all[df_rep_all['연도'] == selected_yr].copy()

    reps_list = list(df_rep_filtered_year['영업담당자'].unique()) if not df_rep_filtered_year.empty else []

    # 1차 선택: 랭킹 요약 vs 개별 담당자
    view_mode = st.radio(
        "조회 방식 선택",
        options=["📊 전체 영업사원 랭킹 요약", "👤 개별 영업담당자 상세 성과"],
        horizontal=True,
        key="rep_view_mode"
    )

    if view_mode == "👤 개별 영업담당자 상세 성과":
        selected_rep = st.radio(
            "영업담당자 선택",
            options=reps_list,
            horizontal=True,
            key="selected_rep_name"
        )
    else:
        selected_rep = "📊 전체 영업사원 랭킹 요약"

    st.markdown("<br>", unsafe_allow_html=True)

    if selected_rep == "📊 전체 영업사원 랭킹 요약":
        st.markdown(f"##### 🏆 [{year_mode}] 전체 영업사원 성과 순위")
        
        if is_yoy_mode:
            rep_summary = df_rep_filtered_year.groupby(['영업담당자', '연도']).agg({
                '할당리드수': 'sum',
                '계약건수': 'sum'
            }).reset_index()
            rep_summary['계약전환율(%)'] = (rep_summary['계약건수'] / rep_summary['할당리드수'] * 100).fillna(0).round(1)

            fig_rank = px.bar(
                rep_summary, x='영업담당자', y='계약건수', color='연도', barmode='group', text='계약건수',
                title="담당자별 전년 동기 대비 계약 건수 비교 (2025 vs 2026)",
                color_discrete_map={'2025': '#94A3B8', '2026': '#4F46E5'}
            )
            fig_rank.update_traces(textposition='outside')
            fig_rank.update_layout(
                height=320, margin=dict(t=30, b=10, l=10, r=10), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0F172A', family='Inter, sans-serif'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(tickfont=dict(color='#0F172A'), showgrid=False, title=""),
                yaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False, title="")
            )
            st.plotly_chart(fig_rank, use_container_width=True)

            st.dataframe(rep_summary.style.format({'할당리드수': '{:,.0f}건', '계약건수': '{:,.0f}건', '계약전환율(%)': '{:.1f}%'}), use_container_width=True, height=220, hide_index=True)

        else:
            rep_summary = df_rep_filtered_year.groupby('영업담당자').agg({
                '할당리드수': 'sum',
                '계약건수': 'sum'
            }).reset_index()
            rep_summary['계약전환율(%)'] = (rep_summary['계약건수'] / rep_summary['할당리드수'] * 100).fillna(0).round(1)
            rep_summary = rep_summary.sort_values(by='계약건수', ascending=False)

            fig_rank = px.bar(
                rep_summary, x='영업담당자', y='계약건수', text='계약건수',
                title=f"[{selected_yr}년] 담당자별 계약 성사 건수 순위",
                color='계약건수', color_continuous_scale=['#93C5FD', '#1E3A8A']
            )
            fig_rank.update_traces(textposition='outside')
            fig_rank.update_layout(
                height=320, margin=dict(t=30, b=10, l=10, r=10), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0F172A', family='Inter, sans-serif'),
                coloraxis_showscale=True,
                xaxis=dict(tickfont=dict(color='#0F172A'), showgrid=False, title=""),
                yaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False, title="")
            )
            st.plotly_chart(fig_rank, use_container_width=True)

            st.dataframe(rep_summary.style.format({'할당리드수': '{:,.0f}건', '계약건수': '{:,.0f}건', '계약전환율(%)': '{:.1f}%'}), use_container_width=True, height=220, hide_index=True)

    else:
        df_single_rep = df_rep_all[df_rep_all['영업담당자'] == selected_rep].copy()
        st.markdown(f"##### 👤 **[{selected_rep}]** 담당자 성과 보고서")

        if is_yoy_mode:
            tot_25 = df_single_rep[df_single_rep['연도'] == '2025']
            tot_26 = df_single_rep[df_single_rep['연도'] == '2026']

            leads_25 = tot_25['할당리드수'].sum()
            leads_26 = tot_26['할당리드수'].sum()
            contracts_25 = tot_25['계약건수'].sum()
            contracts_26 = tot_26['계약건수'].sum()
            rev_25 = tot_25['계약매출액'].sum()
            rev_26 = tot_26['계약매출액'].sum()
            cvr_25 = (contracts_25 / leads_25 * 100) if leads_25 > 0 else 0
            cvr_26 = (contracts_26 / leads_26 * 100) if leads_26 > 0 else 0

            rep_html = f"""<div class="rep-kpi-board">
                <div class="rep-kpi-card">
                    <div class="kpi-label">총 배정 리드</div>
                    <div class="rep-kpi-val">{leads_25:,.0f}건 ➔ {leads_26:,.0f}건</div>
                </div>
                <div class="rep-kpi-card">
                    <div class="kpi-label">총 계약 성사</div>
                    <div class="rep-kpi-val" style="color:#059669;">{contracts_25:,.0f}건 ➔ {contracts_26:,.0f}건</div>
                </div>
                <div class="rep-kpi-card">
                    <div class="kpi-label">평균 전환율</div>
                    <div class="rep-kpi-val" style="color:#D97706;">{cvr_25:.1f}% ➔ {cvr_26:.1f}%</div>
                </div>
                <div class="rep-kpi-card">
                    <div class="kpi-label">총 계약 매출액</div>
                    <div class="rep-kpi-val" style="color:#2563EB;">{rev_25:,.0f}원 ➔ {rev_26:,.0f}원</div>
                </div>
            </div>"""
            st.markdown(rep_html, unsafe_allow_html=True)

            df_single_rep['월_num'] = df_single_rep['월'].astype(str).str.extract(r'(\d+)').astype(float).fillna(0)
            df_single_rep_sorted = df_single_rep.sort_values(by='월_num')
            
            fig_indiv = px.bar(
                df_single_rep_sorted, x='월', y='계약건수', color='연도', barmode='group', text='계약건수',
                title=f"{selected_rep} 월별 계약 건수 비교 (2025 vs 2026)",
                color_discrete_map={'2025': '#94A3B8', '2026': '#10B981'}
            )
            fig_indiv.update_layout(
                height=280, margin=dict(t=30, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0F172A'),
                xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#E2E8F0')
            )
            st.plotly_chart(fig_indiv, use_container_width=True)

        else:
            df_single_rep_yr = df_single_rep[df_single_rep['연도'] == selected_yr].copy()
            df_single_rep_yr['월_num'] = df_single_rep_yr['월'].astype(str).str.extract(r'(\d+)').astype(float).fillna(0)
            df_single_rep_yr = df_single_rep_yr.sort_values(by='월_num')

            tot_assigned = df_single_rep_yr['할당리드수'].sum()
            tot_closed = df_single_rep_yr['계약건수'].sum()
            tot_rev = df_single_rep_yr['계약매출액'].sum()
            avg_cvr = (tot_closed / tot_assigned * 100) if tot_assigned > 0 else 0.0

            rep_html = f"""<div class="rep-kpi-board">
                <div class="rep-kpi-card">
                    <div class="kpi-label">총 배정 리드</div>
                    <div class="rep-kpi-val">{tot_assigned:,.0f}건</div>
                </div>
                <div class="rep-kpi-card">
                    <div class="kpi-label">총 계약 성사</div>
                    <div class="rep-kpi-val" style="color:#059669;">{tot_closed:,.0f}건</div>
                </div>
                <div class="rep-kpi-card">
                    <div class="kpi-label">평균 전환율</div>
                    <div class="rep-kpi-val" style="color:#D97706;">{avg_cvr:.1f}%</div>
                </div>
                <div class="rep-kpi-card">
                    <div class="kpi-label">총 계약 매출액</div>
                    <div class="rep-kpi-val" style="color:#2563EB;">{tot_rev:,.0f}원</div>
                </div>
            </div>"""
            st.markdown(rep_html, unsafe_allow_html=True)

            fig_indiv = go.Figure()
            fig_indiv.add_trace(go.Bar(x=df_single_rep_yr['월'], y=df_single_rep_yr['할당리드수'], name='할당 리드수', marker_color='#6366F1', opacity=0.85))
            fig_indiv.add_trace(go.Bar(x=df_single_rep_yr['월'], y=df_single_rep_yr['계약건수'], name='계약 성사수', marker_color='#10B981'))
            fig_indiv.add_trace(go.Scatter(x=df_single_rep_yr['월'], y=df_single_rep_yr['계약전환율(%)'], name='전환율(%)', yaxis='y2', line=dict(color='#F59E0B', width=2.5)))
            
            fig_indiv.update_layout(
                title=f"[{selected_yr}년] {selected_rep} 월별 파이프라인 추이",
                height=280, margin=dict(t=30, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0F172A'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False),
                yaxis=dict(title="건수", gridcolor='#E2E8F0'),
                yaxis2=dict(title="전환율(%)", overlaying='y', side='right', showgrid=False, ticksuffix='%')
            )
            st.plotly_chart(fig_indiv, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ 대시보드 구동 중 예외 제어 실패: {str(e)}")