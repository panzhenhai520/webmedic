# WebMedic - 语音驱动门诊电子病历生成系统

## 项目简介

WebMedic 是一个基于语音识别和 AI 技术的门诊电子病历生成 Demo 系统，用于演示完整的智能问诊辅助流程。

**⚠️ 重要声明：本项目为技术演示 Demo，不可用于临床正式诊疗，LLM 输出不可作为最终医学结论。**

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **Python**: 3.11.5

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **状态管理**: Pinia
- **UI 组件**: Element Plus
- **HTTP 客户端**: Axios

### AI 组件
- **语音识别**: Dolphin ASR
- **结构化抽取**: Instructor + DeepSeek
- **文档索引**: PageIndex
- **医学知识**: DeepSeek API

## 项目结构

```
D:\webmedic\
├── backend\              # 后端服务
│   ├── app\             # 应用代码
│   │   ├── api\         # API 路由
│   │   ├── core\        # 核心配置
│   │   ├── db\          # 数据库
│   │   ├── models\      # 数据模型
│   │   ├── schemas\     # Pydantic 模型
│   │   ├── services\    # 业务逻辑
│   │   ├── utils\       # 工具函数
│   │   └── prompts\     # AI Prompt 模板
│   ├── medical_records\ # 病历文件目录
│   ├── uploads\         # 上传文件目录
│   ├── logs\            # 日志目录
│   ├── tests\           # 测试代码
│   ├── run.py           # 启动入口
│   ├── requirements.txt # Python 依赖
│   └── .env.example     # 环境变量示例
│
├── frontend\            # 前端应用
│   ├── src\
│   │   ├── api\         # API 调用
│   │   ├── components\  # 组件
│   │   ├── views\       # 页面
│   │   ├── stores\      # 状态管理
│   │   ├── router\      # 路由
│   │   └── assets\      # 静态资源
│   ├── package.json     # 前端依赖
│   └── vite.config.js   # Vite 配置
│
├── docs\                # 文档目录
├── ffmpeg             #录音库，需要在windows系统的path中加入这个目录下的bin路径，https://github.com/FFmpeg，https://www.gyan.dev/ffmpeg/builds/
└── README.md            # 项目说明
```

## 快速开始

### 环境要求

- Python 3.11.5
- Node.js 18+
- MySQL 8.0+

### 后端启动

1. 进入后端目录
```bash
cd D:\webmedic\backend
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
# 复制 .env.example 为 .env
copy .env.example .env

# 编辑 .env 文件，配置数据库密码等信息
```

5. 启动后端服务
```bash
python run.py
```

后端服务将在 `http://localhost:8001` 启动
- API 文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/health

### 前端启动

1. 进入前端目录
```bash
cd D:\webmedic\frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

## 开发阶段

本项目采用分阶段开发模式：

- ✅ **阶段 1**: 项目初始化与目录骨架（当前阶段）
- ✅ **阶段 2**: 后端基础骨架与数据库接入
- ✅ **阶段 3**: 前端工作站基础页面
- ✅ **阶段 4**: 会话管理与固定患者信息
- ✅ **阶段 5**: 音频上传与 ASR 转写链路
- ✅ **阶段 6**: 结构化抽取链路
- ✅ **阶段 7**: PDF 病历索引与相似病历检索
- ✅ **阶段 8**: 病历草稿生成与临床提示引擎
- ✅ **阶段 9**: 日志、回放、打磨与 README 完整化



## 核心功能

1. **语音问诊**: 实时语音转写，区分医生/患者对话
2. **结构化抽取**: 自动提取病历要素（主诉、现病史等）
3. **相似病历检索**: 基于症状检索历史相似病历
4. **病历草稿生成**: AI 辅助生成病历草稿
5. **临床提示**: 智能提示用药风险、追问问题、建议检查
6. **会话历史**: 查看历史会话和对话记录回放
7. **文档管理**: 上传和管理医疗文档，自动索引

## 固定业务设定

- **医生**: Doctor Panython
- **患者**: 张三，男，29 岁
- **病历目录**: `D:\webmedic\backend\medical_records\`

## 开发规范

1. 严格按照《webmedic 开发技术细节文档》进行开发
2. 接口命名、表名、目录名不得随意修改
3. 所有 Prompt 必须文件化存放在 `backend/app/prompts/`
4. API 统一使用 `/api/v1` 前缀
5. 统一响应格式：`{success, message, data}`

## 许可证

本项目仅供学习和技术演示使用。

## 联系方式

如有问题，请查阅项目文档或联系开发团队。
