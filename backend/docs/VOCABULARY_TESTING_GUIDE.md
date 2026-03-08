# 词库维护系统测试指南

## 一、数据库初始化（✅ 已完成）

### 1.1 创建数据库表
```bash
cd D:\webmedic\backend
venv\Scripts\python.exe scripts\create_vocabulary_tables.py
```

**结果：**
- ✅ medical_vocabulary 表已创建
- ✅ icd_codes 表已创建
- ✅ surgery_codes 表已创建

### 1.2 导入初始数据
```bash
venv\Scripts\python.exe scripts\init_vocabulary_data.py
```

**结果：**
- ✅ 医学词汇：121条
- ✅ ICD编码：14条
- ✅ 手术编码：12条

### 1.3 验证数据
```bash
# 查询医学词汇总数
venv\Scripts\python.exe -c "from app.db.session import SessionLocal; from app.models.medical_vocabulary import MedicalVocabulary; db = SessionLocal(); print(f'总数: {db.query(MedicalVocabulary).count()}'); db.close()"

# 查询骨科词汇
venv\Scripts\python.exe -c "from app.db.session import SessionLocal; from app.models.medical_vocabulary import MedicalVocabulary; db = SessionLocal(); vocabs = db.query(MedicalVocabulary).filter(MedicalVocabulary.specialty == '骨科').limit(5).all(); [print(v.standard_name) for v in vocabs]; db.close()"
```

## 二、后端API测试（✅ 已完成）

### 2.1 测试词汇列表API
```bash
cd D:\webmedic\backend
curl -s http://localhost:8001/api/v1/vocabulary/vocabulary/list -X POST -H "Content-Type: application/json" -d @test_request.json
```

**test_request.json:**
```json
{"page":1,"page_size":5,"specialty":"骨科"}
```

**预期结果：**
```json
{
  "success": true,
  "message": "获取词汇列表成功",
  "data": {
    "total": 30,
    "page": 1,
    "page_size": 5,
    "items": [...]
  }
}
```

### 2.2 测试相似词检查API
```bash
curl -s http://localhost:8001/api/v1/vocabulary/vocabulary/check-similar -X POST -H "Content-Type: application/json" -d @test_similar.json
```

**test_similar.json:**
```json
{"text":"肱骨","category":"body_parts"}
```

**预期结果：**
```json
{
  "success": true,
  "message": "检查完成",
  "data": {
    "has_similar": true,
    "similar_items": [
      {
        "id": 37,
        "standard_name": "肱骨",
        "keywords": ["肱骨"],
        "similarity": 1.0
      }
    ]
  }
}
```

## 三、前端页面测试（✅ 已完成）

### 3.1 启动前端服务
```bash
cd D:\webmedic\frontend
npm run dev
```

### 3.2 访问词库维护页面
打开浏览器访问：
```
http://localhost:5173/vocabulary
```

### 3.3 功能测试清单

#### 基础功能
- [ ] 页面正常加载
- [ ] 显示词汇列表
- [ ] 分页功能正常
- [ ] 筛选功能（分类、专科）
- [ ] 搜索功能

#### 新增词汇
- [ ] 点击"新增词汇"按钮
- [ ] 填写表单：
  - 分类：身体部位
  - 专科：骨科
  - 标准名称：测试词汇
  - 关键词：添加1-2个关键词
  - 描述：可选
- [ ] 输入标准名称后自动检查相似词
- [ ] 如果存在相似词，显示警告
- [ ] 点击"保存"按钮
- [ ] 验证是否创建成功

#### 编辑词汇
- [ ] 点击某个词汇的"编辑"按钮
- [ ] 修改关键词或描述
- [ ] 点击"保存"按钮
- [ ] 验证是否更新成功

#### 删除词汇
- [ ] 点击某个词汇的"删除"按钮
- [ ] 确认删除对话框
- [ ] 点击"确定"
- [ ] 验证是否删除成功

