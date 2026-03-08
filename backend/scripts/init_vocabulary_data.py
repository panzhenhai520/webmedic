#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化医学词库数据
将 medical_vocabulary.py 中的数据导入数据库
"""

import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.medical_vocabulary import MedicalVocabulary
from app.models.icd_code import ICDCode
from app.models.surgery_code import SurgeryCode
from app.utils.medical_vocabulary import BODY_PARTS, SYMPTOMS, DISEASES, DIRECTIONS


def init_medical_vocabulary():
    """初始化医学词汇表"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        count = db.query(MedicalVocabulary).count()
        if count > 0:
            print(f"医学词汇表已有 {count} 条数据，跳过初始化")
            return

        print("开始初始化医学词汇表...")

        # 导入身体部位
        for standard_name, keywords in BODY_PARTS.items():
            # 判断专科分类
            specialty = None
            if any(bone in standard_name for bone in ["骨", "椎", "关节"]):
                specialty = "骨科"
            elif any(organ in standard_name for organ in ["心", "肺", "肝", "胆", "胰", "脾", "胃", "肠", "肾"]):
                specialty = "内科"

            vocab = MedicalVocabulary(
                category="body_parts",
                standard_name=standard_name,
                keywords=json.dumps(keywords, ensure_ascii=False),
                specialty=specialty,
                status="active"
            )
            db.add(vocab)

        # 导入症状
        for standard_name, keywords in SYMPTOMS.items():
            vocab = MedicalVocabulary(
                category="symptoms",
                standard_name=standard_name,
                keywords=json.dumps(keywords, ensure_ascii=False),
                status="active"
            )
            db.add(vocab)

        # 导入疾病
        for standard_name, keywords in DISEASES.items():
            vocab = MedicalVocabulary(
                category="diseases",
                standard_name=standard_name,
                keywords=json.dumps(keywords, ensure_ascii=False),
                status="active"
            )
            db.add(vocab)

        # 导入方位词
        for standard_name, keywords in DIRECTIONS.items():
            vocab = MedicalVocabulary(
                category="directions",
                standard_name=standard_name,
                keywords=json.dumps(keywords, ensure_ascii=False),
                status="active"
            )
            db.add(vocab)

        db.commit()

        total = db.query(MedicalVocabulary).count()
        print(f"医学词汇表初始化完成，共导入 {total} 条数据")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


def init_icd_codes():
    """初始化ICD编码（示例数据）"""
    db = SessionLocal()

    try:
        count = db.query(ICDCode).count()
        if count > 0:
            print(f"ICD编码表已有 {count} 条数据，跳过初始化")
            return

        print("开始初始化ICD编码表...")

        # 常见疾病ICD-10编码示例
        icd_data = [
            # 消化系统疾病 (K00-K93)
            {"code": "K80.2", "name_cn": "不伴梗阻的胆囊结石", "category": "消化系统疾病",
             "keywords": ["胆结石", "胆囊结石", "胆石症"]},
            {"code": "K80.5", "name_cn": "不伴梗阻的胆管结石", "category": "消化系统疾病",
             "keywords": ["胆管结石", "胆总管结石"]},
            {"code": "K82.8", "name_cn": "胆囊的其他特指疾病", "category": "消化系统疾病",
             "keywords": ["胆囊息肉", "胆囊炎"]},
            {"code": "K76.0", "name_cn": "肝脂肪变性", "category": "消化系统疾病",
             "keywords": ["脂肪肝", "肝脂肪变"]},
            {"code": "K29.5", "name_cn": "慢性胃炎", "category": "消化系统疾病",
             "keywords": ["胃炎", "慢性胃炎"]},

            # 循环系统疾病 (I00-I99)
            {"code": "I10", "name_cn": "原发性高血压", "category": "循环系统疾病",
             "keywords": ["高血压", "血压高"]},
            {"code": "I25.1", "name_cn": "动脉粥样硬化性心脏病", "category": "循环系统疾病",
             "keywords": ["冠心病", "冠状动脉粥样硬化"]},

            # 呼吸系统疾病 (J00-J99)
            {"code": "J18.9", "name_cn": "肺炎", "category": "呼吸系统疾病",
             "keywords": ["肺炎"]},
            {"code": "J45.9", "name_cn": "哮喘", "category": "呼吸系统疾病",
             "keywords": ["哮喘", "支气管哮喘"]},

            # 肌肉骨骼系统疾病 (M00-M99)
            {"code": "M47.2", "name_cn": "其他脊椎病", "category": "肌肉骨骼系统疾病",
             "keywords": ["颈椎病", "脊椎病"]},
            {"code": "M51.2", "name_cn": "其他特指的椎间盘移位", "category": "肌肉骨骼系统疾病",
             "keywords": ["腰椎间盘突出", "椎间盘突出", "腰突"]},
            {"code": "M19.9", "name_cn": "关节病", "category": "肌肉骨骼系统疾病",
             "keywords": ["关节炎", "骨关节炎"]},

            # 内分泌疾病 (E00-E90)
            {"code": "E11.9", "name_cn": "2型糖尿病", "category": "内分泌疾病",
             "keywords": ["糖尿病", "血糖高", "2型糖尿病"]},
            {"code": "E05.9", "name_cn": "甲状腺毒症", "category": "内分泌疾病",
             "keywords": ["甲亢", "甲状腺功能亢进"]},
        ]

        for item in icd_data:
            icd = ICDCode(
                icd_code=item["code"],
                icd_name_cn=item["name_cn"],
                category=item["category"],
                keywords=json.dumps(item["keywords"], ensure_ascii=False),
                status="active"
            )
            db.add(icd)

        db.commit()

        total = db.query(ICDCode).count()
        print(f"ICD编码表初始化完成，共导入 {total} 条数据")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


