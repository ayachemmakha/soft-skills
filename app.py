import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="تطبيق الأعمدة السبعة",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        padding: 20px;
        font-size: 3em;
        font-weight: bold;
    }
    .pilier-card {
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        background: #f8f9fa;
        border-right: 5px solid #2E8B57;
        text-align: right;
    }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px;
    }
    .question-box {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-right: 4px solid #4361ee;
        text-align: right;
    }
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    * {
        font-family: 'Cairo', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Les 35 questions en arabe
QUESTIONS = {
    "النزاهة": [
        "أفعالي تتوافق مع كلامي",
        "أفي بوعودي، حتى تلك التي أقطعها على نفسي",
        "أكون صادقاً في علاقاتي",
        "أعترف بأخطائي",
        "أحترم التزاماتي المهنية/الشخصية"
    ],
    "الحاجات": [
        "أعرف ما أحتاجه لأكون بخير",
        "أجرؤ على التعبير عن حاجاتي للآخرين",
        "أعتني بحاجاتي الجسدية (نوم، تغذية)",
        "أسمح لنفسي بإشباع حاجاتي العاطفية",
        "أعرف كيف أقول 'كفى' عندما أكون متعباً/مشبعاً"
    ],
    "القيم": [
        "أعرف قيمي الرئيسية الثلاث",
        "قراراتي المهمة تحترم قيمي",
        "أختار أشخاصاً يشاركونني قيمي",
        "أفكر بانتظام في أهمية قيمي",
        "أشعر بالفخر عندما أتصرف وفق قيمي"
    ],
    "الإيجابية": [
        "أرى الجانب الجيد في المواقف الصعبة",
        "أمارس الامتنان يومياً",
        "أحدّ من أفكاري السلبية",
        "أحافظ على حديث داخلي لطيف مع نفسي",
        "أشارك الطاقة الإيجابية مع محيطي"
    ],
    "الحدود": [
        "أعرف كيف أقول 'لا' دون أن أبرر نفسي كثيراً",
        "أحمي نفسي من العلاقات السامة",
        "أتواصل بوضوح حول حدودي",
        "أحترم حدودي دون شعور بالذنب",
        "أشعر عندما يتم تجاوز حدودي"
    ],
    "الشبكة": [
        "أشعر بأنني مدعوم من قبل شخصين أو ثلاثة على الأقل",
        "أحافظ بنشاط على علاقاتي المهمة",
        "أعرف كيف أطلب المساعدة عندما أحتاجها",
        "علاقاتي متوازنة (أعطي/أتلقى)",
        "أشعر بأنني محاط بأشخاص يحترمونني"
    ],
    "الحاضر": [
        "ألاحظ عندما يتجول ذهني (في الماضي/المستقبل)",
        "أمارس اليقظة الذهنية في نشاطاتي اليومية",
        "أستمتع باللحظات البسيطة الصغيرة",
        "أتخلى عما لا أستطيع التحكم فيه",
        "أشعر بأنني حاضر بالكامل في تفاعلاتي"
    ]
}

# Emojis et descriptions
PILIERS = {
    "النزاهة": {"emoji": "⚖️", "description": "أن تكون صادقاً مع نفسك"},
    "الحاجات": {"emoji": "💗", "description": "تحديد الاحتياجات الأساسية"},
    "القيم": {"emoji": "🎯", "description": "توضيح ما يهم حقاً"},
    "الإيجابية": {"emoji": "🌞", "description": "تنمية موقف إيجابي"},
    "الحدود": {"emoji": "🛡️", "description": "معرفة كيف تحمي نفسك"},
    "الشبكة": {"emoji": "🤝", "description": "علاقات صحية ومغذية"},
    "الحاضر": {"emoji": "⏳", "description": "عيش اللحظة الحالية"}
}

# Recommandations
RECOMMANDATIONS = {
    "النزاهة": [
        "اكتب وعداً قطعته على نفسك والتزم به هذا الأسبوع",
        "خذ 5 دقائق يومياً للتحقق من تطابق أفعالك مع نواياك"
    ],
    "الحاجات": [
        "حدد حاجة غير مشبعة واتخذ إجراءً للاستجابة لها",
        "مارس التعاطف الذاتي بالاستماع لاحتياجاتك دون حكم"
    ],
    "القيم": [
        "اذكر قيمك الثلاث الرئيسية وعرضها في مكان مرئي",
        "اسأل نفسك قبل أي قرار: 'هل هذا يتوافق مع قيمي؟'"
    ],
    "الإيجابية": [
        "اكتب 3 أشياء تشعر بالامتنان لها كل مساء",
        "استبدل فكرة سلبية بفكرتين إيجابيتين"
    ],
    "الحدود": [
        "تدرب على قول 'لا' لطلب صغير هذا الأسبوع",
        "حدد موقفاً تحتاج فيه لوضع حدود أوضح"
    ],
    "الشبكة": [
        "اتصل بصديق لم تتحدث معه منذ فترة",
        "شارك شيئاً شخصياً مع شخص تثق به"
    ],
    "الحاضر": [
        "مارس دقيقتين من التنفس الواعي يومياً",
        "كل وجبة واحدة بانتباه كامل (بدون هاتف)"
    ]
}

def calculer_scores(reponses):
    """Calcule les scores pour chaque pilier"""
    scores = {}
    for pilier in QUESTIONS.keys():
        if pilier in reponses and reponses[pilier]:
            total = sum(reponses[pilier])
            max_possible = len(reponses[pilier]) * 5
            scores[pilier] = round((total / max_possible) * 100)
    
    if scores:
        scores['المعدل'] = round(sum(scores.values()) / len(scores))
    
    return scores

def afficher_page_accueil():
    """Affiche la page d'accueil"""
    st.markdown('<h1 class="main-header">🌿 تطبيق الأعمدة السبعة</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 1.2em; margin-bottom: 40px;'>
    اكتشف توازنك الشخصي عبر تقييم الأعمدة الأساسية لنموك وتطورك
    </div>
    """, unsafe_allow_html=True)
    
    # Afficher les piliers
    cols = st.columns(3)
    for i, (pilier_key, pilier_info) in enumerate(PILIERS.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='pilier-card'>
                <h2 style='color: #2E8B57;'>{pilier_info['emoji']} {pilier_key}</h2>
                <p>{pilier_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 بدء الاختبار الآن", use_container_width=True, type="primary"):
            st.session_state.page = "test"
            st.rerun()
        
        if st.button("📊 عرض النتائج السابقة", use_container_width=True):
            if 'scores' in st.session_state:
                st.session_state.page = "results"
                st.rerun()
            else:
                st.warning("⚠️ لم تقم بإجراء الاختبار بعد")

def afficher_test():
    """Affiche le questionnaire"""
    st.markdown('<h1 style="text-align: center; color: #2E8B57;">📋 اختبار الأعمدة السبعة</h1>', unsafe_allow_html=True)
    
    # Initialiser les réponses
    if 'reponses' not in st.session_state:
        st.session_state.reponses = {pilier: [0] * 5 for pilier in QUESTIONS.keys()}
    
    if 'current_pilier' not in st.session_state:
        st.session_state.current_pilier = list(QUESTIONS.keys())[0]
        st.session_state.current_question = 0
    
    current_pilier = st.session_state.current_pilier
    current_q = st.session_state.current_question
    
    # Barre de progression
    total_questions = sum(len(q) for q in QUESTIONS.values())
    answered = sum(1 for pilier in QUESTIONS.keys() 
                  for ans in st.session_state.reponses.get(pilier, []) if ans > 0)
    progress = answered / total_questions
    
    st.progress(progress)
    st.caption(f"التقدم: {answered}/{total_questions} سؤال ({int(progress*100)}%)")
    
    st.markdown("---")
    
    # Afficher le pilier courant
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center; background: #f0f9ff; padding: 20px; border-radius: 15px;'>
            <h2>{PILIERS[current_pilier]['emoji']} {current_pilier}</h2>
            <p style='color: #666;'>{PILIERS[current_pilier]['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Question courante
    question_text = QUESTIONS[current_pilier][current_q]
    
    st.markdown(f"""
    <div class='question-box'>
        <h3 style='color: #4361ee;'>السؤال {current_q + 1} من 5:</h3>
        <h2>{question_text}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Options de réponse
    st.subheader("اختر درجة موافقتك:")
    
    labels = ["لا أوافق بشدة", "لا أوافق", "محايد", "أوافق", "أوافق بشدة"]
    
    cols = st.columns(5)
    selected = None
    
    for i, (col, label) in enumerate(zip(cols, labels)):
        with col:
            value = i + 1
            if st.button(f"{value}\n{label}", use_container_width=True, 
                        type="primary" if st.session_state.reponses[current_pilier][current_q] == value else "secondary"):
                st.session_state.reponses[current_pilier][current_q] = value
                selected = value
    
    if selected:
        st.success(f"✓ تم حفظ إجابتك: {selected}")
    
    st.markdown("---")
    
    # Boutons de navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⏮️ السابق", use_container_width=True, disabled=current_q == 0 and current_pilier == list(QUESTIONS.keys())[0]):
            if current_q > 0:
                st.session_state.current_question -= 1
            else:
                pilier_index = list(QUESTIONS.keys()).index(current_pilier)
                if pilier_index > 0:
                    st.session_state.current_pilier = list(QUESTIONS.keys())[pilier_index - 1]
                    st.session_state.current_question = 4
            st.rerun()
    
    with col4:
        next_text = "التالي ⏭️" if not (current_q == 4 and current_pilier == list(QUESTIONS.keys())[-1]) else "إنهاء الاختبار 🎯"
        if st.button(next_text, use_container_width=True, type="primary"):
            if current_q < 4:
                st.session_state.current_question += 1
            else:
                pilier_index = list(QUESTIONS.keys()).index(current_pilier)
                if pilier_index < len(QUESTIONS) - 1:
                    st.session_state.current_pilier = list(QUESTIONS.keys())[pilier_index + 1]
                    st.session_state.current_question = 0
                else:
                    # Fin du test
                    st.session_state.scores = calculer_scores(st.session_state.reponses)
                    st.session_state.test_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.page = "results"
            st.rerun()
    
    with col2:
        if st.button("🏠 الصفحة الرئيسية", use_container_width=True):
            st.session_state.page = "accueil"
            st.rerun()
    
    with col3:
        if st.button("🔄 إعادة تعيين", use_container_width=True):
            st.session_state.reponses = {pilier: [0] * 5 for pilier in QUESTIONS.keys()}
            st.session_state.current_pilier = list(QUESTIONS.keys())[0]
            st.session_state.current_question = 0
            st.success("تم إعادة تعيين الإجابات")
            st.rerun()

def afficher_resultats():
    """Affiche les résultats"""
    if 'scores' not in st.session_state:
        st.error("❌ لم تقم بإجراء الاختبار بعد")
        if st.button("العودة إلى الصفحة الرئيسية"):
            st.session_state.page = "accueil"
            st.rerun()
        return
    
    scores = st.session_state.scores
    date_test = st.session_state.get('test_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    st.markdown('<h1 style="text-align: center; color: #2E8B57;">📊 نتائج الاختبار</h1>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align: center; color: #666; margin-bottom: 30px;'>
    تاريخ الاختبار: {date_test}
    </div>
    """, unsafe_allow_html=True)
    
    # Score global
    score_global = scores.get('المعدل', 0)
    
    if score_global >= 80:
        interpretation = "🌟 ممتاز - واصل العمل الرائع!"
        color = "#10B981"
        rgba_color = "rgba(16, 185, 129, 0.2)"
    elif score_global >= 60:
        interpretation = "✅ جيد - يمكن التحسين"
        color = "#3B82F6"
        rgba_color = "rgba(59, 130, 246, 0.2)"
    elif score_global >= 40:
        interpretation = "⚠️ انتبه - يحتاج للعمل"
        color = "#F59E0B"
        rgba_color = "rgba(245, 158, 11, 0.2)"
    else:
        interpretation = "🔄 أولوية - يحتاج للتعزيز العاجل"
        color = "#EF4444"
        rgba_color = "rgba(239, 68, 68, 0.2)"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class='score-box'>
            <h1 style='font-size: 4em; margin: 0;'>{score_global}%</h1>
            <h3 style='margin: 10px 0;'>{interpretation}</h3>
            <p>المعدل العام</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphique radar CORRIGÉ
    st.subheader("📈 مخطط الأعمدة السبعة")
    
    # Préparer les données pour le graphique
    pilier_scores = {k: v for k, v in scores.items() if k != 'المعدل'}
    
    # Créer un DataFrame pour Plotly
    categories = list(pilier_scores.keys())
    values = list(pilier_scores.values())
    
    # Dupliquer le premier point pour fermer le graphique
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        name='نتائجك',
        line_color=color,
        fillcolor=rgba_color,  # Format RGBA correct
        line_width=3,
        opacity=0.8
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12),
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                tickfont=dict(size=14),
                direction="clockwise",
                rotation=90
            ),
            bgcolor='rgba(248,249,250,0.5)'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Graphique à barres horizontal (alternative)
    st.subheader("📊 تفصيل النتائج")
    
    # Créer un DataFrame pour le graphique à barres
    df_scores = pd.DataFrame({
        'العمود': list(pilier_scores.keys()),
        'النسبة': list(pilier_scores.values()),
        'اللون': [color] * len(pilier_scores)
    })
    
    # Trier par score
    df_scores = df_scores.sort_values('النسبة', ascending=True)
    
    # Créer le graphique à barres
    fig_bar = px.bar(
        df_scores,
        x='النسبة',
        y='العمود',
        orientation='h',
        color='النسبة',
        color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
        range_color=[0, 100],
        text='النسبة',
        title='نتائج الأعمدة السبعة'
    )
    
    fig_bar.update_layout(
        yaxis_title="",
        xaxis_title="النسبة المئوية %",
        showlegend=False,
        height=400,
        xaxis=dict(range=[0, 100]),
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )
    
    fig_bar.update_traces(
        texttemplate='%{text}%',
        textposition='outside',
        marker_line_color='white',
        marker_line_width=2
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Détail des scores avec barres de progression Streamlit
    st.subheader("📋 تفصيل النتائج مع التقدم")
    
    for pilier, score in pilier_scores.items():
        progress = score / 100
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**{PILIERS[pilier]['emoji']} {pilier}**")
            st.markdown(f"**{score}%**")
        with col2:
            st.progress(progress, text=f"{score}%")
        
        # Barre de progression colorée manuelle
        if score >= 80:
            bar_color = "#10B981"
        elif score >= 60:
            bar_color = "#3B82F6"
        elif score >= 40:
            bar_color = "#F59E0B"
        else:
            bar_color = "#EF4444"
            
        st.markdown(f"""
        <div style='width: 100%; background: #e0e0e0; border-radius: 10px; margin: 5px 0 20px 0;'>
            <div style='width: {score}%; background: {bar_color}; height: 20px; border-radius: 10px;'></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recommandations
    st.subheader("🎯 توصيات للتحسين")
    
    # Trouver les piliers les plus faibles
    pilier_scores_sorted = sorted(pilier_scores.items(), key=lambda x: x[1])
    
    for pilier, score in pilier_scores_sorted[:3]:
        if pilier in RECOMMANDATIONS and score < 70:
            with st.expander(f"{PILIERS[pilier]['emoji']} {pilier} ({score}%) - يحتاج تحسين"):
                for i, rec in enumerate(RECOMMANDATIONS[pilier][:2], 1):
                    st.markdown(f"**{i}.** {rec}")
    
    # Ajouter des recommandations générales
    with st.expander("📝 توصيات عامة للجميع"):
        st.markdown("""
        1. **مارس التأمل** لمدة 5 دقائق يومياً
        2. **احتفظ بمفكرة** لكتابة أفكارك وتطورك
        3. **حدد أهدافاً صغيرة** قابلة للتحقيق أسبوعياً
        4. **شارك تجربتك** مع صديق للمساءلة المتبادلة
        5. **كرر هذا الاختبار** كل شهر لتتبع تطورك
        """)
    
    st.markdown("---")
    
    # Actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 إعادة الاختبار", use_container_width=True, type="primary"):
            st.session_state.reponses = {pilier: [0] * 5 for pilier in QUESTIONS.keys()}
            st.session_state.current_pilier = list(QUESTIONS.keys())[0]
            st.session_state.current_question = 0
            st.session_state.page = "test"
            st.rerun()
    
    with col2:
        if st.button("📥 تصدير النتائج", use_container_width=True):
            # Convertir en DataFrame pour téléchargement
            df = pd.DataFrame({
                'العمود': list(pilier_scores.keys()),
                'النسبة المئوية': list(pilier_scores.values()),
                'التاريخ': date_test
            })
            
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="⬇️ تحميل كملف CSV",
                data=csv,
                file_name=f"نتائج_الأعمدة_السبعة_{date_test}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        if st.button("🖨️ طباعة النتائج", use_container_width=True):
            st.info("💡 استخدم Ctrl+P في متصفحك لطباعة هذه الصفحة")
    
    with col4:
        if st.button("🏠 الرئيسية", use_container_width=True):
            st.session_state.page = "accueil"
            st.rerun()

# Gestion des pages
def main():
    # Initialiser l'état de la page
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    # Afficher la page appropriée
    if st.session_state.page == "accueil":
        afficher_page_accueil()
    elif st.session_state.page == "test":
        afficher_test()
    elif st.session_state.page == "results":
        afficher_resultats()

if __name__ == "__main__":
    main()