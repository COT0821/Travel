# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
import markdown # 需在 requirements.txt 新增此套件

# 設定頁面配置
st.set_page_config(
    page_title="咖啡咖旅遊趣",
    page_icon="☕",
    layout="wide"
)

# --- 關鍵修復：強制連結開啟新分頁 ---
def make_links_open_in_new_tab(html_str):
    """
    將 HTML 中的所有 <a href="..."> 自動加上 target="_blank"
    解決連結在 Streamlit iframe 中無法開啟或被擋住的問題
    """
    return html_str.replace('<a href=', '<a target="_blank" rel="noopener noreferrer" href=')

# --- CSS 樣式：溫暖咖啡館風格 (強制鎖定配色) ---
st.markdown("""
<style>
    /* 強制全站背景 (無視深色模式) */
    .stApp {
        background-color: #FDFCF0;
    }
    
    /* 強制全站文字顏色 */
    .stApp, .stApp p, .stApp li, .stApp div {
        color: #4B3621; 
    }
    
    /* 標題樣式 */
    .main-header {
        font-family: 'Microsoft JhengHei', sans-serif;
        font-size: 3rem;
        color: #4B3621 !important;
        text-align: center;
        font-weight: bold;
        text-shadow: 1px 1px 0px #D7CCC8;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
    }
    
    .sub-header {
        font-family: 'Microsoft JhengHei', sans-serif;
        text-align: center;
        color: #795548 !important;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: bold;
    }

    /* 分區標題 */
    .region-title {
        color: #FFFFFF !important;
        background-color: #6D4C41;
        padding: 5px 15px;
        border-radius: 15px;
        display: inline-block;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.1);
    }

    /* 一般按鈕 (城市按鈕/收藏按鈕) - 拿鐵餅乾風格 */
    .stButton>button {
        width: 100%;
        height: 60px;
        border-radius: 15px;
        background-color: #D7CCC8;
        color: #3E2723 !important;
        border: 2px solid #FFFFFF;
        font-weight: bold;
        font-size: 18px;
        transition: 0.2s;
        box-shadow: 0 4px 0 #A1887F;
    }
    .stButton>button:hover {
        background-color: #BCAAA4;
        color: #FFF !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 0 #8D6E63;
    }
    .stButton>button:active {
        transform: translateY(2px);
        box-shadow: 0 0 0 #8D6E63;
    }

    /* 下載按鈕特化樣式 - 深焙黑咖啡風格 (與上方按鈕同款，但換色) */
    [data-testid="stDownloadButton"] > button {
        width: 100%;
        height: 60px; /* 高度一致 */
        border-radius: 15px; /* 圓角一致 */
        background-color: #5D4037; /* 深咖啡底色 */
        color: #FFF8E1 !important; /* 淺奶油色字 (強制變色) */
        border: 2px solid #FFFFFF; /* 白框 */
        font-weight: bold;
        font-size: 18px;
        transition: 0.2s;
        box-shadow: 0 4px 0 #3E2723; /* 深色陰影 */
    }
    /* 強制下載按鈕內的文字顏色，避免被全站樣式覆蓋 */
    [data-testid="stDownloadButton"] > button * {
        color: #FFF8E1 !important;
    }
    
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #4E342E;
        color: #FFFFFF !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 0 #271c19;
    }
    [data-testid="stDownloadButton"] > button:active {
        transform: translateY(2px);
        box-shadow: 0 0 0 #271c19;
    }
    
    /* 側邊欄背景 */
    [data-testid="stSidebar"] {
        background-color: #FFF8E1;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #4B3621 !important;
    }
    
    /* --- 結果顯示框 (無框模式) --- */
    .result-container {
        background-color: transparent;
        padding: 20px 40px; 
        border-radius: 0; 
        border: none;
        box-shadow: none;
        color: #3E2723 !important; 
        margin-top: 10px;
    }
    
    /* --- Day 行程標題 (木製招牌風格) --- */
    .result-container h3 {
        color: #FFF8E1 !important;
        background-color: #5D4037 !important;
        padding: 15px 20px;
        border-radius: 10px;
        border: 3px solid #D7CCC8;
        margin-top: 40px !important;
        margin-bottom: 25px !important;
        font-size: 1.6rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        letter-spacing: 1.5px;
    }

    /* 其他標題 */
    .result-container h1, .result-container h2 {
        color: #4E342E !important; 
        margin-top: 0 !important;
    }
    .result-container h4 {
        color: #8D6E63 !important;
        margin-top: 25px !important;
        border-bottom: 1px dashed #BCAAA4;
        padding-bottom: 5px;
    }
    
    /* --- 連結樣式 --- */
    .result-container a {
        color: #D84315 !important;
        text-decoration: underline !important;
        font-weight: bold;
        transition: 0.2s;
    }
    .result-container a:hover {
        background-color: #FFE0B2;
        color: #BF360C !important;
    }
    
    /* --- 交通資訊引用區塊 --- */
    .result-container blockquote {
        background-color: rgba(255, 255, 255, 0.5);
        border-left: 4px solid #8D6E63; 
        padding: 8px 15px;
        font-size: 0.95em;
        color: #222222 !important; 
        margin: 10px 0;
        border-radius: 4px;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# --- 函數區：HTML 生成器 ---
def convert_to_html(markdown_content, title):
    """將 Markdown 轉換為帶有樣式的 HTML"""
    # 1. 轉 HTML
    html_content = markdown.markdown(markdown_content)
    # 2. 強制連結開新視窗
    html_content = make_links_open_in_new_tab(html_content)
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: "Microsoft JhengHei", sans-serif;
                background-color: #FDFCF0;
                padding: 40px;
                margin: 0;
                color: #3E2723;
            }}
            .result-container {{
                max-width: 900px;
                margin: 0 auto;
                background-color: transparent;
                padding: 20px;
                border: none;
            }}
            /* Day 標題 (木製招牌) */
            h3 {{ 
                color: #FFF8E1;
                background-color: #5D4037;
                padding: 15px 20px;
                border-radius: 10px;
                border: 3px solid #D7CCC8;
                margin-top: 40px;
                margin-bottom: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                text-align: center;
                letter-spacing: 1.5px;
            }}
            h1, h2 {{ color: #4E342E; margin-top: 0; }}
            h4 {{ 
                color: #8D6E63; 
                margin-top: 30px; 
                border-bottom: 1px dashed #BCAAA4;
                padding-bottom: 5px;
            }}
            a {{ color: #D84315; text-decoration: underline; font-weight: bold; }}
            a:hover {{ background-color: #FFE0B2; }}
            
            /* 交通資訊 */
            blockquote {{
                background-color: rgba(255, 255, 255, 0.5);
                border-left: 4px solid #8D6E63;
                padding: 8px 15px; 
                margin: 10px 0;
                color: #222222; 
                border-radius: 4px;
                font-size: 0.9em;
            }}
            ul {{ line-height: 1.8; }}
            li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="result-container">
            {html_content}
            <hr style="border: 0; border-top: 1px dashed #A1887F; margin: 40px 0;">
            <p style="text-align: center; font-size: 0.9em; color: #8D6E63;">
                 ☕ 咖啡咖旅遊趣 | 下載時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
            </p>
        </div>
    </body>
    </html>
    """
    return full_html

# --- 初始化 Session State ---
if 'destination' not in st.session_state:
    st.session_state.destination = ""
if 'auto_submit' not in st.session_state:
    st.session_state.auto_submit = False
if 'saved_trips' not in st.session_state:
    st.session_state.saved_trips = [] 
if 'current_result' not in st.session_state:
    st.session_state.current_result = "" 

# 定義按鈕回呼函數
def set_destination(city):
    st.session_state.destination = city
    st.session_state.auto_submit = True

def save_trip():
    if st.session_state.current_result:
        default_title = f"{st.session_state.trip_title_input}" if st.session_state.trip_title_input else f"{st.session_state.destination} 之旅"
        new_trip = {
            "title": default_title,
            "content": st.session_state.current_result,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.saved_trips.insert(0, new_trip)
        st.success(f"✅ 已收藏：{default_title}")

def load_trip(index):
    trip = st.session_state.saved_trips[index]
    st.session_state.current_result = trip['content']
    st.session_state.destination = trip['title']

# --- 側邊欄設定 ---
with st.sidebar:
    st.title("🎒 旅人行囊")
    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        elif "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
        if api_key:
            st.success("✅ 通行證 (Key) 已確認")
        else:
            st.error("⚠️ 未偵測到 API Key")
    except:
        st.info("請在 secrets.toml 設定 API Key")
    
    st.markdown("---")
    st.subheader("🗂️ 我的旅遊收藏")
    if not st.session_state.saved_trips:
        st.caption("尚未收藏任何行程")
    else:
        for i, trip in enumerate(st.session_state.saved_trips):
            if st.button(f"📄 {trip['title']}", key=f"history_{i}", use_container_width=True):
                load_trip(i)
        if st.button("🗑️ 清空所有紀錄"):
            st.session_state.saved_trips = []
            st.rerun()

# --- 主畫面 ---
st.markdown('<div class="main-header">☕ 咖啡咖旅遊趣</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">「一個背包，一杯咖啡，幾首喜歡的歌，一張單程車票以及一顆旅遊的心。」</div>', unsafe_allow_html=True)

# 1. 旅伴與交通設定
st.markdown("##### 🚋 步驟 1：設定你的旅遊規劃")
col1, col2, col3, col4 = st.columns(4)
with col1:
    group_type = st.selectbox("👥 這次與誰同遊?", ["情侶/夫妻", "家庭親子", "好友", "獨旅"])
with col2:
    people_count = st.number_input("🔢 人數", 1, 50, 2)
with col3:
    duration = st.slider("📅 天數", 1, 7, 2)
with col4:
    transport = st.selectbox("🚗 交通", ["開車", "機車", "大眾運輸", "徒步"])

# 2. 旅行願望
st.markdown("##### 📝 步驟 2：寫下你的旅遊期望")
special_requests = st.text_area(
    label="旅行願望",
    label_visibility="collapsed",
    placeholder="例如：我想去安靜的老宅咖啡廳、想吃在地人推薦的排骨飯、晚上想看夜景...",
    height=80
)

st.markdown("---")

# 3. 城市選擇區
st.markdown("##### 📍 步驟 3：點擊城市出發~!")

regions = {
    "北部區域": [("基隆", "🚢"), ("台北", "🏯"), ("新北", "🏮"), ("桃園", "✈️"), ("新竹市", "🎋"), ("新竹縣", "⛰️"), ("宜蘭", "🌾")],
    "中部區域": [("苗栗", "🍓"), ("台中", "☀️"), ("彰化", "🗿"), ("南投", "🍵"), ("雲林", "🎭")],
    "南部區域": [("嘉義市", "🚂"), ("嘉義縣", "🏔️"), ("台南", "⛩️"), ("高雄", "🐉"), ("屏東", "🌴")],
    "東部區域": [("花蓮", "🐋"), ("台東", "🎈")],
    "離島區域": [("澎湖", "🎆"), ("金門", "⚔️"), ("馬祖", "🌊")]
}

for region_name, cities in regions.items():
    st.markdown(f'<div class="region-title">{region_name}</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (city_name, icon) in enumerate(cities):
        col_index = i % 5
        with cols[col_index]:
            st.button(f"{icon} {city_name}", key=f"btn_{city_name}", on_click=set_destination, args=(city_name,), use_container_width=True)

# 手動輸入
with st.expander("🔍 上面沒有你想去的地方？手動輸入"):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        # 修改提示文字，暗示可以輸入國外地點
        manual_dest = st.text_input("輸入地點 (可試試全球城市唷!)", value=st.session_state.destination)
    with col_btn:
        manual_submit = st.button("出發")

# --- AI 邏輯處理 ---
trigger_gen = st.session_state.auto_submit or manual_submit

if trigger_gen:
    final_destination = manual_dest if manual_dest else st.session_state.destination
    st.session_state.auto_submit = False 
    
    if not api_key:
        st.error("❌ 哎呀，找不到通行證 (API Key)。")
    elif not final_destination:
        st.warning("❌ 請先點選一個城市！")
    else:
        try:
            genai.configure(api_key=api_key)
            # --- 關鍵修改：移除 ", Taiwan" 強制後綴，並更新 Role ---
            prompt = f"""
            Role: You are a professional travel planner for "咖啡咖旅遊趣".
            Task: Plan a detailed {duration}-day trip to {final_destination}.
            
            Profile:
            - Group: {group_type}, {people_count} pax
            - Transport: {transport}
            - Requests: {special_requests}
            
            **Critical Requirements:**
            1. **Logistics:** Display travel time/distance in a separate blockquote style.
            2. **Google Maps Links (STRICT):** You MUST provide a Markdown link for EVERY spot and restaurant. 
               Format: `[Spot Name](https://www.google.com/maps/search/?api=1&query=Spot+Name)` 
               (Ensure the query part is the specific name in Traditional Chinese).
            3. **Content Format:** For every spot or restaurant, provide exactly these two bullet points:
               - **INFO/HIGHLIGHT**: A concise introduction or vibe check.
               - **推薦**: Specific photo spots (for attractions) or must-order dishes (for restaurants), referencing popular Google Reviews.
            4. **Pacing & Meal Times (STRICT):** - **Breakfast**: 08:00 - 09:00.
               - **Lunch**: Around 12:00.
               - **Dinner**: Around 18:00.
               - **Density**: Fill gaps with attractions (1.5 - 2 hours per spot). Full day plan until ~20:00.
            5. **Smart Route Logic (CRITICAL):** Group attractions geographically for each day to minimize travel.
            
            **Output Format (Markdown):**
            # ☕ {final_destination}：咖啡咖專屬旅程
            > *"{final_destination} 的美好時光，為您精心沖煮"*

            ### Day 1: [Theme Title]
            
            #### 📍 09:00 [Spot Name](https://www.google.com/maps/search/?api=1&query=Spot+Name)
            * ℹ️ **INFO/HIGHLIGHT**: [Concise description]
            * 🌟 **推薦**: [Must-see spots / Must-eat dishes based on Google Reviews]
            
            > 🚗 **移動前往下一站**: 約 15 分鐘 / 3 公里
            
            #### ☕ 10:30 [Cafe/Spot Name](https://www.google.com/maps/search/?api=1&query=Spot+Name)
            * ℹ️ **INFO/HIGHLIGHT**: [Description]
            * 🌟 **推薦**: [Signature items]
            
            ... (Continue for all days)
            """
            
            with st.spinner(f"☕ 正在沖煮 {final_destination} 的最佳行程..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    st.session_state.current_result = response.text.strip()
                except Exception as e:
                    try:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(prompt)
                        st.session_state.current_result = response.text.strip()
                    except Exception as e2:
                        st.error(f"連線失敗: {e2}")

        except Exception as e:
            st.error(f"設定錯誤: {e}")

# --- 顯示與儲存結果區 ---
if st.session_state.current_result:
    st.markdown("---")
    
    col_name, col_save, col_dl = st.columns([2, 1, 1])
    
    with col_name:
        st.text_input("行程標題 (用於存檔/下載檔名)", 
                     value=f"{st.session_state.destination} 咖啡咖旅遊趣", 
                     key="trip_title_input")
        
    with col_save:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        st.button("❤️ 收藏到側邊欄", on_click=save_trip, type="primary", use_container_width=True)
        
    with col_dl:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        trip_title = st.session_state.trip_title_input if st.session_state.trip_title_input else "MyTrip"
        html_data = convert_to_html(st.session_state.current_result, trip_title)
        
        st.download_button(
            label="📥 下載行程 (網頁版)",
            data=html_data,
            file_name=f"{trip_title}.html",
            mime="text/html",
            use_container_width=True
        )

    # 顯示結果框
    # 1. 轉 HTML
    display_html = markdown.markdown(st.session_state.current_result)
    # 2. 強制連結開新視窗 (這裡也要加，確保網頁上預覽正常)
    display_html = make_links_open_in_new_tab(display_html)
    
    # 3. 組合最終顯示的 HTML
    final_display_html = f"""
    <div class="result-container">
        {display_html}
    </div>
    """
    
    st.markdown(final_display_html, unsafe_allow_html=True)