import streamlit as st
import pandas as pd
import datetime
import os
from tcm_data import TCM_QUESTIONS, CONSTITUTION_TYPES, HEALTH_ADVICE
from diagnosis_engine import DiagnosisEngine
from database import save_diagnosis_result, get_diagnosis_history, get_diagnosis_stats

# ページ設定
st.set_page_config(
    page_title="東洋医学体質診断アプリ",
    page_icon="🏥",
    layout="wide"
)

# セッション状態の初期化
if 'diagnosis_complete' not in st.session_state:
    st.session_state.diagnosis_complete = False
if 'user_responses' not in st.session_state:
    st.session_state.user_responses = {}
if 'diagnosis_result' not in st.session_state:
    st.session_state.diagnosis_result = None

def save_result_to_database(user_data, diagnosis_result, responses):
    """診断結果をデータベースに保存"""
    try:
        result = save_diagnosis_result(user_data, diagnosis_result, responses)
        return True
    except Exception as e:
        st.error(f"結果の保存に失敗しました: {str(e)}")
        return False

def main():
    st.title("🏥 東洋医学体質診断アプリ")
    st.markdown("---")
    
    # サイドバーで説明
    with st.sidebar:
        st.header("📖 診断について")
        st.write("""
        この診断は東洋医学の考え方に基づいて、
        あなたの体質タイプを判定し、
        個別の養生アドバイスを提供します。
        
        **診断できる体質タイプ：**
        - 気虚（ききょ）
        - 気滞（きたい）
        - 水滞（すいたい）
        - 血虚（けっきょ）
        - 瘀血（おけつ）
        """)
    
    # 診断が完了していない場合は質問を表示
    if not st.session_state.diagnosis_complete:
        st.header("📋 体質診断質問票")
        st.write("以下の質問に答えて、あなたの体質を診断しましょう。")
        
        # 基本情報の入力
        st.subheader("基本情報")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.selectbox("年齢", ["20歳未満", "20-29歳", "30-39歳", "40-49歳", "50-59歳", "60歳以上"], index=3)
        with col2:
            gender = st.selectbox("性別", ["男性", "女性", "その他"], index=1)
        
        st.markdown("---")
        
        # 質問票
        st.subheader("体調に関する質問")
        st.write("以下の質問にお答えください。該当する場合は詳細な症状もお聞きします。")
        
        responses = {}
        
        for i, question_data in enumerate(TCM_QUESTIONS):
            st.write(f"**質問 {i+1}: {question_data['question']}**")
            
            # 自由記述の質問かどうかチェック
            if question_data.get('type') == 'free_text':
                response = st.text_area(
                    f"質問{i+1}の回答",
                    placeholder=question_data.get('placeholder', ''),
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                responses[f"question_{i}"] = response
                responses[f"question_{i}_question"] = question_data['question']
            else:
                # 通常の選択肢質問
                response = st.radio(
                    f"質問{i+1}の回答",
                    question_data['options'],
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                responses[f"question_{i}"] = response
                responses[f"question_{i}_question"] = question_data['question']
                
                # フォローアップ質問がある場合
                if response == "はい" and 'follow_up_questions' in question_data:
                    st.write("　　↓ 詳細をお聞かせください（複数選択可）")
                    for j, follow_up in enumerate(question_data['follow_up_questions']):
                        st.write(f"**{follow_up['question']}**")
                        
                        # 複数選択可能なチェックボックス
                        selected_options = []
                        for k, option in enumerate(follow_up['options']):
                            if st.checkbox(
                                option,
                                key=f"q_{i}_follow_{j}_option_{k}",
                                value=False
                            ):
                                selected_options.append(option)
                        
                        # 選択された項目を保存（複数の場合はカンマ区切り）
                        if selected_options:
                            responses[f"question_{i}_follow_up_{j}"] = ", ".join(selected_options)
                        else:
                            responses[f"question_{i}_follow_up_{j}"] = "どれも当てはまらない"
        
        # 診断ボタン
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 体質診断を実行", type="primary", use_container_width=True):
                # 必須質問に回答されているかチェック
                required_questions = [i for i, q in enumerate(TCM_QUESTIONS) if q.get('type') != 'free_text']
                answered_questions = [i for i in range(len(TCM_QUESTIONS)) if f"question_{i}" in responses and responses[f"question_{i}"].strip()]
                
                if len(answered_questions) >= len(required_questions):
                    # 診断エンジンで結果を計算
                    engine = DiagnosisEngine()
                    diagnosis_result = engine.diagnose(responses)
                    
                    # セッション状態を更新
                    st.session_state.user_responses = responses
                    st.session_state.diagnosis_result = diagnosis_result
                    st.session_state.diagnosis_complete = True
                    
                    # 結果をデータベースに保存
                    user_data = {'age': age, 'gender': gender}
                    save_result_to_database(user_data, diagnosis_result, responses)
                    
                    st.rerun()
                else:
                    st.error("すべての質問にお答えください。")
    
    # 診断結果の表示
    else:
        result = st.session_state.diagnosis_result
        
        st.header("🎯 診断結果")
        
        # 結果のメイン表示
        st.success(f"**あなたの体質タイプ: {result['constitution_type']}**")
        

        
        st.markdown("---")
        
        # AI風のアドバイス表示
        st.header("🤖 AIからの個別アドバイス")
        
        constitution = result['constitution_type']
        if constitution in HEALTH_ADVICE:
            advice = HEALTH_ADVICE[constitution]
            
            # 体質の説明
            st.subheader("💡 あなたの体質について")
            st.info(advice['description'])
            
            # 今日の養生アドバイス
            st.subheader("🌸 今日の養生アドバイス")
            for tip in advice['daily_tips']:
                st.write(f"• {tip}")
            
            # 食事のアドバイス
            st.subheader("🍽️ 食事のアドバイス")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**おすすめ食材：**")
                for food in advice['recommended_foods']:
                    st.write(f"✅ {food}")
            
            with col2:
                st.write("**控えめにする食材：**")
                for food in advice['foods_to_avoid']:
                    st.write(f"❌ {food}")
            
            # 生活習慣のアドバイス
            st.subheader("🏃‍♀️ 生活習慣のアドバイス")
            for habit in advice['lifestyle_tips']:
                st.write(f"• {habit}")
        
        st.markdown("---")
        
        # 再診断ボタン
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 再度診断する", type="secondary", use_container_width=True):
                # セッション状態をリセット
                st.session_state.diagnosis_complete = False
                st.session_state.user_responses = {}
                st.session_state.diagnosis_result = None
                st.rerun()
        
        # 診断履歴の表示（管理者向け）
        if st.checkbox("📊 診断履歴を表示（管理者向け）"):
            try:
                # 統計情報の表示
                stats = get_diagnosis_stats()
                
                st.subheader("📈 5つの体質タイプ別集計")
                
                # 体質タイプ別統計のグラフ
                if stats['constitution_stats']:
                    constitution_df = pd.DataFrame([
                        {'体質タイプ': c.constitution_type, '件数': c.count} 
                        for c in stats['constitution_stats']
                    ])
                    st.bar_chart(constitution_df.set_index('体質タイプ'))
                    
                    # 体質タイプ別の詳細表示
                    st.subheader("詳細集計")
                    for stat in stats['constitution_stats']:
                        st.write(f"**{stat.constitution_type}**: {stat.count}件")
                else:
                    st.info("まだ診断データがありません。")
                
                # 診断履歴の詳細表示
                st.subheader("📋 診断履歴詳細")
                history = get_diagnosis_history(50)  # 最新50件
                
                if history:
                    history_data = []
                    for record in history:
                        history_data.append({
                            'タイムスタンプ': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            '年齢': record.age,
                            '性別': record.gender,
                            '体質タイプ': record.constitution_type,
                            '気になる不調': record.free_text_concern[:50] + "..." if record.free_text_concern and len(record.free_text_concern) > 50 else record.free_text_concern
                        })
                    
                    df = pd.DataFrame(history_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # CSVダウンロード
                    csv = df.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="📥 診断履歴をCSVでダウンロード",
                        data=csv,
                        file_name=f"tcm_diagnosis_history_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("まだ診断履歴がありません。")
                    
            except Exception as e:
                st.error(f"データベースの読み込みに失敗しました: {str(e)}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    main()
