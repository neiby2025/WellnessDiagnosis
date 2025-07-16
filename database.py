import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DiagnosisResult(Base):
    """診断結果テーブル"""
    __tablename__ = "diagnosis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    age = Column(String(50))
    gender = Column(String(20))
    constitution_type = Column(String(50))
    score = Column(Float)
    confidence = Column(Float)
    responses = Column(JSONB)  # JSON形式で全回答を保存
    free_text_concern = Column(Text)  # 自由記述の悩み
    all_scores = Column(JSONB)  # 全体質タイプのスコア

class User(Base):
    """ユーザーテーブル（将来の拡張用）"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_diagnosis = Column(DateTime)
    total_diagnoses = Column(Integer, default=0)

def create_tables():
    """データベーステーブルを作成"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_diagnosis_result(user_data, diagnosis_result, responses):
    """診断結果をデータベースに保存"""
    db = SessionLocal()
    try:
        # 自由記述の回答を抽出
        free_text_concern = ""
        for key, value in responses.items():
            if "question_10" in key and not "_question" in key:  # 最後の自由記述質問
                free_text_concern = value
                break
        
        db_result = DiagnosisResult(
            age=user_data.get('age', ''),
            gender=user_data.get('gender', ''),
            constitution_type=diagnosis_result['constitution_type'],
            score=diagnosis_result['score'],
            confidence=diagnosis_result['confidence'],
            responses=responses,
            free_text_concern=free_text_concern,
            all_scores=diagnosis_result['all_scores']
        )
        
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_diagnosis_history(limit=100):
    """診断履歴を取得"""
    db = SessionLocal()
    try:
        results = db.query(DiagnosisResult).order_by(DiagnosisResult.timestamp.desc()).limit(limit).all()
        return results
    finally:
        db.close()

def get_diagnosis_stats():
    """診断統計を取得"""
    db = SessionLocal()
    try:
        total_diagnoses = db.query(DiagnosisResult).count()
        
        # 体質タイプ別の統計
        constitution_stats = db.query(
            DiagnosisResult.constitution_type,
            db.func.count(DiagnosisResult.constitution_type).label('count')
        ).group_by(DiagnosisResult.constitution_type).all()
        
        # 年齢別の統計
        age_stats = db.query(
            DiagnosisResult.age,
            db.func.count(DiagnosisResult.age).label('count')
        ).group_by(DiagnosisResult.age).all()
        
        # 性別統計
        gender_stats = db.query(
            DiagnosisResult.gender,
            db.func.count(DiagnosisResult.gender).label('count')
        ).group_by(DiagnosisResult.gender).all()
        
        return {
            'total_diagnoses': total_diagnoses,
            'constitution_stats': constitution_stats,
            'age_stats': age_stats,
            'gender_stats': gender_stats
        }
    finally:
        db.close()

# データベーステーブルを初期化
create_tables()