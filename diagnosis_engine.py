import random
from tcm_data import CONSTITUTION_TYPES

class DiagnosisEngine:
    """東洋医学体質診断エンジン（新しい問診フォーマット対応）"""
    
    def __init__(self):
        # 各体質タイプに対する診断ロジック
        self.diagnosis_rules = {
            "気虚": {
                "primary_indicators": [
                    ("疲れやすいと感じますか？", "はい"),
                    ("食欲がない、軟便になりやすいですか？", "はい")
                ],
                "secondary_indicators": [
                    ("風邪をひきやすい、肌が乾燥しやすいですか？", "はい"),
                    ("下半身が冷えやすい、足腰がだるくなることがありますか？", "はい")
                ]
            },
            "気滞": {
                "primary_indicators": [
                    ("イライラしやすい、胸やお腹がつかえる感じはありますか？", "はい"),
                    ("感情の波が激しい、目の疲れやすさはありますか？", "はい")
                ],
                "secondary_indicators": [
                    ("不安感が強い、睡眠の不調を感じますか？", "はい")
                ]
            },
            "水滞": {
                "primary_indicators": [
                    ("むくみやすい、胃がぽちゃぽちゃすることはありますか？", "はい"),
                    ("食欲がない、軟便になりやすいですか？", "はい")
                ],
                "secondary_indicators": [
                    ("下半身が冷えやすい、足腰がだるくなることがありますか？", "はい")
                ]
            },
            "血虚": {
                "primary_indicators": [
                    ("顔色が青白い、めまいがしやすいですか？", "はい"),
                    ("不安感が強い、睡眠の不調を感じますか？", "はい")
                ],
                "secondary_indicators": [
                    ("疲れやすいと感じますか？", "はい"),
                    ("風邪をひきやすい、肌が乾燥しやすいですか？", "はい")
                ]
            },
            "瘀血": {
                "primary_indicators": [
                    ("肩こりや生理痛がひどいなど、血の巡りが悪いと感じることはありますか？", "はい"),
                    ("感情の波が激しい、目の疲れやすさはありますか？", "はい")
                ],
                "secondary_indicators": [
                    ("イライラしやすい、胸やお腹がつかえる感じはありますか？", "はい")
                ]
            }
        }
    
    def calculate_constitution_score(self, responses, constitution_type):
        """特定の体質タイプのスコアを計算"""
        if constitution_type not in self.diagnosis_rules:
            return 0
        
        rules = self.diagnosis_rules[constitution_type]
        score = 0
        max_score = 0
        
        # プライマリ指標のチェック（重み3）
        for question, expected_answer in rules["primary_indicators"]:
            max_score += 3
            # 質問文をチェック
            for q_key, response in responses.items():
                if "_question" in q_key and question in response:
                    # 対応する回答を取得
                    answer_key = q_key.replace("_question", "")
                    if answer_key in responses and responses[answer_key] == expected_answer:
                        score += 3
                    break
        
        # セカンダリ指標のチェック（重み1）
        for question, expected_answer in rules["secondary_indicators"]:
            max_score += 1
            for q_key, response in responses.items():
                if "_question" in q_key and question in response:
                    answer_key = q_key.replace("_question", "")
                    if answer_key in responses and responses[answer_key] == expected_answer:
                        score += 1
                    break
        
        # フォローアップ質問による加算
        for q_key, response in responses.items():
            if "follow_up" in q_key and response != "どれも当てはまらない":
                max_score += 1
                # 複数選択の場合（カンマ区切り）もチェック
                response_items = [item.strip() for item in response.split(',')]
                
                # 特定の症状がある場合の加算ロジック
                matching_symptoms = []
                if constitution_type == "気虚":
                    matching_symptoms = ["息切れしやすい", "声に力がない", "食後に眠くなる"]
                elif constitution_type == "気滞":
                    matching_symptoms = ["ため息をよくつく", "月経前に不調がある", "胸や喉に違和感"]
                elif constitution_type == "水滞":
                    matching_symptoms = ["雨の日に体調が悪い", "下痢や軟便になりやすい", "舌に歯型がある"]
                elif constitution_type == "血虚":
                    matching_symptoms = ["爪が割れやすい", "動悸がある", "夢をよく見る"]
                elif constitution_type == "瘀血":
                    matching_symptoms = ["刺すような痛み", "経血に血塊が多い", "シミやくすみが目立つ"]
                
                # マッチする症状の数に応じてスコア加算
                matches = sum(1 for item in response_items if item in matching_symptoms)
                if matches > 0:
                    score += min(matches, 2)  # 最大2点まで加算
        
        # 正規化されたスコア（0-100）
        if max_score > 0:
            return (score / max_score) * 100
        return 0
    
    def diagnose(self, responses):
        """体質診断を実行"""
        constitution_scores = {}
        
        # 各体質タイプのスコアを計算
        for constitution_type in self.diagnosis_rules.keys():
            score = self.calculate_constitution_score(responses, constitution_type)
            constitution_scores[constitution_type] = score
        
        # 最高スコアの体質タイプを特定
        if constitution_scores:
            best_constitution = max(constitution_scores, key=constitution_scores.get)
            best_score = constitution_scores[best_constitution]
        else:
            best_constitution = "気虚"  # デフォルト
            best_score = 50
        
        # 信頼度を計算（最高スコアと2番目のスコアの差を考慮）
        sorted_scores = sorted(constitution_scores.values(), reverse=True)
        if len(sorted_scores) >= 2 and sorted_scores[0] > 0:
            score_diff = sorted_scores[0] - sorted_scores[1]
            confidence = min(95, 60 + score_diff * 0.5)
        else:
            confidence = 75
        
        # AI風のランダム要素を少し追加（信頼度の微調整）
        confidence += random.uniform(-3, 3)
        confidence = max(65, min(95, confidence))
        
        return {
            "constitution_type": best_constitution,
            "score": best_score,
            "confidence": confidence,
            "all_scores": constitution_scores
        }