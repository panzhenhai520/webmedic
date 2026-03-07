# Mock 模式数据问题说明

## 问题描述

结构化病历中出现了患者没有说过的内容：
- **时间错误**：患者说"六天"，但病历写"3天"
- **位置幻觉**：患者没说"左侧"，但病历写"以左侧为主"
- **症状幻觉**：患者没说"头晕"、"恶心"、"睡眠质量下降"等，但都出现在病历中

## 问题原因

**这不是大模型幻觉，而是 Mock 模式返回的固定测试数据。**

当前系统配置：
```env
LLM_USE_MOCK=true  # 使用模拟模式
```

Mock 模式的特点：
1. **完全忽略实际对话内容**
2. **返回预设的固定数据**
3. **用于快速测试，不调用真实 API**

Mock 模式返回的固定数据（`backend/app/services/llm_service.py` 第 97-106 行）：
```python
{
    "chief_complaint": "颈部疼痛伴头晕3天",
    "present_illness": "患者3天前无明显诱因出现颈部疼痛，以左侧为主，伴有头晕，活动时加重，休息后稍缓解。疼痛呈持续性钝痛，无放射痛。伴有恶心，无呕吐。睡眠质量下降，食欲正常。",
    "past_history": "既往体健，否认高血压、糖尿病等慢性病史，否认手术史、外伤史。",
    "allergy_history": "对青霉素过敏",
    "physical_exam": "颈部活动受限，左侧颈部肌肉紧张，压痛明显。神经系统检查未见明显异常。",
    "preliminary_diagnosis": "颈椎病（神经根型）",
    "suggested_exams": "颈椎X光片、血常规、血沉",
    "warning_flags": "青霉素过敏，避免使用青霉素类抗生素"
}
```

无论患者说什么，Mock 模式都会返回这些固定内容。

---

## 解决方案

### 方案1：使用真实的 DeepSeek API（推荐）

**优点**：
- 根据实际对话内容生成病历
- 准确提取患者描述的症状
- 智能推理和补充信息

**缺点**：
- 需要消耗 API 额度
- 响应时间稍长（2-5秒）
- 可能出现真正的 LLM 幻觉（但概率较低）

**配置步骤**：

1. 修改 `.env` 文件：
```env
LLM_USE_MOCK=false  # 改为 false
```

2. 确认 DeepSeek API Key 有效：
```env
DEEPSEEK_API_KEY=sk-9cbb533c0d064d2c8fd0c9fea55eb930
```

3. 重启后端服务：
```bash
cd D:\webmedic\backend
python run.py
```

4. 测试：
   - 开始新会话
   - 录制真实对话
   - 查看结构化病历是否准确

---

### 方案2：改进 Mock 模式（用于测试）

如果只是想测试功能，不想调用真实 API，可以改进 Mock 模式，让它根据对话内容生成简单的提取结果。

**修改位置**：`backend/app/services/llm_service.py` 第 96-106 行

**改进思路**：
```python
def _generate_mock_json(self, prompt: str) -> Dict[str, Any]:
    """Mock 模式：根据 prompt 简单提取信息"""
    logger.info("使用 Mock 模式生成 JSON")

    # 简单的关键词提取
    chief_complaint = "未提及"
    if "颈" in prompt or "脖子" in prompt:
        chief_complaint = "颈部不适"
    if "头晕" in prompt:
        chief_complaint += "伴头晕"

    # 提取时间
    days = "未明确"
    if "天" in prompt:
        # 简单提取数字
        import re
        numbers = re.findall(r'(\d+)天', prompt)
        if numbers:
            days = numbers[-1] + "天"  # 取最后一次提到的天数

    return {
        "chief_complaint": chief_complaint,
        "present_illness": f"患者主诉{chief_complaint}，具体病史待补充。",
        "past_history": "待询问",
        "allergy_history": "待询问",
        "physical_exam": "待检查",
        "preliminary_diagnosis": "待诊断",
        "suggested_exams": "待完善相关检查",
        "warning_flags": "无特殊"
    }
```

**注意**：这只是简单的关键词匹配，效果远不如真实 LLM。

---

## 真实 LLM 的幻觉问题

如果使用真实的 DeepSeek API，仍然可能出现幻觉，但可以通过以下方式减少：

### 1. 优化 Prompt（已实现）

系统的 Prompt 模板（`backend/app/prompts/extract_structured_record.txt`）已经包含了防止幻觉的指令：

