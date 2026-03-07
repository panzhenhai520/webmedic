#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Service
病历文档管理服务
"""

import os
import hashlib
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.medical_document import MedicalDocument


class DocumentService:
    """病历文档管理服务"""

    @staticmethod
    def scan_local_directory(db: Session, directory: str) -> Tuple[int, int, int, List[MedicalDocument]]:
        """
        扫描本地目录，发现并登记 PDF 文件

        Args:
            db: 数据库会话
            directory: 要扫描的目录路径

        Returns:
            (total_found, new_added, already_exists, documents)
        """
        if not os.path.exists(directory):
            raise ValueError(f"目录不存在: {directory}")

        if not os.path.isdir(directory):
            raise ValueError(f"路径不是目录: {directory}")

        # 扫描目录中的 PDF 文件
        pdf_files = []
        for file_name in os.listdir(directory):
            if file_name.lower().endswith('.pdf'):
                file_path = os.path.join(directory, file_name)
                if os.path.isfile(file_path):
                    pdf_files.append((file_name, file_path))

        total_found = len(pdf_files)
        new_added = 0
        already_exists = 0
        documents = []

        for file_name, file_path in pdf_files:
            # 计算文件哈希值
            file_hash = DocumentService._calculate_file_hash(file_path)

            # 检查文件是否已存在
            existing_doc = db.query(MedicalDocument).filter(
                MedicalDocument.file_hash == file_hash
            ).first()

            if existing_doc:
                already_exists += 1
                documents.append(existing_doc)
            else:
                # 创建新文档记录
                new_doc = MedicalDocument(
                    file_name=file_name,
                    file_path=file_path,
                    file_hash=file_hash,
                    parse_status="pending",
                    index_status="pending",
                    source_type="pdf"
                )
                db.add(new_doc)
                db.flush()
                new_added += 1
                documents.append(new_doc)

        db.commit()

        return total_found, new_added, already_exists, documents

    @staticmethod
    def _calculate_file_hash(file_path: str) -> str:
        """
        计算文件的 SHA256 哈希值

        Args:
            file_path: 文件路径

        Returns:
            文件哈希值
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # 分块读取文件，避免大文件占用过多内存
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def get_all_documents(db: Session) -> List[MedicalDocument]:
        """
        获取所有文档

        Args:
            db: 数据库会话

        Returns:
            文档列表
        """
        return db.query(MedicalDocument).order_by(MedicalDocument.created_at.desc()).all()

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> MedicalDocument:
        """
        根据ID获取文档

        Args:
            db: 数据库会话
            document_id: 文档ID

        Returns:
            文档对象
        """
        return db.query(MedicalDocument).filter(MedicalDocument.id == document_id).first()

    @staticmethod
    def register_document(db: Session, file_path: str) -> MedicalDocument:
        """
        登记单个文档到数据库

        Args:
            db: 数据库会话
            file_path: 文件路径

        Returns:
            文档对象
        """
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")

        file_name = os.path.basename(file_path)
        file_hash = DocumentService._calculate_file_hash(file_path)

        # 检查文件是否已存在
        existing_doc = db.query(MedicalDocument).filter(
            MedicalDocument.file_hash == file_hash
        ).first()

        if existing_doc:
            return existing_doc

        # 创建新文档记录
        new_doc = MedicalDocument(
            file_name=file_name,
            file_path=file_path,
            file_hash=file_hash,
            parse_status="pending",
            index_status="pending",
            source_type="pdf"
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        return new_doc