#### 相似词检查
- [ ] 新增词汇时，输入"肱骨"
- [ ] 失焦后自动检查相似词
- [ ] 应该显示警告：发现相似词汇
- [ ] 显示相似度：100%

#### 关键词管理
- [ ] 点击"+ 添加关键词"
- [ ] 输入关键词并回车
- [ ] 验证关键词是否添加
- [ ] 点击关键词的"×"删除
- [ ] 验证关键词是否删除

## 四、导航菜单测试

### 4.1 主工作站页面
访问：http://localhost:5173/

**验证：**
- [ ] 顶部导航栏显示"系统维护"菜单
- [ ] 鼠标悬停显示下拉菜单
- [ ] 下拉菜单包含：
  - 医学词库（可点击）
  - ICD编码（禁用）
  - 手术编码（禁用）

### 4.2 菜单跳转
- [ ] 点击"系统维护" → "医学词库"
- [ ] 跳转到词库维护页面
- [ ] 点击页面左上角返回按钮
- [ ] 返回主工作站页面

## 五、数据验证

### 5.1 骨科词汇验证
在词库维护页面：
1. 专科筛选选择"骨科"
2. 点击"搜索"
3. 验证显示的词汇包括：
   - 肱骨
   - 桡骨
   - 尺骨
   - 颈椎
   - 腰椎
   - 等等...

### 5.2 搜索功能验证
1. 在搜索框输入"肱"
2. 点击"搜索"
3. 验证只显示包含"肱"的词汇（如：肱骨）

### 5.3 分类筛选验证
1. 分类选择"症状"
2. 点击"搜索"
3. 验证显示的都是症状类词汇（疼痛、头晕、恶心等）

## 六、已知问题和限制

### 6.1 当前实现
- ✅ 医学词汇维护（完整功能）
- ⏳ ICD编码维护（菜单已添加，功能待开发）
- ⏳ 手术编码维护（菜单已添加，功能待开发）

### 6.2 待开发功能
- 批量导入（Excel/CSV）
- 批量导出
- 审核流程
- 修改历史记录
- 权限控制

## 七、故障排查

### 7.1 后端API不响应
```bash
# 检查后端服务是否运行
curl http://localhost:8001/health

# 如果没有响应，重启后端
cd D:\webmedic\backend
start.bat
```

### 7.2 前端页面空白
```bash
# 检查前端服务是否运行
# 浏览器访问 http://localhost:5173

# 如果没有响应，重启前端
cd D:\webmedic\frontend
npm run dev
```

### 7.3 数据库连接错误
```bash
# 检查数据库配置
# 编辑 D:\webmedic\backend\.env
# 确认 DB_HOST, DB_USER, DB_PASSWORD, DB_NAME 正确
```

### 7.4 词汇列表为空
```bash
# 重新运行数据初始化
cd D:\webmedic\backend
venv\Scripts\python.exe scripts\init_vocabulary_data.py
```

## 八、下一步计划

### 8.1 短期（本周）
- [ ] 完善ICD编码维护页面
- [ ] 完善手术编码维护页面
- [ ] 添加批量导入功能

### 8.2 中期（本月）
- [ ] Mock模式集成（从数据库动态加载）
- [ ] 添加审核流程
- [ ] 添加修改历史记录

### 8.3 长期（下月）
- [ ] AI辅助生成关键词
- [ ] 智能推荐相关词汇
- [ ] 统计分析功能

## 九、联系支持

如遇到问题，请检查：
1. 后端日志：`D:\webmedic\backend\logs\webmedic.log`
2. 浏览器控制台（F12）
3. 网络请求（F12 → Network）

## 十、成功标准

系统正常运行的标志：
- ✅ 数据库表已创建
- ✅ 初始数据已导入（121条词汇）
- ✅ 后端API正常响应
- ✅ 前端页面正常显示
- ✅ 可以新增、编辑、删除词汇
- ✅ 相似词检查功能正常
- ✅ 导航菜单正常工作
