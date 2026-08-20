import streamlit as st
import pandas as pd
import plotly.express as px
import os

# إعداد صفحة التطبيق لتكون عريضة واحترافية
st.set_page_config(
    page_title="نظام إدارة مشروع قنطرة - غلولو",
    page_icon="🏗️",
    layout="wide"
)

# ملف تخزين البيانات المحلي المؤقت
DATA_FILE = "gholoul_data.csv"

# وظيفة تحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # بيانات أولية افتراضية في حال لم يوجد الملف
        df_default = pd.DataFrame(columns=["ID_Poutre", "Type", "Etape", "Effectif", "Date"])
        df_default.to_csv(DATA_FILE, index=False)
        return df_default

# وظيفة حفظ البيانات
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- الشريط الجانبي (Sidebar) لتسجيل الدخول والإدارة ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/constructor.png", width=80)
    st.title("لوحة التحكم")
    
    # حالة تسجيل الدخول
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.subheader("🔑 تسجيل دخول المشرف")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول"):
            if username == "gholoul_admin" and password == "12345":
                st.session_state.authenticated = True
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
    else:
        st.success("👤 مسجل كـ: مشرف الموقع")
        if st.button("تسجيل الخروج"):
            st.session_state.authenticated = False
            st.rerun()
            
        st.markdown("---")
        st.subheader("➕ إضافة دالة جديدة")
        
        with st.form("add_form", clear_on_submit=True):
            poutre_id = st.text_input("معرف الدالة (مثال: DP1-01)")
            p_type = st.selectbox("نوع الدالة", ["DP1", "DP2", "DP3", "DP4", "DP5"])
            etape = st.selectbox("المرحلة", ["Coffrage (كوفراج)", "Ferraillage (تسليح)", "Coulage (صب)", "Décoffrage (فك)"])
            effectif = st.number_input("عدد العمال", min_value=1, max_value=100, value=5)
            date_saisie = st.date_input("التاريخ")
            
            submitted = st.form_submit_button("حفظ وإضافة")
            if submitted:
                if poutre_id:
                    new_row = pd.DataFrame({
                        "ID_Poutre": [poutre_id],
                        "Type": [p_type],
                        "Etape": [etape],
                        "Effectif": [effectif],
                        "Date": [str(date_saisie)]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"تمت إضافة {poutre_id} بنجاح!")
                    st.rerun()
                else:
                    st.warning("الرجاء إدخال معرف الدالة على الأقل.")

# --- الواجهة الرئيسية (Main Dashboard) ---
st.title("🏗️ لوحة متابعة مشروع قنطرة - شركة غلولو")
st.markdown("متابعة لحظية لمراحل الإنجاز وتوزيع العمالة في الموقع.")
st.markdown("---")

if not df.empty:
    # 1. بطاقات المؤشرات الرئيسية (KPIs Cards)
    col1, col2, col3 = st.columns(3)
    
    total_poutres = len(df)
    total_workers = int(df["Effectif"].sum())
    latest_stage = df.iloc[-1]["Etape"] if not df.empty else "N/A"
    
    col1.metric(label="📊 إجمالي السجلات / الدالات", value=total_poutres)
    col2.metric(label="👷 إجمالي العمال المسجلين", value=total_workers)
    col3.metric(label="🔄 آخر مرحلة مسجلة", value=latest_stage)
    
    st.markdown("---")
    
    # 2. الرسوم البيانية العصرية باستخدام Plotly
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 توزيع الدالات حسب المرحلة")
        fig_pie = px.pie(
            df, 
            names='Etape', 
            hole=0.4, 
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("👥 عدد العمال حسب نوع الدالة")
        fig_bar = px.bar(
            df, 
            x='Type', 
            y='Effectif', 
            color='Etape',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # 3. جدول البيانات المفصل
    st.subheader("📋 سجل المتابعة التفصيلي")
    st.dataframe(df, use_container_width=True)
    
    # زر تصفير أو حذف البيانات (اختياري للإدارة)
    if st.session_state.authenticated:
        if st.button("🗑️ مسح جميع البيانات وإعادة تعيين الجدول", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("تم مسح البيانات بنجاح.")
            st.rerun()

else:
    st.info("📌 لا توجد بيانات مسجلة حتى الآن. استخدم الشريط الجانبي لتسجيل الدخول وإضافة أول دالة.")
