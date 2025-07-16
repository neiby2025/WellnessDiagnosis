import streamlit as st
import pandas as pd
import datetime
import os
from tcm_data import TCM_QUESTIONS, CONSTITUTION_TYPES, HEALTH_ADVICE
from diagnosis_engine import DiagnosisEngine

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

def save_result_to_csv(user_data, diagnosis_result):
    """診断結果をCSVファイルに保存"""
    try:
        # データディレクトリが存在しない場合は作成
        os.makedirs('data', exist_ok=True)
        
        # 保存するデータを準備
        result_data = {
            'タイムスタンプ': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '年齢': user_data.get('age', ''),
            '性別': user_data.get('gender', ''),
            '体質タイプ': diagnosis_result['constitution_type'],
            'スコア': diagnosis_result['score'],
            '信頼度': f"{diagnosis_result['confidence']:.1f}%"
        }
        
        # 質問への回答も保存
        for i, response in enumerate(st.session_state.user_responses.values()):
            result_data[f'質問{i+1}'] = response
        
        # CSVファイルに追記
        df = pd.DataFrame([result_data])
        csv_file = 'data/results.csv'
        
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8')
        else:
            df.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')
        
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
        - 陽虚（ようきょ）
        - 陰虚（いんきょ）
        - 痰湿（たんしつ）
        - 湿熱（しつねつ）
        - 血瘀（けつお）
        - 気鬱（きうつ）
        - 特禀（とくひん）
        - 平和（へいわ）
        """)
    
    # 診断が完了していない場合は質問を表示
    if not st.session_state.diagnosis_complete:
        st.header("📋 体質診断質問票")
        st.write("以下の質問に答えて、あなたの体質を診断しましょう。")
        
        # 基本情報の入力
        st.subheader("基本情報")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.selectbox("年齢", ["20歳未満", "20-29歳", "30-39歳", "40-49歳", "50-59歳", "60歳以上"])
        with col2:
            gender = st.selectbox("性別", ["男性", "女性", "その他"])
        
        st.markdown("---")
        
        # 質問票
        st.subheader("体調に関する質問")
        st.write("あなたの普段の体調に最も近いものを選択してください。")
        
        responses = {}
        
        for i, question in enumerate(TCM_QUESTIONS):
            st.write(f"**質問 {i+1}: {question['question']}**")
            
            response = st.radio(
                f"質問{i+1}の回答",
                question['options'],
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            responses[f"question_{i}"] = response
        
        # 診断ボタン
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 体質診断を実行", type="primary", use_container_width=True):
                # 全ての質問に回答されているかチェック
                if len(responses) == len(TCM_QUESTIONS):
                    # 診断エンジンで結果を計算
                    engine = DiagnosisEngine()
                    diagnosis_result = engine.diagnose(responses)
                    
                    # セッション状態を更新
                    st.session_state.user_responses = responses
                    st.session_state.diagnosis_result = diagnosis_result
                    st.session_state.diagnosis_complete = True
                    
                    # 結果をCSVに保存
                    user_data = {'age': age, 'gender': gender}
                    save_result_to_csv(user_data, diagnosis_result)
                    
                    st.rerun()
                else:
                    st.error("すべての質問にお答えください。")
    
    # 診断結果の表示
    else:
        result = st.session_state.diagnosis_result
        
        st.header("🎯 診断結果")
        
        # 結果のメイン表示
        st.success(f"**あなたの体質タイプ: {result['constitution_type']}**")
        
        # 信頼度の表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("診断スコア", f"{result['score']:.1f}")
        with col2:
            st.metric("信頼度", f"{result['confidence']:.1f}%")
        
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
                if os.path.exists('data/results.csv'):
                    df = pd.read_csv('data/results.csv', encoding='utf-8')
                    st.dataframe(df, use_container_width=True)
                    
                    # CSVダウンロード
                    csv = df.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="📥 CSVファイルをダウンロード",
                        data=csv,
                        file_name=f"tcm_diagnosis_results_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("まだ診断履歴がありません。")
            except Exception as e:
                st.error(f"履歴の読み込みに失敗しました: {str(e)}")

if __name__ == "__main__":
    main()