def init_surgery_codes():
    """初始化手术编码（示例数据）"""
    db = SessionLocal()

    try:
        count = db.query(SurgeryCode).count()
        if count > 0:
            print(f"手术编码表已有 {count} 条数据，跳过初始化")
            return

        print("开始初始化手术编码表...")

        # 常见手术编码示例（ICD-9-CM-3）
        surgery_data = [
            # 消化系统手术
            {"code": "51.22", "name": "腹腔镜胆囊切除术", "category": "消化系统手术",
             "keywords": ["胆囊切除", "腹腔镜胆囊切除"], "level": "3"},
            {"code": "51.23", "name": "开腹胆囊切除术", "category": "消化系统手术",
             "keywords": ["胆囊切除", "开腹胆囊切除"], "level": "3"},
            {"code": "45.23", "name": "结肠镜检查", "category": "消化系统手术",
             "keywords": ["结肠镜", "肠镜"], "level": "2"},
            {"code": "44.13", "name": "胃镜检查", "category": "消化系统手术",
             "keywords": ["胃镜", "胃镜检查"], "level": "2"},

            # 骨科手术
            {"code": "81.54", "name": "全髋关节置换术", "category": "骨科手术",
             "keywords": ["髋关节置换", "人工髋关节"], "level": "4"},
            {"code": "81.55", "name": "全膝关节置换术", "category": "骨科手术",
             "keywords": ["膝关节置换", "人工膝关节"], "level": "4"},
            {"code": "80.51", "name": "椎间盘切除术", "category": "骨科手术",
             "keywords": ["椎间盘切除", "腰椎手术"], "level": "3"},
            {"code": "79.35", "name": "骨折闭合复位", "category": "骨科手术",
             "keywords": ["骨折复位", "闭合复位"], "level": "2"},

            # 心血管手术
            {"code": "36.1", "name": "冠状动脉旁路移植术", "category": "心血管手术",
             "keywords": ["冠脉搭桥", "搭桥手术", "CABG"], "level": "4"},
            {"code": "37.22", "name": "左心导管检查", "category": "心血管手术",
             "keywords": ["心导管", "冠脉造影"], "level": "3"},

            # 普通外科
            {"code": "47.09", "name": "阑尾切除术", "category": "普通外科",
             "keywords": ["阑尾切除", "阑尾炎手术"], "level": "2"},
            {"code": "53.00", "name": "疝修补术", "category": "普通外科",
             "keywords": ["疝修补", "疝气手术"], "level": "2"},
        ]

        for item in surgery_data:
            surgery = SurgeryCode(
                surgery_code=item["code"],
                surgery_name=item["name"],
                category=item["category"],
                keywords=json.dumps(item["keywords"], ensure_ascii=False),
                difficulty_level=item["level"],
                status="active"
            )
            db.add(surgery)

        db.commit()

        total = db.query(SurgeryCode).count()
        print(f"手术编码表初始化完成，共导入 {total} 条数据")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("="*60)
    print("医学词库数据初始化")
    print("="*60)

    try:
        init_medical_vocabulary()
        print()
        init_icd_codes()
        print()
        init_surgery_codes()
        print()
        print("="*60)
        print("所有数据初始化完成！")
        print("="*60)
    except Exception as e:
        print(f"初始化过程出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
