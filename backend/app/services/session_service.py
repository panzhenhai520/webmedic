#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Service
会话管理服务
"""

from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models import EncounterSession, Doctor, Patient, TranscriptSegment


class SessionService:
    """会话服务类"""

    @staticmethod
    def generate_session_no() -> str:
        """
        生成会话编号
        格式：WM + 年月日 + 时分秒 + 毫秒
        例如：WM20240306143025123
        """
        now = datetime.now()
        return now.strftime("WM%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"

    @staticmethod
    def create_session(db: Session, doctor_id: int, patient_id: int) -> EncounterSession:
        """
        创建问诊会话

        Args:
            db: 数据库会话
            doctor_id: 医生ID
            patient_id: 患者ID

        Returns:
            创建的会话对象

        Raises:
            ValueError: 如果医生或患者不存在
        """
        # 验证医生是否存在
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise ValueError(f"医生ID {doctor_id} 不存在")

        # 验证患者是否存在
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"患者ID {patient_id} 不存在")

        # 生成会话编号
        session_no = SessionService.generate_session_no()

        # 创建会话
        session = EncounterSession(
            session_no=session_no,
            doctor_id=doctor_id,
            patient_id=patient_id,
            status="started",
            started_at=datetime.now()
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def end_session(db: Session, session_id: int) -> EncounterSession:
        """
        结束问诊会话

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            更新后的会话对象

        Raises:
            ValueError: 如果会话不存在或已结束
        """
        # 查询会话
        session = db.query(EncounterSession).filter(EncounterSession.id == session_id).first()
        if not session:
            raise ValueError(f"会话ID {session_id} 不存在")

        if session.status == "ended":
            raise ValueError(f"会话已结束，无法重复结束")

        # 更新会话状态
        session.status = "ended"
        session.ended_at = datetime.now()

        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def get_session(db: Session, session_id: int) -> EncounterSession:
        """
        获取会话详情

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            会话对象

        Raises:
            ValueError: 如果会话不存在
        """
        session = db.query(EncounterSession).filter(EncounterSession.id == session_id).first()
        if not session:
            raise ValueError(f"会话ID {session_id} 不存在")

        return session

    @staticmethod
    def get_default_doctor(db: Session) -> Doctor:
        """
        获取默认医生（Doctor Panython）

        Args:
            db: 数据库会话

        Returns:
            医生对象

        Raises:
            ValueError: 如果默认医生不存在
        """
        doctor = db.query(Doctor).filter(Doctor.doctor_name == "Doctor Panython").first()
        if not doctor:
            raise ValueError("默认医生 Doctor Panython 不存在")

        return doctor

    @staticmethod
    def get_default_patient(db: Session) -> Patient:
        """
        获取默认患者（张三）

        Args:
            db: 数据库会话

        Returns:
            患者对象

        Raises:
            ValueError: 如果默认患者不存在
        """
        patient = db.query(Patient).filter(Patient.patient_name == "张三").first()
        if not patient:
            raise ValueError("默认患者 张三 不存在")

        return patient

    @staticmethod
    def get_all_sessions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        doctor_id: Optional[int] = None
    ) -> Tuple[List[dict], int]:
        """
        获取会话列表（分页），包含医生和患者信息

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            status: 状态过滤 (created/started/ended)
            doctor_id: 医生ID过滤（可选）

        Returns:
            (会话列表, 总数)
        """
        query = db.query(EncounterSession)

        if status:
            query = query.filter(EncounterSession.status == status)

        if doctor_id:
            query = query.filter(EncounterSession.doctor_id == doctor_id)

        total = query.count()
        sessions = query.order_by(
            EncounterSession.created_at.desc()
        ).offset(skip).limit(limit).all()

        # 关联查询医生和患者信息
        result = []
        for session in sessions:
            doctor = db.query(Doctor).filter(Doctor.id == session.doctor_id).first()
            patient = db.query(Patient).filter(Patient.id == session.patient_id).first()

            # 统计转写片段数量
            transcript_count = db.query(TranscriptSegment).filter(
                TranscriptSegment.session_id == session.id
            ).count()

            result.append({
                "id": session.id,
                "session_no": session.session_no,
                "status": session.status,
                "doctor_name": doctor.doctor_name if doctor else "未知",
                "doctor_title": doctor.title if doctor else "",
                "patient_name": patient.patient_name if patient else "未知",
                "patient_gender": patient.gender if patient else "",
                "patient_age": patient.age if patient else 0,
                "transcript_count": transcript_count,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
                "created_at": session.created_at
            })

        return result, total

    @staticmethod
    def get_session_with_transcripts(
        db: Session,
        session_id: int
    ) -> dict:
        """
        获取会话详情（包含转写记录）

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            包含会话和转写记录的字典
        """
        session = SessionService.get_session(db, session_id)

        # 获取转写记录
        transcripts = db.query(TranscriptSegment).filter(
            TranscriptSegment.session_id == session_id
        ).order_by(TranscriptSegment.created_at.asc()).all()

        return {
            "session": session,
            "transcripts": transcripts,
            "transcript_count": len(transcripts)
        }
