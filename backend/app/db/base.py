#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLAlchemy Base Class
所有数据模型的基类
"""

from sqlalchemy.ext.declarative import declarative_base

# 创建 SQLAlchemy Base 类
Base = declarative_base()

# 导入所有模型，确保它们被注册到 Base.metadata
# 这样 Base.metadata.create_all() 才能创建所有表
def import_all_models():
    """导入所有模型以注册到 Base.metadata"""
    from app.models.doctor import Doctor
    from app.models.patient import Patient
    from app.models.encounter_session import EncounterSession
    from app.models.transcript_segment import TranscriptSegment
    from app.models.structured_record import StructuredRecord
    from app.models.medical_document import MedicalDocument
    from app.models.similar_case_match import SimilarCaseMatch
    from app.models.emr_draft import EmrDraft
    from app.models.clinical_hint import ClinicalHint
