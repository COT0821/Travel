# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import os
import pandas as pd

# 設定頁面配置
st.set_page_config(
    page_title="咖啡咖旅遊趣",
    page_icon="☕",
    layout="wide"
)

# --- CSS 樣式：溫暖咖啡館風格 ---
st.markdown("""
<style>
    /* 全站背景 - 溫暖拿鐵色 */
    .stApp {
        background-color: #F5EFE6; /* 淺米色 */
    }
    
    /* 標題樣式 - 深焙咖啡色 */
    .main-header {
        font-family: 'Comic Sans MS', 'Microsoft JhengHei', sans-serif;
        font-size: 3rem;
        color: #4B3621; /* 深咖啡 */
        text-align: center;
        font-weight: bold;
        text-shadow: 1px 1px 0px #D7CCC8;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
    }
    
    .sub-header {
        font-family: 'Microsoft JhengHei', sans-serif;
        text-align: center;
        color: #795548; /* 淺咖啡 */
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: bold;
    }

    /* 分區標題樣式 */
    .region-title {
        color: #FFFFFF;
        background-color: #6D4C41; /* 咖啡豆色 */
        padding: 5px 15px;
        border-radius: 15px;
        display: inline-block;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.1);
    }

    /* 城市按鈕優化 - 餅乾風格 */
    .stButton>button {
        width: 100%;
        height: 60px;
        border-radius: 15px;
        background-color: #D7CCC8; /* 奶咖色 */
        color: #3E2723;
        border: 2px solid #FFFFFF;
        font-weight: bold;
        font-size: 18px;
        transition: 0.2s;
        box-shadow: 0 4px 0 #A1887F;
    }
    .stButton>button:hover {
        background-color: #BCAAA4;
        color: #FFF;
        transform: translateY(-2px);
        box-shadow: 0 6px 0 #8D6E63;
    }
    .stButton>button:active {
        transform: translateY(2px);
        box-shadow: 0 0 0 #8D6E63;
    }
    
    /* 側邊欄 */
    [data-testid="stSidebar"] {
        background-color: #FFF8E1; /* 奶油色 */
    }
    
    /* 結果顯示框 - 改為較柔和的咖啡色 (調整處) */
    .result-container {
        background-color: #6D4C41; /* 改成中焙咖啡色 (原本是 #4B3621) */
        padding: 20px 40px 40px 40px; 
        border-radius: 15px; 
        border: 2px solid #8D6E63; /* 邊框也調淺 */
        box-shadow: 0 10px 20px rgba(0,0,0,0.15); 
        color: #F5EFE6; /* 淺米色文字 */
        margin-top: 10px;
    }
    
    /* 強制移除結果框內第一個標題的上方留白，並設定顏色 */
    .result-container h1:first-child, 
    .result-container h2:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #FFF3E0 !important; /* 標題改成亮一點的奶油色 */
    }

    /* 設定結果框內所有標題的顏色 */
    .result-container h1, .result-container h2, .result-container h3, .result-container h4 {
        color: #FFF3E0 !important;
    }
    
    /* 連結樣式優化 - 配合新背景色 */
    .result-container a {
        color: #FFCC80 !important; /* 亮橘黃色 */
        text-decoration: none;
        font-weight: bold;
        border-bottom: 1px dashed #FFCC80;
    }
    .result-container a:hover {
        background-color: #5D4037;
        border-bottom: 2px solid #FFCC80;
    }
    
    /* 強制調整 Markdown 內的 blockquote 樣式 (搭配新背景) */
    blockquote {
        background-color: #4E342E; /* 稍微深一點的底色，做層次感 */
        border-left: 5px solid #FFB74D; /* 亮橘色邊框 */
        padding: 15px;
        font-size: 0.95em;
        color: #EFEBE9; /* 淺灰白文字 */
        margin: 15px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 初始化 Session State ---
if 'destination' not in st.session_state:
    st.session_state.destination = ""
if 'auto_submit' not in st.session_state:
    st.session_state.auto_submit = False

# 定義按鈕回呼函數
def set_destination(city):
    st.session_state.destination = city
    st.session_state.auto_submit = True

# --- 側邊欄設定 ---
with st.sidebar:
    st.title("🎒 旅人行囊")
    
    # API Key 處理
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
    st.caption("設定完成後，請在右側選擇目的地。")

# --- 主畫面 ---
st.markdown('<div class="main-header">☕ 咖啡咖旅遊趣</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">「選個為你專屬設計的城市之旅吧!」</div>', unsafe_allow_html=True)

# 1. 旅伴與交通設定 (基本參數)
st.markdown("##### 🚋 步驟 1：設定你的旅程參數")
col1, col2, col3, col4 = st.columns(4)
with col1:
    group_type = st.selectbox("👥 這次跟誰去？", ["情侶/夫妻", "家庭親子", "好友", "獨旅", "長輩"])
with col2:
    people_count = st.number_input("🔢 人數", 1, 50, 2)
with col3:
    duration = st.slider("📅 天數", 1, 7, 2)
with col4:
    transport = st.selectbox("🚗 交通", ["開車", "機車", "大眾運輸", "徒步"])

# 2. 旅行願望 (移至此處，變成長框備註)
st.markdown("##### 📝 步驟 2：寫下旅行想遇到的~!")
special_requests = st.text_area(
    label="旅行願望", # 隱藏標籤，使用上面的 markdown
    label_visibility="collapsed",
    placeholder="例如：我想去安靜的老宅咖啡廳、想吃在地人推薦的排骨飯、晚上想看夜景...",
    height=80 # 設定高度，讓它看起來像長條備註
)

st.markdown("---")

# 3. 城市選擇區 (圖卡式佈局)
st.markdown("##### 📍 步驟 3：點擊城市出發！")

# 定義城市資料結構 (含 Emoji) - 已拆分東部與離島
regions = {
    "北部區域": [
        ("基隆", "🚢"), ("台北", "🏯"), ("新北", "🏮"), 
        ("桃園", "✈️"), ("新竹市", "🎋"), ("新竹縣", "⛰️"), ("宜蘭", "🌾")
    ],
    "中部區域": [
        ("苗栗", "🍓"), ("台中", "☀️"), ("彰化", "🗿"), 
        ("南投", "🍵"), ("雲林", "🎭")
    ],
    "南部區域": [
        ("嘉義市", "🚂"), ("嘉義縣", "🏔️"), ("台南", "⛩️"), 
        ("高雄", "🐉"), ("屏東", "🌴")
    ],
    "東部區域": [
        ("花蓮", "🐋"), ("台東", "🎈")
    ],
    "離島區域": [
        ("澎湖", "🎆"), ("金門", "⚔️"), ("馬祖", "🌊")
    ]
}

# 迴圈生成按鈕網格
for region_name, cities in regions.items():
    st.markdown(f'<div class="region-title">{region_name}</div>', unsafe_allow_html=True)
    
    # 建立欄位 (每行 5 個按鈕，自動換行)
    cols = st.columns(5)
    for i, (city_name, icon) in enumerate(cities):
        col_index = i % 5
        with cols[col_index]:
            # 按鈕顯示文字：Emoji + 城市名
            btn_label = f"{icon} {city_name}"
            # 按下按鈕後，觸發 set_destination 函數
            st.button(
                btn_label, 
                key=f"btn_{city_name}", 
                on_click=set_destination, 
                args=(city_name,),
                use_container_width=True
            )

# 手動輸入備用 (放在最下面)
with st.expander("🔍 上面沒有你想去的地方？手動輸入"):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        manual_dest = st.text_input("輸入地點", value=st.session_state.destination)
    with col_btn:
        manual_submit = st.button("出發")

# --- AI 邏輯處理 ---
# 觸發條件：按下城市按鈕 (auto_submit=True) 或 手動輸入按鈕
trigger_gen = st.session_state.auto_submit or manual_submit

if trigger_gen:
    # 決定目的地 (手動輸入優先權若被觸發，否則用 session 的值)
    final_destination = manual_dest if manual_dest else st.session_state.destination
    
    # 重置 auto_submit，避免無限重跑，但保留 destination 顯示
    st.session_state.auto_submit = False
    
    if not api_key:
        st.error("❌ 哎呀，找不到通行證 (API Key)，請檢查 secrets.toml 設定。")
    elif not final_destination:
        st.warning("❌ 請先點選一個城市，或輸入目的地喔！")
    else:
        try:
            genai.configure(api_key=api_key)
            # 優化後的 Prompt
            prompt = f"""
            Role: You are a professional travel planner for "咖啡咖旅遊趣" (CoffeeKa Travel).
            Task: Plan a detailed {duration}-day trip to {final_destination}, Taiwan.
            
            Profile:
            - Group: {group_type}, {people_count} people
            - Transport: {transport}
            - Requests: {special_requests}
            
            **Critical Requirements:**
            1. **Granular Planning:** Specific shops, photo spots, hidden gems.
            2. **Logistics (IMPORTANT):** Display travel time/distance in a separate blockquote style, NOT mixed in the bullet list.
            3. **Concise Descriptions:** Short, punchy, <30 words.
            4. **Food:** Specific names and must-eat dishes.
            5. **Google Maps Links:** For EVERY spot/restaurant, provide a link. 
               Format: `[Spot Name](https://www.google.com/maps/search/?api=1&query=Spot+Name)`
               (Ensure the query is the spot name in Traditional Chinese).
            
            **Output Format (Markdown):**
            # ☕ [Creative Title for {final_destination}]
            > *"{final_destination}，咖啡咖的專屬旅程"*

            ### 📅 Day 1: [Theme]
            
            #### 📍 09:00 [Spot Name](https://www.google.com/maps/search/?api=1&query=Spot+Name)
            * 📝 *Intro:* [Short concise description]
            
            > 🚗 **移動前往下一站**: 約 15 分鐘 / 3 公里
            
            #### ☕ 10:00 [Spot/Cafe Name](https://www.google.com/maps/search/?api=1&query=Spot+Name)
            * 📝 *Highlight:* [Short concise description]
            
            ... (Continue for all days)
            """
            
            # 顯示載入動畫
            with st.spinner(f"☕ 正在沖煮 {final_destination} 的最佳行程與地圖連結..."):
                try:
                    # 優先嘗試 gemini-2.5-flash
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    # 移除前後空白，避免空行導致的留白
                    st.session_state.result = response.text.strip()
                except Exception as e:
                    # Fallback 機制
                    try:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(prompt)
                        st.session_state.result = response.text.strip()
                    except Exception as e2:
                        st.error(f"連線失敗: {e2}")

        except Exception as e:
            st.error(f"設定錯誤: {e}")

# --- 顯示結果 ---
if "result" in st.session_state:
    st.markdown("---")
    # 修正顯示方式：分開使用 HTML tag 和 markdown
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown(st.session_state.result) # 讓 Streamlit 解析 markdown
    st.markdown('</div>', unsafe_allow_html=True)