```
重要提示：
1. 严格基于对话内容提取信息，不要添加对话中没有的内容
2. 如果某项信息在对话中未提及，请填写"未提及"或"待询问"
3. 不要根据症状推测其他症状
4. 时间、位置等关键信息必须准确
```

### 2. 使用更严格的 Temperature

降低 temperature 参数可以减少随机性和幻觉：

```python
# 在 extract_service.py 中
result_json = llm_service.generate_json(
    prompt=prompt,
    temperature=0.3  # 降低到 0.3（默认 0.7）
)
```

### 3. 后处理验证

可以添加验证逻辑，检查生成的内容是否在原始对话中出现：

```python
def validate_extraction(dialogue_text: str, extracted_data: dict) -> dict:
    """验证提取的数据是否在对话中出现"""
    # 检查关键信息是否在对话中
    for key, value in extracted_data.items():
        if value and value != "未提及":
            # 简单检查：关键词是否在对话中
            if not any(word in dialogue_text for word in value.split()[:3]):
                logger.warning(f"可能的幻觉：{key} = {value}")
    return extracted_data
```

---

## 推荐配置

### 开发测试阶段
```env
LLM_USE_MOCK=true   # 使用 Mock 模式，快速测试
ASR_USE_MOCK=true   # 使用 Mock 模式，不需要录音
```

### 功能演示阶段
```env
LLM_USE_MOCK=false  # 使用真实 API，准确提取
ASR_USE_MOCK=false  # 使用真实语音识别
ASR_ENGINE=dolphin  # 使用本地 Dolphin，节省成本
```

### 生产部署阶段
```env
LLM_USE_MOCK=false  # 使用真实 API
ASR_USE_MOCK=false  # 使用真实语音识别
ASR_ENGINE=whisper  # 使用 OpenAI Whisper，准确度更高
```

---

## 测试步骤

### 测试真实 LLM 提取

1. **修改配置**：
```bash
# 编辑 backend/.env
LLM_USE_MOCK=false
```

2. **重启后端**：
```bash
cd D:\webmedic\backend
python run.py
```

3. **测试对话**：
   - 开始新会话
   - 录制对话：
     ```
     医生：哪里不舒服？
     患者：颈椎痛
     医生：多久了？
     患者：六天了
     ```

4. **查看结果**：
   - 检查结构化病历
   - 确认时间是"六天"而不是"三天"
   - 确认没有患者未提及的症状

### 对比 Mock 和真实 API

| 项目 | Mock 模式 | 真实 API |
|------|----------|----------|
| 数据来源 | 固定预设数据 | 实际对话内容 |
| 准确性 | 与对话无关 | 高度准确 |
| 响应速度 | 极快（<0.1秒） | 较慢（2-5秒） |
| 成本 | 免费 | 消耗 API 额度 |
| 适用场景 | 功能测试 | 实际使用 |

---

## 常见问题

### Q1: 真实 API 会不会也出现幻觉？

**A**: 可能会，但概率较低。DeepSeek 等现代 LLM 在医疗领域的准确性较高，特别是在有明确 Prompt 指导的情况下。如果出现幻觉，可以：
- 优化 Prompt 模板
- 降低 temperature 参数
- 添加后处理验证

### Q2: 如何判断是 Mock 模式还是真实 API？

**A**: 查看后端日志：
```bash
# Mock 模式会显示：
使用 Mock 模式生成 JSON

# 真实 API 会显示：
使用真实 DeepSeek API 生成 JSON
DeepSeek API 返回内容: ...
```

### Q3: DeepSeek API 费用如何？

**A**: DeepSeek 的费用相对较低：
- 输入：约 ¥0.001/1K tokens
- 输出：约 ¥0.002/1K tokens
- 一次结构化提取约消耗 500-1000 tokens
- 成本约 ¥0.001-0.003/次

### Q4: 可以混合使用吗？

**A**: 可以。例如：
```env
ASR_USE_MOCK=true   # 语音识别用 Mock（测试时）
LLM_USE_MOCK=false  # 结构化提取用真实 API（确保准确）
```

---

## 总结

1. **当前问题**：使用 Mock 模式导致返回固定数据，与实际对话无关
2. **解决方案**：修改 `.env` 设置 `LLM_USE_MOCK=false`，使用真实 DeepSeek API
3. **注意事项**：真实 API 也可能出现幻觉，但概率较低，可通过优化 Prompt 减少
4. **推荐配置**：演示和生产环境使用真实 API，开发测试使用 Mock 模式
