import random
from tcm_data import CONSTITUTION_TYPES

class DiagnosisEngine:
    """東洋医学体質診断エンジン"""
    
    def __init__(self):
        # 各体質タイプに対する質問の重み付け
        self.constitution_weights = {
            "気虚": {
                "question_0": [4, 3, 1, 0],  # 疲れやすさ - 疲れやすいほど気虚
                "question_2": [3, 2, 1, 0],  # 食欲 - 食欲不振は気虚
                "question_4": [3, 2, 0, 1],  # 便通 - 便秘傾向
                "question_6": [1, 2, 1, 0],  # 精神状態 - 不安傾向
                "question_8": [3, 1, 0, 0],  # 体型 - 痩せ型
            },
            "陽虚": {
                "question_1": [4, 3, 1, 0],  # 寒がり - 寒がりほど陽虚
                "question_5": [0, 1, 2, 4],  # 水分摂取 - 温かいものを好む
                "question_4": [1, 2, 0, 3],  # 便通 - 軟便傾向
                "question_8": [2, 1, 3, 0],  # 体型 - むくみやすい
            },
            "陰虚": {
                "question_1": [0, 1, 2, 4],  # 暑がり
                "question_3": [3, 2, 1, 0],  # 睡眠 - 不眠傾向
                "question_4": [4, 3, 1, 0],  # 便通 - 便秘傾向
                "question_5": [2, 1, 3, 1],  # 水分摂取 - 冷たいものを好む
                "question_7": [4, 2, 1, 0],  # 肌 - 乾燥肌
            },
            "痰湿": {
                "question_8": [0, 1, 4, 2],  # 体型 - ぽっちゃり、むくみ
                "question_0": [2, 3, 1, 0],  # 疲れやすさ - だるさ
                "question_2": [1, 2, 1, 3],  # 食欲 - 食欲旺盛
                "question_7": [1, 3, 2, 1],  # 肌 - 脂っぽい
            },
            "湿熱": {
                "question_7": [1, 4, 2, 1],  # 肌 - 脂っぽい、ニキビ
                "question_6": [4, 2, 1, 1],  # 精神状態 - イライラ
                "question_4": [3, 2, 1, 0],  # 便通 - 便秘
                "question_5": [1, 2, 4, 1],  # 水分摂取 - 冷たいものを好む
            },
            "血瘀": {
                "question_9": [4, 3, 1, 2],  # 頭痛・肩こり
                "question_6": [3, 1, 2, 2],  # 精神状態 - ストレス時症状
                "question_7": [2, 1, 3, 2],  # 肌の状態
                "question_8": [1, 2, 1, 3],  # 体型 - 筋肉質
            },
            "気鬱": {
                "question_6": [2, 4, 4, 0],  # 精神状態 - 不安、憂鬱
                "question_3": [3, 2, 1, 1],  # 睡眠 - 不眠傾向
                "question_9": [2, 1, 1, 4],  # 頭痛・肩こり - ストレス時
                "question_2": [2, 3, 1, 1],  # 食欲にムラ
            },
            "特禀": {
                "question_7": [2, 2, 1, 4],  # 肌 - 敏感肌
                "question_6": [1, 3, 1, 2],  # 精神状態 - 不安傾向
                "question_2": [2, 3, 1, 1],  # 食欲にムラ
            },
            "平和": {
                "question_0": [0, 1, 3, 4],  # 疲れにくい
                "question_2": [0, 1, 4, 2],  # 普通の食欲
                "question_3": [0, 1, 4, 2],  # 良い睡眠
                "question_4": [0, 1, 4, 1],  # 規則正しい便通
                "question_6": [0, 1, 1, 4],  # 精神安定
                "question_7": [0, 1, 4, 1],  # 普通の肌
                "question_9": [0, 1, 4, 2],  # 頭痛・肩こりなし
            }
        }
    
    def calculate_constitution_score(self, responses, constitution_type):
        """特定の体質タイプのスコアを計算"""
        if constitution_type not in self.constitution_weights:
            return 0
        
        weights = self.constitution_weights[constitution_type]
        total_score = 0
        max_possible_score = 0
        
        for question_key, response in responses.items():
            if question_key in weights:
                # 回答のインデックスを取得
                response_index = weights[question_key]
                if isinstance(response_index, list):
                    # 選択肢の文字列から回答インデックスを特定
                    # この実装では簡略化のため、質問データから推定
                    from tcm_data import TCM_QUESTIONS
                    question_num = int(question_key.split('_')[1])
                    if question_num < len(TCM_QUESTIONS):
                        options = TCM_QUESTIONS[question_num]['options']
                        if response in options:
                            idx = options.index(response)
                            if idx < len(response_index):
                                total_score += response_index[idx]
                                max_possible_score += max(response_index)
        
        # 正規化されたスコア（0-100）
        if max_possible_score > 0:
            return (total_score / max_possible_score) * 100
        return 0
    
    def diagnose(self, responses):
        """体質診断を実行"""
        constitution_scores = {}
        
        # 各体質タイプのスコアを計算
        for constitution_type in self.constitution_weights.keys():
            score = self.calculate_constitution_score(responses, constitution_type)
            constitution_scores[constitution_type] = score
        
        # 最高スコアの体質タイプを特定
        best_constitution = max(constitution_scores, key=constitution_scores.get)
        best_score = constitution_scores[best_constitution]
        
        # 信頼度を計算（最高スコアと2番目のスコアの差を考慮）
        sorted_scores = sorted(constitution_scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            score_diff = sorted_scores[0] - sorted_scores[1]
            confidence = min(95, 60 + score_diff * 0.7)
        else:
            confidence = 85
        
        # AI風のランダム要素を少し追加（信頼度の微調整）
        confidence += random.uniform(-5, 5)
        confidence = max(60, min(95, confidence))
        
        return {
            "constitution_type": best_constitution,
            "score": best_score,
            "confidence": confidence,
            "all_scores": constitution_scores
        }
