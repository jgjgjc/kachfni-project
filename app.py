import streamlit as st
import google.generativeai as genai
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="إذاعة صفاقس - كشفني", page_icon="📻", layout="wide")

# تخصيص الألوان (أخضر وأبيض)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #007a3d !important; text-align: right; }
    .stButton > button {
        background-color: #007a3d !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        border: none;
    }
    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #007a3d !important;
        border: 2px solid #007a3d !important;
    }
    .stInfo { background-color: #e6f4ea; color: #007a3d; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- نظام السرية (Secrets) ---
# التأكد من وجود المفتاح في إعدادات Streamlit Cloud
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ خطأ في السرية: مفتاح API غير مضبوط في إعدادات Secrets.")
    st.stop()

# --- واجهة التطبيق ---
st.title("📻 إذاعة صفاقس - منظومة كشفني")
st.markdown("### التكشيف الآلي الذكي للأرشيف السمعي البصري")
st.write("---")

uploaded_file = st.file_uploader("📂 ارفع ملف الصوت أو الفيديو (MP3, MP4, WAV)", type=['mp3', 'wav', 'mp4', 'm4a'])

if uploaded_file:
    st.success(f"تم تحميل الملف: {uploaded_file.name}")
    
    if st.button("🚀 بدء المعالجة والتكشيف"):
        with st.spinner("جاري التحليل واستخراج البيانات..."):
            try:
                # رفع الملف للمعالجة
                temp_file = genai.upload_file(uploaded_file.name)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # البرومبت المتخصص
                prompt = """
                بصفتك خبير أرشفة في إذاعة صفاقس، قم بتحليل هذا الملف بدقة:
                1. استخرج النص الكامل (Transcription) مع الحفاظ على اللهجة.
                2. ميز بين المتحدثين (المذيع، الضيوف) بوضوح.
                3. استخرج أهم 10 كلمات مفتاحية (Descriptors).
                4. أنشئ مستخلصاً (Summary) وافياً للمحتوى باللغة العربية الفصحى.
                نسق النتائج في جداول أو نقاط واضحة.
                """
                
                response = model.generate_content([temp_file, prompt])
                full_result = response.text

                # عرض النتائج
                st.markdown("## 📊 نتائج التكشيف الوثائقي")
                st.markdown(full_result)

                # --- ميزة التصدير لملف Excel ---
                output = BytesIO()
                df = pd.DataFrame({
                    "تاريخ التكشيف": [datetime.now().strftime("%Y-%m-%d")],
                    "اسم الملف": [uploaded_file.name],
                    "مخرجات الذكاء الاصطناعي": [full_result]
                })
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Kachfni_Report')
                
                st.download_button(
                    label="📥 تحميل بطاقة الوصف (Excel)",
                    data=output.getvalue(),
                    file_name=f"Kachfni_Sfax_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")