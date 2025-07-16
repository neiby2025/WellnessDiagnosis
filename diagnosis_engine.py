import random
from tcm_data import CONSTITUTION_TYPES

class DiagnosisEngine:
    """東洋医学体質診断エンジン（新しい問診フォーマット対応）"""
    
    def __init__(self):
        # 各体質タイプに対する診断ロジック（TCM専門文書に基づく）
        self.diagnosis_rules = {
            "気虚": {
                "primary_questions": {
                    "疲れやすいと感じますか？": 4,  # 主症状
                    "食欲がない、軟便になりやすいですか？": 3,  # 脾胃気虚
                    "風邪をひきやすい、肌が乾燥しやすいですか？": 3,  # 肺気虚
                    "下半身が冷えやすい、足腰がだるくなることがありますか？": 3  # 腎陽虚
                },
                "follow_up_symptoms": {
                    # 質問1のフォローアップ
                    "朝から": 2, "食後に": 3, "夕方以降": 2,
                    "息切れしやすい": 3, "声に力がない": 3, "食後に眠くなる": 3,
                    # 質問7のフォローアップ
                    "動悸がする": 2,
                    # 質問8のフォローアップ  
                    "食欲がない、または食べたくないことがよくある": 3,
                    "下痢・軟便になりやすい": 2, "食後すぐにお腹がもたれる": 2,
                    # 質問9のフォローアップ
                    "鼻水や鼻づまり": 2,
                    # 質問10のフォローアップ
                    "頻尿・夜間尿がある": 3, "足腰のだるさがある": 3, "耳鳴り・聴力低下がある": 2
                }
            },
            "気滞": {
                "primary_questions": {
                    "イライラしやすい、胸やお腹がつかえる感じはありますか？": 4,  # 主症状
                    "感情の波が激しい、目の疲れやすさはありますか？": 3,  # 肝気鬱結
                    "不安感が強い、睡眠の不調を感じますか？": 2  # 肝鬱による
                },
                "follow_up_symptoms": {
                    # 質問2のフォローアップ
                    "ため息をよくつく": 3, "月経前に不調がある": 3, "胸や喉に違和感": 3,
                    # 質問6のフォローアップ
                    "怒りっぽい": 4, "月経不順": 3
                }
            },
            "水滞": {
                "primary_questions": {
                    "むくみやすい、胃がぽちゃぽちゃすることはありますか？": 4,  # 主症状
                    "食欲がない、軟便になりやすいですか？": 2  # 脾虚湿盛
                },
                "follow_up_symptoms": {
                    # 質問5のフォローアップ
                    "雨の日に体調が悪い": 3, "下痢や軟便になりやすい": 3, "舌に歯型がある": 3,
                    # 質問8のフォローアップ
                    "下痢・軟便になりやすい": 2,
                    # 質問9のフォローアップ
                    "鼻水や鼻づまり": 2
                }
            },
            "血虚": {
                "primary_questions": {
                    "顔色が青白い、めまいがしやすいですか？": 4,  # 主症状
                    "不安感が強い、睡眠の不調を感じますか？": 3,  # 心血虚
                    "感情の波が激しい、目の疲れやすさはありますか？": 2,  # 肝血虚
                    "風邪をひきやすい、肌が乾燥しやすいですか？": 2  # 血燥
                },
                "follow_up_symptoms": {
                    # 質問3のフォローアップ
                    "爪が割れやすい": 3, "動悸がある": 3, "夢をよく見る": 3,
                    # 質問6のフォローアップ
                    "目が乾く、かすむ": 3,
                    # 質問7のフォローアップ
                    "動悸がする": 2, "眠りが浅い": 3, "多夢": 3,
                    # 質問9のフォローアップ
                    "肌が乾燥する": 3, "空咳": 2,
                    # 質問10のフォローアップ
                    "耳鳴り・聴力低下がある": 2
                }
            },
            "瘀血": {
                "primary_questions": {
                    "肩こりや生理痛がひどいなど、血の巡りが悪いと感じることはありますか？": 4  # 主症状
                },
                "follow_up_symptoms": {
                    # 質問4のフォローアップ
                    "刺すような痛み": 4, "経血に血塊が多い": 4, "シミやくすみが目立つ": 3
                }
            }
        }
    
    def calculate_constitution_score(self, responses, constitution_type):
        """特定の体質タイプのスコアを計算（TCM専門文書に基づく）"""
        if constitution_type not in self.diagnosis_rules:
            return 0
        
        rules = self.diagnosis_rules[constitution_type]
        score = 0
        max_score = 0
        
        # プライマリ質問のチェック
        for question, weight in rules["primary_questions"].items():
            max_score += weight
            # 質問文をチェック
            for q_key, response in responses.items():
                if "_question" in q_key and question in response:
                    # 対応する回答を取得
                    answer_key = q_key.replace("_question", "")
                    if answer_key in responses and responses[answer_key] == "はい":
                        score += weight
                    break
        
        # フォローアップ症状による加算
        for q_key, response in responses.items():
            if "follow_up" in q_key and response != "どれも当てはまらない":
                # 複数選択の場合（カンマ区切り）をチェック
                response_items = [item.strip() for item in response.split(',')]
                
                for symptom in response_items:
                    if symptom in rules["follow_up_symptoms"]:
                        symptom_weight = rules["follow_up_symptoms"][symptom]
                        score += symptom_weight
                        max_score += symptom_weight
        
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
        
        # 自由記述質問の分析（簡易版）
        free_text_analysis = self.analyze_free_text(responses)
        for constitution_type, additional_score in free_text_analysis.items():
            if constitution_type in constitution_scores:
                constitution_scores[constitution_type] += additional_score
        
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
    
    def analyze_free_text(self, responses):
        """自由記述質問の分析"""
        analysis_result = {"気虚": 0, "気滞": 0, "水滞": 0, "血虚": 0, "瘀血": 0}
        
        # 質問11の自由記述を取得
        free_text = ""
        for key, value in responses.items():
            if "question_10" in key and not "_question" in key and value:
                free_text = value.lower()
                break
        
        if not free_text:
            return analysis_result
        
        # キーワードベースの簡易分析
        keywords = {
            "気虚": ["疲れ", "だるい", "疲労", "息切れ", "食欲", "下痢", "軟便", "冷え"],
            "気滞": ["イライラ", "ストレス", "憂鬱", "胸", "つかえ", "ため息", "生理前"],
            "水滞": ["むくみ", "浮腫", "重い", "だるい", "雨", "湿気", "胃", "ぽちゃぽちゃ"],
            "血虚": ["めまい", "立ちくらみ", "動悸", "不眠", "爪", "肌", "乾燥", "白い"],
            "瘀血": ["痛み", "こり", "生理痛", "血塊", "しみ", "あざ", "刺す", "固定"]
        }
        
        for constitution_type, keyword_list in keywords.items():
            matches = sum(1 for keyword in keyword_list if keyword in free_text)
            if matches > 0:
                analysis_result[constitution_type] = min(matches * 2, 10)  # 最大10点
        
        return analysis_result