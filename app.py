import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# 1. إعداد الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/drive/drive.javascript", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Gholoul_Project').sheet1

# 2. وظيفة جلب البيانات
def get_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# 3. واجهة المستخدم العصرية
st.set_page_config(page_title="Dashboard Gholoul", layout="wide")
st.title("🏗️ نظام إدارة مشروع قنطرة - غلولو")

df = get_data()

# عرض مؤشرات الأداء (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي الدالات", len(df))
col2.metric("إجمالي العمالة", df['Effectif'].sum() if not df.empty else 0)

# الرسوم البيانية (Plotly)
if not df.empty:
    st.subheader("📊 تحليل توزيع المراحل")
    fig = px.pie(df, names='Etape', title="نسبة الإنجاز حسب المرحلة")
    st.plotly_chart(fig, use_container_width=True)

# 4. نموذج الإدخال (مع حماية بسيطة)
with st.sidebar:
    st.header("إدارة البيانات")
    poutre_id = st.text_input("ID الدالة (مثال: DP1-01)")
    etape = st.selectbox("المرحلة", ["Coffrage", "Ferraillage", "Coulage", "Décoffrage"])
    effectif = st.number_input("عدد العمال", min_value=0)
    
    if st.button("حفظ البيانات"):
        sheet.append_row([poutre_id, etape, effectif])
        st.success("تم الحفظ بنجاح!")

# 5. عرض الجدول
st.subheader("📋 سجل البيانات الحالي")
st.dataframe(df, use_container_width=True)
