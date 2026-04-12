API Debug Tool 质量保障平台 - Phase 3 详细设计文档
======================================

一、Phase 3 概述
------------

### 1.1 阶段定位

在 Phase 2 建立的自动化测试能力基础上，Phase 3 重点**向左扩展**到开发阶段，打通代码质量与测试质量的关联，形成从代码到接口的完整质量闭环。

### 1.2 核心目标

| 目标        | 说明                 | 成功标准                     |
| --------- | ------------------ | ------------------------ |
| 单元测试集成    | 对接主流单测框架，统一展示单测结果  | 支持 Python/Java/JS 单测报告解析 |
| 代码覆盖率采集   | 解析覆盖率报告，建立代码-用例映射  | 覆盖率数据入库，可视化展示            |
| 用例-代码关联   | 建立 API 用例与源代码的双向追溯 | 接口可查看对应代码覆盖率             |
| 缺陷管理模块    | 内置轻量级缺陷工作流         | 支持缺陷 CRUD、状态流转           |
| 第三方缺陷系统对接 | 插件化对接 Jira/TAPD/禅道 | 一键提缺陷，双向状态同步             |
| 质量门禁      | CI/CD 流水线中的质量检查点   | 支持覆盖率阈值、用例通过率门禁          |

### 1.3 与 Phase 1/2 的关系

text

Phase 1 产出                Phase 2 产出                Phase 3 扩展
─────────────────────────────────────────────────────────────────────
用例管理 ──────────────────────────────────────────► 用例-代码关联
环境管理 ──────────────────────────────────────────► CI 环境集成
执行记录 ──────────────────────────────────────────► 缺陷创建依据
定时任务 ──────────────────────────────────────────► 质量巡检任务
报告生成 ──────────────────────────────────────────► 质量报告融合
CLI 工具 ──────────────────────────────────────────► 质量门禁 CLI

### 1.4 不包含内容

* 多用户与权限（Phase 4）

* 智能分析与 AI 辅助（Phase 4）

* 性能基线与容量评估（Phase 4）

* * *

二、系统架构扩展
--------

### 2.1 Phase 3 架构全景图

text

┌─────────────────────────────────────────────────────────────────────────┐
│                              Phase 3 新增模块                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  覆盖率解析器    │  │  缺陷管理器      │  │  质量门禁引擎            │ │
│  │  CoverageParser │  │  DefectManager  │  │  QualityGateEngine      │ │
│  └────────┬────────┘  └────────┬────────┘  └───────────┬─────────────┘ │
│           │                    │                       │                │
│           ▼                    ▼                       ▼                │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    Phase 1/2 核心服务层                            │ │
│  │  变量引擎 │ 断言引擎 │ 请求执行器 │ 场景执行器 │ 定时调度器         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      Phase 3 新增服务                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │ │
│  │  │ 单测结果解析  │  │ 代码仓库集成  │  │  第三方缺陷适配器         │ │ │
│  │  │ UnitTest     │  │ Git          │  │  DefectAdapter           │ │ │
│  │  │ Parser       │  │ Integration  │  │  (Jira/TAPD/禅道)         │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        数据存储层（Phase 3 扩展）                   │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │ │
│  │  │ 代码仓库表  │ │ 覆盖率记录表 │ │ 缺陷表      │ │ 用例-代码映射表 │  │ │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        外部系统集成层                               │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │ │
│  │  │ GitLab CI  │ │ Jenkins    │ │ Jira/TAPD  │ │ SonarQube      │  │ │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

### 2.2 新增模块职责说明

| 模块           | 职责                             | 依赖           |
| ------------ | ------------------------------ | ------------ |
| **单测结果解析器**  | 解析 JUnit/TestNG/Pytest 等单测报告格式 | XML/JSON 解析库 |
| **覆盖率解析器**   | 解析 lcov/cobertura/JaCoCo 覆盖率报告 | 覆盖率报告格式库     |
| **代码仓库集成**   | 管理 Git 仓库信息，获取代码变更             | GitPython    |
| **用例-代码映射**  | 建立 API 用例与源代码文件/方法的关联          | 映射规则引擎       |
| **缺陷管理器**    | 内置缺陷工作流，CRUD 操作                | 数据库          |
| **第三方缺陷适配器** | 插件化对接 Jira/TAPD/禅道             | 各系统 API SDK  |
| **质量门禁引擎**   | 执行门禁规则判断，返回通过/阻断               | 规则引擎         |

* * *

三、数据模型扩展
--------

### 3.1 Phase 3 新增表 ER 图

text

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   TestCase      │       │  CodeRepository │       │  CodeFile       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │       │ id              │
│ name            │       │ name            │       │ repository_id   │
│ code_file_id    │◄──────│ url             │       │ file_path       │
│ code_method     │       │ branch          │       │ file_name       │
└─────────────────┘       │ last_sync_at    │       │ package_path    │
                          └─────────────────┘       │ language        │
                                   │                └────────┬────────┘
                                   │ 1:N                     │
                                   │                         │ 1:N
                                   ▼                         ▼
                          ┌─────────────────┐       ┌─────────────────┐
                          │ CoverageRecord  │       │  CodeMethod     │
                          ├─────────────────┤       ├─────────────────┤
                          │ id              │       │ id              │
                          │ repository_id   │       │ file_id         │
                          │ commit_hash     │       │ method_name     │
                          │ file_path       │       │ line_start      │
                          │ line_coverage   │       │ line_end        │
                          │ branch_coverage │       │ complexity      │
                          │ total_lines     │       └─────────────────┘
                          │ covered_lines   │
                          │ uncovered_lines │
                          │ report_date     │
                          └─────────────────┘
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Defect        │       │ DefectAttachment│       │ DefectComment   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │       │ id              │
│ title           │       │ defect_id       │       │ defect_id       │
│ description     │       │ file_name       │       │ content         │
│ severity        │       │ file_path       │       │ author          │
│ priority        │       │ file_size       │       │ created_at      │
│ status          │       │ uploaded_at     │       └─────────────────┘
│ assignee        │       └─────────────────┘
│ reporter        │
│ execution_log_id│◄── 关联执行记录
│ case_id         │◄── 关联用例
│ environment     │
│ steps_to_repro  │
│ expected_result │
│ actual_result   │
│ resolution      │
│ resolved_at     │
│ created_at      │
│ updated_at      │
└─────────────────┘
┌─────────────────────────────────────────┐
│           QualityGate                   │
├─────────────────────────────────────────┤
│ id                                      │
│ name                                    │
│ description                             │
│ project_id (预留 Phase 4)                │
│ rules (JSON 数组)                       │
│ enabled                                 │
│ created_at                              │
│ updated_at                              │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│         QualityGateResult               │
├─────────────────────────────────────────┤
│ id                                      │
│ gate_id                                 │
│ trigger_type (commit/pr/deploy)         │
│ trigger_ref (commit hash / PR id)       │
│ status (passed/failed/warning)          │
│ rule_results (JSON)                     │
│ triggered_at                            │
└─────────────────────────────────────────┘

### 3.2 新增表详细设计

#### 3.2.1 代码仓库表 `code_repository`

| 字段           | 类型           | 约束                        | 说明                        |
| ------------ | ------------ | ------------------------- | ------------------------- |
| id           | INTEGER      | PRIMARY KEY               | 自增主键                      |
| name         | VARCHAR(200) | NOT NULL                  | 仓库名称                      |
| url          | VARCHAR(500) | NOT NULL                  | Git 仓库地址                  |
| branch       | VARCHAR(100) | DEFAULT 'main'            | 默认分支                      |
| provider     | VARCHAR(20)  |                           | github/gitlab/gitee/local |
| access_token | VARCHAR(200) |                           | 访问令牌（加密存储）                |
| local_path   | VARCHAR(500) |                           | 本地克隆路径                    |
| last_sync_at | TIMESTAMP    |                           | 最后同步时间                    |
| created_at   | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                      |
| updated_at   | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                      |

#### 3.2.2 代码文件表 `code_file`

| 字段               | 类型           | 约束                        | 说明                        |
| ---------------- | ------------ | ------------------------- | ------------------------- |
| id               | INTEGER      | PRIMARY KEY               | 自增主键                      |
| repository_id    | INTEGER      | FOREIGN KEY               | 关联仓库 ID                   |
| file_path        | VARCHAR(500) | NOT NULL                  | 文件相对路径                    |
| file_name        | VARCHAR(200) | NOT NULL                  | 文件名                       |
| package_path     | VARCHAR(500) |                           | 包路径（Java/Python）          |
| language         | VARCHAR(20)  |                           | python/java/javascript/go |
| last_commit_hash | VARCHAR(64)  |                           | 最后提交 Hash                 |
| created_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                      |
| updated_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                      |

**索引**：`idx_code_file_repo_path` ON (repository_id, file_path)

#### 3.2.3 代码方法表 `code_method`

| 字段          | 类型           | 约束                        | 说明      |
| ----------- | ------------ | ------------------------- | ------- |
| id          | INTEGER      | PRIMARY KEY               | 自增主键    |
| file_id     | INTEGER      | FOREIGN KEY               | 关联文件 ID |
| method_name | VARCHAR(200) | NOT NULL                  | 方法名/函数名 |
| class_name  | VARCHAR(200) |                           | 类名      |
| line_start  | INTEGER      |                           | 起始行号    |
| line_end    | INTEGER      |                           | 结束行号    |
| complexity  | INTEGER      |                           | 圈复杂度    |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间    |
| updated_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间    |

#### 3.2.4 覆盖率记录表 `coverage_record`

| 字段                | 类型           | 约束                        | 说明                    |
| ----------------- | ------------ | ------------------------- | --------------------- |
| id                | INTEGER      | PRIMARY KEY               | 自增主键                  |
| repository_id     | INTEGER      | FOREIGN KEY               | 关联仓库 ID               |
| commit_hash       | VARCHAR(64)  | NOT NULL                  | 提交 Hash               |
| file_path         | VARCHAR(500) | NOT NULL                  | 文件路径                  |
| line_coverage     | FLOAT        |                           | 行覆盖率（0-100）           |
| branch_coverage   | FLOAT        |                           | 分支覆盖率                 |
| function_coverage | FLOAT        |                           | 函数覆盖率                 |
| total_lines       | INTEGER      |                           | 总行数                   |
| covered_lines     | INTEGER      |                           | 覆盖行数                  |
| uncovered_lines   | TEXT         |                           | JSON 数组，未覆盖行号         |
| report_format     | VARCHAR(20)  |                           | lcov/cobertura/jacoco |
| report_date       | DATE         | NOT NULL                  | 报告日期                  |
| created_at        | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                  |

**索引**：

* `idx_coverage_repo_commit` ON (repository_id, commit_hash)

* `idx_coverage_repo_date` ON (repository_id, report_date)

#### 3.2.5 缺陷表 `defect`

| 字段                 | 类型           | 约束                        | 说明                                        |
| ------------------ | ------------ | ------------------------- | ----------------------------------------- |
| id                 | INTEGER      | PRIMARY KEY               | 自增主键                                      |
| title              | VARCHAR(500) | NOT NULL                  | 缺陷标题                                      |
| description        | TEXT         |                           | 缺陷描述                                      |
| severity           | VARCHAR(20)  | NOT NULL                  | 严重程度：critical/high/medium/low             |
| priority           | VARCHAR(20)  | NOT NULL                  | 优先级：urgent/high/medium/low                |
| status             | VARCHAR(20)  | DEFAULT 'open'            | open/in_progress/resolved/closed/reopened |
| defect_type        | VARCHAR(30)  |                           | 功能/性能/安全/兼容性/UI                           |
| assignee           | VARCHAR(100) |                           | 处理人                                       |
| reporter           | VARCHAR(100) | NOT NULL                  | 报告人                                       |
| execution_log_id   | INTEGER      | FOREIGN KEY               | 关联执行记录                                    |
| case_id            | INTEGER      | FOREIGN KEY               | 关联用例                                      |
| scenario_id        | INTEGER      | FOREIGN KEY               | 关联场景                                      |
| environment        | VARCHAR(50)  |                           | 发现环境                                      |
| steps_to_reproduce | TEXT         |                           | 复现步骤                                      |
| expected_result    | TEXT         |                           | 期望结果                                      |
| actual_result      | TEXT         |                           | 实际结果                                      |
| resolution         | TEXT         |                           | 解决方案                                      |
| resolved_at        | TIMESTAMP    |                           | 解决时间                                      |
| external_id        | VARCHAR(100) |                           | 外部系统 ID（Jira 等）                           |
| external_url       | VARCHAR(500) |                           | 外部系统链接                                    |
| created_at         | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                                      |
| updated_at         | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                                      |

**索引**：

* `idx_defect_status` ON (status)

* `idx_defect_assignee` ON (assignee)

* `idx_defect_case` ON (case_id)

#### 3.2.6 缺陷附件表 `defect_attachment`

| 字段          | 类型           | 约束                        | 说明       |
| ----------- | ------------ | ------------------------- | -------- |
| id          | INTEGER      | PRIMARY KEY               | 自增主键     |
| defect_id   | INTEGER      | FOREIGN KEY               | 关联缺陷 ID  |
| file_name   | VARCHAR(200) | NOT NULL                  | 文件名      |
| file_path   | VARCHAR(500) | NOT NULL                  | 存储路径     |
| file_size   | INTEGER      |                           | 文件大小（字节） |
| file_type   | VARCHAR(50)  |                           | MIME 类型  |
| uploaded_at | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 上传时间     |

#### 3.2.7 缺陷评论表 `defect_comment`

| 字段         | 类型           | 约束                        | 说明      |
| ---------- | ------------ | ------------------------- | ------- |
| id         | INTEGER      | PRIMARY KEY               | 自增主键    |
| defect_id  | INTEGER      | FOREIGN KEY               | 关联缺陷 ID |
| content    | TEXT         | NOT NULL                  | 评论内容    |
| author     | VARCHAR(100) | NOT NULL                  | 评论人     |
| created_at | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间    |

#### 3.2.8 质量门禁表 `quality_gate`

| 字段          | 类型           | 约束                        | 说明           |
| ----------- | ------------ | ------------------------- | ------------ |
| id          | INTEGER      | PRIMARY KEY               | 自增主键         |
| name        | VARCHAR(200) | NOT NULL                  | 门禁名称         |
| description | TEXT         |                           | 门禁描述         |
| rules       | TEXT         | NOT NULL                  | JSON 数组，门禁规则 |
| enabled     | BOOLEAN      | DEFAULT 1                 | 是否启用         |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间         |
| updated_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间         |

**rules 字段结构**：

json

[
  {
    "id": "rule_1",
    "type": "coverage",
    "metric": "line_coverage",
    "operator": "gte",
    "threshold": 80,
    "scope": "overall"
  },
  {
    "id": "rule_2",
    "type": "test_pass_rate",
    "operator": "gte",
    "threshold": 95,
    "scope": "scenario:1"
  },
  {
    "id": "rule_3",
    "type": "response_time",
    "operator": "lte",
    "threshold": 1000,
    "scope": "case:5"
  },
  {
    "id": "rule_4",
    "type": "critical_defects",
    "operator": "eq",
    "threshold": 0
  }
]

#### 3.2.9 质量门禁结果表 `quality_gate_result`

| 字段           | 类型           | 约束                        | 说明                        |
| ------------ | ------------ | ------------------------- | ------------------------- |
| id           | INTEGER      | PRIMARY KEY               | 自增主键                      |
| gate_id      | INTEGER      | FOREIGN KEY               | 关联门禁 ID                   |
| trigger_type | VARCHAR(20)  |                           | commit/pr/deploy/schedule |
| trigger_ref  | VARCHAR(200) |                           | 触发引用（commit/PR ID）        |
| status       | VARCHAR(20)  | NOT NULL                  | passed/failed/warning     |
| rule_results | TEXT         |                           | JSON 数组，各规则结果             |
| summary      | TEXT         |                           | 结果摘要                      |
| triggered_at | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 触发时间                      |

#### 3.2.10 用例表扩展字段

Phase 1 的 `test_case` 表新增以下字段：

| 字段                 | 类型           | 说明          |
| ------------------ | ------------ | ----------- |
| code_file_id       | INTEGER      | 关联的代码文件 ID  |
| code_method_id     | INTEGER      | 关联的代码方法 ID  |
| coverage_threshold | INTEGER      | 该用例对应的覆盖率阈值 |
| unit_test_path     | VARCHAR(500) | 对应的单元测试文件路径 |

* * *

四、核心引擎设计
--------

### 4.1 单测结果解析器

**设计目标**：解析主流单元测试框架的报告格式，统一存储和展示

**支持的框架与格式**：

| 语言         | 框架       | 报告格式             | 解析方式        |
| ---------- | -------- | ---------------- | ----------- |
| Python     | pytest   | JUnit XML        | XML 解析      |
| Python     | unittest | JUnit XML        | XML 解析      |
| Java       | JUnit    | JUnit XML        | XML 解析      |
| Java       | TestNG   | TestNG XML       | XML 解析      |
| JavaScript | Jest     | JUnit XML        | XML 解析      |
| JavaScript | Mocha    | JUnit XML / JSON | XML/JSON 解析 |
| Go         | testing  | JSON             | JSON 解析     |

**处理流程**：

text

┌─────────────────────────────────────────────────────────────┐
│                  单测报告解析流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 接收报告文件（上传或 CI 回调）                            │
│         │                                                   │
│         ▼                                                   │
│  2. 识别报告格式（XML/JSON）                                 │
│         │                                                   │
│         ▼                                                   │
│  3. 解析测试用例                                             │
│     - 测试类/文件                                            │
│     - 测试方法                                                │
│     - 执行状态（通过/失败/跳过）                               │
│     - 执行耗时                                                │
│     - 失败信息                                                │
│         │                                                   │
│         ▼                                                   │
│  4. 关联代码文件/方法                                         │
│     - 根据类名/方法名匹配                                     │
│     - 存储到 code_method 表                                  │
│         │                                                   │
│         ▼                                                   │
│  5. 存储单测执行记录                                          │
│         │                                                   │
│         ▼                                                   │
│  6. 更新质量指标                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.2 覆盖率解析器

**设计目标**：解析多种覆盖率报告格式，建立代码覆盖率数据仓库

**支持的格式**：

| 格式        | 工具                | 语言          | 文件示例                                     |
| --------- | ----------------- | ----------- | ---------------------------------------- |
| LCOV      | Jest/Istanbul/Go  | JS/TS/Go    | coverage/[lcov.info](https://lcov.info/) |
| Cobertura | pytest-cov/JaCoCo | Python/Java | coverage.xml                             |
| JaCoCo    | JaCoCo            | Java        | jacoco.xml                               |
| HTML      | 通用                | 通用          | index.html（解析 DOM）                       |

**覆盖率指标**：

| 指标    | 说明       | 计算方式         |
| ----- | -------- | ------------ |
| 行覆盖率  | 被执行代码行占比 | 覆盖行数 / 总行数   |
| 分支覆盖率 | 被执行分支占比  | 覆盖分支数 / 总分支数 |
| 函数覆盖率 | 被调用函数占比  | 覆盖函数数 / 总函数数 |
| 语句覆盖率 | 被执行语句占比  | 覆盖语句数 / 总语句数 |

**处理流程**：

text

┌─────────────────────────────────────────────────────────────┐
│                  覆盖率报告解析流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 接收覆盖率报告（CI 上传或定时拉取）                         │
│         │                                                   │
│         ▼                                                   │
│  2. 识别报告格式，选择解析器                                   │
│         │                                                   │
│         ▼                                                   │
│  3. 解析文件级覆盖率数据                                       │
│     - 文件路径                                                │
│     - 行覆盖情况                                              │
│     - 分支覆盖情况                                            │
│         │                                                   │
│         ▼                                                   │
│  4. 与代码仓库文件关联                                         │
│     - 匹配 code_file 表                                      │
│     - 不存在则创建                                            │
│         │                                                   │
│         ▼                                                   │
│  5. 存储覆盖率记录                                            │
│     - 关联 commit_hash                                       │
│     - 记录未覆盖行号                                          │
│         │                                                   │
│         ▼                                                   │
│  6. 触发覆盖率变化分析                                         │
│     - 与上一次对比                                            │
│     - 识别新增未覆盖代码                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.3 用例-代码关联引擎

**设计目标**：建立 API 测试用例与源代码的双向映射

**关联方式**：

| 方式       | 说明                     | 配置示例                           | 准确度    |
| -------- | ---------------------- | ------------------------------ | ------ |
| **手动关联** | 在用例编辑器中手动选择代码文件/方法     | 选择 Controller 文件               | 100%   |
| **注解关联** | 代码中使用注解标记对应的 API 用例    | `@ApiCase("TC-001")`           | 100%   |
| **路径匹配** | 根据 URL 路径推断 Controller | `/api/user` → `UserController` | 70-90% |
| **智能推荐** | 根据请求/响应结构匹配代码          | AI 相似度计算                       | 50-80% |

**路径匹配规则**：

text

┌─────────────────────────────────────────────────────────────┐
│                    路径匹配规则示例                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  API URL                    推断的代码文件                    │
│  ─────────────────────────────────────────────────────────  │
│  GET /api/users             UserController.list()           │
│  POST /api/users            UserController.create()         │
│  GET /api/users/{id}        UserController.get()            │
│  PUT /api/users/{id}        UserController.update()         │
│  DELETE /api/users/{id}     UserController.delete()         │
│                                                             │
│  匹配逻辑：                                                  │
│  1. 提取 URL 中的资源名（users）                              │
│  2. 转换为类名（UserController）                              │
│  3. 根据 HTTP 方法匹配方法名                                  │
│     GET /list    → list / getAll / index                    │
│     GET /{id}    → get / show / detail                      │
│     POST         → create / store / save                    │
│     PUT/PATCH    → update / modify                          │
│     DELETE       → delete / remove / destroy                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

**关联数据流**：

text

┌─────────────────────────────────────────────────────────────┐
│                  用例-代码关联数据流                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    关联     ┌──────────┐    分析     ┌──────────┐
│  │ API 用例 │ ◄────────► │ 代码文件 │ ◄─────────► │ 覆盖率   │
│  └──────────┘            └──────────┘            └──────────┘
│       │                       │                        │     │
│       │                       │                        │     │
│       ▼                       ▼                        ▼     │
│  ┌──────────┐            ┌──────────┐            ┌──────────┐ │
│  │ 执行结果 │            │ 代码变更 │            │ 未覆盖行 │ │
│  └──────────┘            └──────────┘            └──────────┘ │
│                                                             │
│  应用场景：                                                  │
│  • 接口测试失败 → 查看关联代码变更记录                         │
│  • 代码覆盖率低 → 推荐补充 API 用例                           │
│  • 代码变更 → 推荐执行相关 API 用例                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.4 缺陷管理器

**设计目标**：内置轻量级缺陷管理，支持与第三方系统双向同步

**缺陷工作流**：

text

┌─────────────────────────────────────────────────────────────┐
│                      缺陷状态流转图                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        ┌──────────┐                          │
│                        │  新建    │                          │
│                        │  open    │                          │
│                        └────┬─────┘                          │
│                             │                                │
│                             ▼                                │
│                        ┌──────────┐                          │
│                        │  处理中   │                          │
│                        │in_progress│                          │
│                        └────┬─────┘                          │
│                             │                                │
│              ┌──────────────┼──────────────┐                 │
│              │              │              │                 │
│              ▼              ▼              ▼                 │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│        │  已解决   │  │  拒绝    │  │  延期    │            │
│        │ resolved │  │ rejected │  │ deferred │            │
│        └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│             │             │             │                   │
│             │    ┌────────┴────────┐    │                   │
│             │    │                 │    │                   │
│             ▼    ▼                 ▼    ▼                   │
│        ┌──────────┐          ┌──────────┐                  │
│        │  重新打开 │          │   关闭   │                  │
│        │ reopened │◄─────────│  closed  │                  │
│        └──────────┘          └──────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

**一键提缺陷功能**：

text

┌─────────────────────────────────────────────────────────────┐
│                    一键提缺陷流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户在测试结果页点击「提缺陷」                                 │
│         │                                                   │
│         ▼                                                   │
│  系统自动填充：                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • 标题：[API] 接口 xxx 返回异常                        │   │
│  │ • 环境：测试环境                                       │   │
│  │ • 复现步骤：请求方法、URL、Headers、Body（脱敏）         │   │
│  │ • 实际结果：响应状态码、响应体                          │   │
│  │ • 附件：请求/响应截图、cURL 命令                        │   │
│  │ • 关联用例：自动关联当前用例                            │   │
│  │ • 关联执行记录：自动关联 execution_log_id                │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  用户补充：                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • 期望结果                                             │   │
│  │ • 严重程度/优先级                                      │   │
│  │ • 指派人                                               │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  提交缺陷 → 同步到第三方系统（如已配置）                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.5 第三方缺陷系统适配器

**设计目标**：插件化对接主流缺陷管理系统

**适配器接口**：

| 方法                           | 说明     |
| ---------------------------- | ------ |
| `create_defect(defect)`      | 创建缺陷   |
| `update_defect(id, updates)` | 更新缺陷   |
| `get_defect(id)`             | 获取缺陷详情 |
| `add_comment(id, comment)`   | 添加评论   |
| `add_attachment(id, file)`   | 添加附件   |
| `get_statuses()`             | 获取状态列表 |
| `get_users()`                | 获取用户列表 |

**支持的系统**：

| 系统            | 适配方式        | 同步方向 |
| ------------- | ----------- | ---- |
| Jira          | REST API    | 双向   |
| TAPD          | Open API    | 双向   |
| 禅道            | REST API    | 双向   |
| GitHub Issues | GraphQL API | 双向   |
| GitLab Issues | REST API    | 双向   |

**同步策略**：

text

┌─────────────────────────────────────────────────────────────┐
│                    缺陷双向同步策略                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  本地 → 远程：                                               │
│  - 创建缺陷时，同步到远程系统                                  │
│  - 状态变更时，同步到远程系统                                  │
│  - 添加评论/附件时，同步到远程系统                             │
│                                                             │
│  远程 → 本地：                                               │
│  - 定时轮询远程系统变更                                        │
│  - Webhook 实时接收变更通知                                   │
│  - 同步状态、评论、附件                                        │
│                                                             │
│  冲突处理：                                                  │
│  - 以时间戳较新的为准                                          │
│  - 冲突时记录日志，人工介入                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.6 质量门禁引擎

**设计目标**：在 CI/CD 流水线中执行质量检查，决定是否允许继续

**门禁类型**：

| 类型     | 说明                    | 适用阶段                  |
| ------ | --------------------- | --------------------- |
| 代码提交门禁 | 代码 push 时触发           | pre-commit / pre-push |
| PR 门禁  | Pull Request 创建/更新时触发 | PR 检查                 |
| 部署门禁   | 部署前检查                 | 预发布环境                 |
| 发布门禁   | 生产发布前检查               | 生产发布                  |

**支持的门禁规则**：

| 规则类型  | 指标         | 示例              |
| ----- | ---------- | --------------- |
| 覆盖率规则 | 行覆盖率/分支覆盖率 | 整体行覆盖率 ≥ 80%    |
|       | 增量覆盖率      | 新增代码覆盖率 ≥ 90%   |
|       | 文件覆盖率      | 核心文件覆盖率 ≥ 95%   |
| 测试规则  | 用例通过率      | 场景通过率 = 100%    |
|       | 核心用例       | 核心用例全部通过        |
|       | 新增用例       | 新增用例全部通过        |
| 性能规则  | 响应时间       | P95 RT ≤ 1000ms |
|       | TPS        | TPS ≥ 100       |
| 缺陷规则  | 严重缺陷数      | critical 缺陷 = 0 |
|       | 未解决缺陷      | 未解决缺陷 ≤ 5       |

**门禁执行流程**：

text

┌─────────────────────────────────────────────────────────────┐
│                    质量门禁执行流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CI 触发（代码提交/PR/部署）                                   │
│         │                                                   │
│         ▼                                                   │
│  调用门禁 API：POST /api/quality-gate/{id}/evaluate          │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              执行各规则检查                           │   │
│  │                                                      │   │
│  │  Rule 1: 覆盖率检查                                   │   │
│  │  ├── 获取最新覆盖率数据                               │   │
│  │  ├── 计算整体/增量覆盖率                              │   │
│  │  └── 判断是否满足阈值                                 │   │
│  │                                                      │   │
│  │  Rule 2: 测试通过率检查                               │   │
│  │  ├── 触发相关用例执行                                 │   │
│  │  ├── 等待执行完成                                     │   │
│  │  └── 计算通过率                                       │   │
│  │                                                      │   │
│  │  Rule 3: 缺陷检查                                     │   │
│  │  ├── 查询关联模块的未解决缺陷                          │   │
│  │  └── 统计严重缺陷数量                                 │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  汇总结果：                                                  │
│  - 所有规则通过 → status: passed                             │
│  - 有规则失败（阻断级）→ status: failed                       │
│  - 有规则失败（警告级）→ status: warning                      │
│         │                                                   │
│         ▼                                                   │
│  返回结果给 CI，决定是否继续                                   │
│         │                                                   │
│         ▼                                                   │
│  记录门禁结果，发送通知                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

* * *

五、API 接口扩展
----------

### 5.1 新增接口总览

| 模块        | 方法     | 路径                                           | 说明              |
| --------- | ------ | -------------------------------------------- | --------------- |
| **代码仓库**  | GET    | `/api/repositories`                          | 获取仓库列表          |
|           | POST   | `/api/repositories`                          | 添加代码仓库          |
|           | GET    | `/api/repositories/{id}`                     | 获取仓库详情          |
|           | PUT    | `/api/repositories/{id}`                     | 更新仓库            |
|           | DELETE | `/api/repositories/{id}`                     | 删除仓库            |
|           | POST   | `/api/repositories/{id}/sync`                | 同步代码结构          |
| **覆盖率**   | POST   | `/api/coverage/upload`                       | 上传覆盖率报告         |
|           | GET    | `/api/coverage/summary`                      | 获取覆盖率概览         |
|           | GET    | `/api/coverage/files`                        | 获取文件覆盖率列表       |
|           | GET    | `/api/coverage/files/{id}`                   | 获取文件覆盖详情        |
|           | GET    | `/api/coverage/trend`                        | 获取覆盖率趋势         |
| **用例关联**  | PUT    | `/api/cases/{id}/code-binding`               | 绑定用例到代码         |
|           | GET    | `/api/cases/{id}/coverage`                   | 获取用例关联代码覆盖率     |
|           | GET    | `/api/cases/suggestions`                     | 获取用例补充建议        |
| **缺陷管理**  | GET    | `/api/defects`                               | 获取缺陷列表          |
|           | POST   | `/api/defects`                               | 创建缺陷            |
|           | GET    | `/api/defects/{id}`                          | 获取缺陷详情          |
|           | PUT    | `/api/defects/{id}`                          | 更新缺陷            |
|           | DELETE | `/api/defects/{id}`                          | 删除缺陷            |
|           | POST   | `/api/defects/{id}/comments`                 | 添加评论            |
|           | POST   | `/api/defects/{id}/attachments`              | 上传附件            |
|           | POST   | `/api/defects/from-execution`                | 从执行记录创建缺陷       |
| **第三方集成** | GET    | `/api/integrations/defect-systems`           | 获取缺陷系统配置        |
|           | POST   | `/api/integrations/defect-systems`           | 添加缺陷系统          |
|           | PUT    | `/api/integrations/defect-systems/{id}`      | 更新配置            |
|           | POST   | `/api/integrations/defect-systems/{id}/test` | 测试连接            |
|           | POST   | `/api/integrations/webhook/jira`             | Jira Webhook 回调 |
| **质量门禁**  | GET    | `/api/quality-gates`                         | 获取门禁列表          |
|           | POST   | `/api/quality-gates`                         | 创建质量门禁          |
|           | GET    | `/api/quality-gates/{id}`                    | 获取门禁详情          |
|           | PUT    | `/api/quality-gates/{id}`                    | 更新门禁            |
|           | DELETE | `/api/quality-gates/{id}`                    | 删除门禁            |
|           | POST   | `/api/quality-gates/{id}/evaluate`           | 执行门禁评估          |
|           | GET    | `/api/quality-gates/{id}/results`            | 获取历史结果          |

### 5.2 核心接口详细说明

#### 5.2.1 上传覆盖率报告

**请求**：

text

POST /api/coverage/upload
Content-Type: multipart/form-data
{
  "repository_id": 1,
  "commit_hash": "abc123def456",
  "report_format": "lcov",
  "file": <覆盖率报告文件>
}

**响应**：

json

{
  "code": 0,
  "data": {
    "summary": {
      "line_coverage": 78.5,
      "branch_coverage": 65.2,
      "function_coverage": 82.1,
      "total_lines": 12500,
      "covered_lines": 9812,
      "total_files": 156,
      "files_fully_covered": 42
    },
    "files": [
      {
        "path": "src/controllers/UserController.java",
        "line_coverage": 85.3,
        "branch_coverage": 72.1,
        "uncovered_lines": [45, 46, 78, 102]
      }
    ]
  }
}

#### 5.2.2 从执行记录创建缺陷

**请求**：

text

POST /api/defects/from-execution
Content-Type: application/json
{
  "execution_log_id": 12345,
  "title": "[API] 用户登录接口返回 500",
  "severity": "high",
  "priority": "high",
  "assignee": "developer1",
  "expected_result": "返回 code=0 和 token",
  "steps_to_reproduce": "使用测试账号登录",
  "sync_to_external": true
}

**响应**：

json

{
  "code": 0,
  "data": {
    "id": 1,
    "title": "[API] 用户登录接口返回 500",
    "status": "open",
    "execution_snapshot": {
      "request": {
        "method": "POST",
        "url": "http://test.example.com/api/login",
        "headers": {...},
        "body": {...}
      },
      "response": {
        "status": 500,
        "body": {...}
      }
    },
    "external_id": "JIRA-123",
    "external_url": "https://jira.example.com/browse/JIRA-123"
  }
}

#### 5.2.3 执行质量门禁

**请求**：

text

POST /api/quality-gates/1/evaluate
Content-Type: application/json
{
  "trigger_type": "pr",
  "trigger_ref": "PR-123",
  "commit_hash": "abc123",
  "context": {
    "changed_files": ["src/controllers/UserController.java"]
  }
}

**响应**：

json

{
  "code": 0,
  "data": {
    "status": "failed",
    "summary": "2 项通过，1 项失败",
    "rule_results": [
      {
        "id": "rule_1",
        "name": "整体覆盖率",
        "type": "coverage",
        "status": "passed",
        "actual": 82.5,
        "threshold": 80,
        "message": "覆盖率 82.5% ≥ 80%，通过"
      },
      {
        "id": "rule_2",
        "name": "增量覆盖率",
        "type": "coverage",
        "status": "failed",
        "actual": 65.3,
        "threshold": 90,
        "message": "增量覆盖率 65.3% < 90%，不通过"
      },
      {
        "id": "rule_3",
        "name": "核心用例",
        "type": "test_pass_rate",
        "status": "passed",
        "actual": 100,
        "threshold": 100,
        "message": "核心用例全部通过"
      }
    ],
    "suggestions": [
      "文件 src/controllers/UserController.java 新增代码覆盖率不足，建议补充单元测试",
      "建议执行用例 TC-001 验证变更"
    ]
  }
}

* * *

六、前端页面扩展
--------

### 6.1 新增页面结构

text

Phase 3 新增页面
├── 代码质量管理
│   ├── 代码仓库管理
│   ├── 覆盖率仪表盘
│   ├── 文件覆盖率详情
│   └── 覆盖率趋势图
├── 用例-代码关联
│   ├── 代码绑定配置
│   └── 关联建议列表
├── 缺陷管理
│   ├── 缺陷列表（看板视图）
│   ├── 缺陷详情页
│   ├── 创建缺陷（含一键创建）
│   └── 缺陷统计看板
├── 集成设置
│   ├── 缺陷系统配置
│   ├── CI/CD 集成配置
│   └── Webhook 管理
└── 质量门禁
    ├── 门禁规则配置
    ├── 门禁执行历史
    └── 门禁结果详情

### 6.2 核心页面设计

#### 6.2.1 覆盖率仪表盘

text

┌─────────────────────────────────────────────────────────────────┐
│  覆盖率仪表盘                                          [同步数据] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  仓库：[user-service ▼]  分支：[main ▼]  时间：[最近一次 ▼]      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  │ 行覆盖率      │  │ 分支覆盖率    │  │ 函数覆盖率    │  │ 文件覆盖率    │
│  │   78.5%      │  │   65.2%      │  │   82.1%      │  │   68.4%      │
│  │  ▲ +2.1%     │  │  ▼ -0.5%     │  │  ▲ +1.2%     │  │  ▲ +3.1%     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    覆盖率趋势图                           │   │
│  │  100% │                                                  │   │
│  │   80% │        ╭───╮        ╭───╮                        │   │
│  │   60% │      ╭─╯   ╰─╮    ╭─╯   ╰─╮                      │   │
│  │   40% │    ╭─╯       ╰──╮─╯       ╰─╮                    │   │
│  │   20% │  ╭─╯           ╰─╯           ╰─╮                  │   │
│  │    0% └────────────────────────────────────►              │   │
│  │        1/1   1/5   1/9   1/13  1/17  1/21                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 文件覆盖率详情                                            │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ 文件路径                           │ 行覆盖 │ 分支   │ 状态 │ │   │
│  │ ├─────────────────────────────────────────────────────┤ │   │
│  │ │ src/controllers/UserController.java  │ 85.3% │ 72.1% │ 🟢  │ │   │
│  │ │ src/controllers/OrderController.java │ 45.2% │ 32.8% │ 🔴  │ │   │
│  │ │ src/services/UserService.java        │ 92.1% │ 88.5% │ 🟢  │ │   │
│  │ │ src/services/PaymentService.java     │ 23.5% │ 15.2% │ 🔴  │ │   │
│  │ │ src/utils/Validator.java             │ 78.9% │ 65.4% │ 🟡  │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📊 覆盖率较低的接口建议补充测试：                                 │
│  • POST /api/orders (OrderController.create) - 覆盖率 45.2%     │
│  • POST /api/payments (PaymentService.process) - 覆盖率 23.5%   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

#### 6.2.2 缺陷看板

text

┌─────────────────────────────────────────────────────────────────┐
│  缺陷看板                                    [+ 新建缺陷] [筛选] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   待处理 3    │   处理中 5    │   已解决 8    │   已关闭 12   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │    待处理        │ │    处理中        │ │    已解决        │    │
│  │                 │ │                 │ │                 │    │
│  │ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │    │
│  │ │ 🔴 BUG-001  │ │ │ │ 🟡 BUG-004  │ │ │ │ 🟢 BUG-006  │ │    │
│  │ │ 登录失败    │ │ │ │ 订单超时    │ │ │ │ 参数校验    │ │    │
│  │ │ 严重:高     │ │ │ │ 严重:中     │ │ │ │ 严重:低     │ │    │
│  │ │ 指派人:张三 │ │ │ │ 指派人:李四 │ │ │ │ 指派人:王五 │ │    │
│  │ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │    │
│  │                 │ │                 │ │                 │    │
│  │ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │    │
│  │ │ 🔴 BUG-002  │ │ │ │ 🟡 BUG-005  │ │ │ │ 🟢 BUG-007  │ │    │
│  │ │ 数据丢失    │ │ │ │ 并发问题    │ │ │ │ 文档错误    │ │    │
│  │ │ 严重:紧急   │ │ │ │ 严重:中     │ │ │ │ 严重:低     │ │    │
│  │ │ 指派人:赵六 │ │ │ │ 指派人:张三 │ │ │ │ 指派人:李四 │ │    │
│  │ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │    │
│  │                 │ │                 │ │                 │    │
│  │ ┌─────────────┐ │ │                 │ │                 │    │
│  │ │ 🟠 BUG-003  │ │ │                 │ │                 │    │
│  │ │ 响应慢      │ │ │                 │ │                 │    │
│  │ │ 严重:中     │ │ │                 │ │                 │    │
│  │ │ 指派人:未   │ │ │                 │ │                 │    │
│  │ └─────────────┘ │ │                 │ │                 │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

#### 6.2.3 质量门禁配置

text

┌─────────────────────────────────────────────────────────────────┐
│  编辑质量门禁 - 发布门禁                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  基本信息                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 名称：[生产发布门禁                            ]          │   │
│  │ 描述：[生产环境部署前的质量检查                 ]          │   │
│  │ 启用：[●]                                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  门禁规则                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │  📊 覆盖率规则                                           │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ ☑ 整体行覆盖率 ≥ [80] %                  [阻断] [×] │ │   │
│  │  │ ☑ 核心模块覆盖率 ≥ [95] %                [阻断] [×] │ │   │
│  │  │ ☐ 增量覆盖率 ≥ [90] %                    [阻断] [×] │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │  🧪 测试规则                                             │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ ☑ 核心场景通过率 = [100] %                [阻断] [×] │ │   │
│  │  │ ☑ 回归测试通过率 ≥ [95] %                [阻断] [×] │ │   │
│  │  │ ☐ 新增用例全部通过                        [阻断] [×] │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │  ⚡ 性能规则                                             │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ ☑ 核心接口 P95 RT ≤ [1000] ms             [警告] [×] │ │   │
│  │  │ ☐ 核心接口 TPS ≥ [100]                    [警告] [×] │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │  🐛 缺陷规则                                             │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ ☑ Critical/High 缺陷数 = [0]              [阻断] [×] │ │   │
│  │  │ ☐ Medium 缺陷数 ≤ [5]                     [警告] [×] │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │                                    [+ 添加规则]          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 通知设置                                                  │   │
│  │ ☑ 门禁通过时发送通知                                      │   │
│  │ ☑ 门禁失败时发送通知                                      │   │
│  │ 通知渠道：[钉钉 ▼] [邮件 ▼]                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                          [取消] [保存] [测试]   │
└─────────────────────────────────────────────────────────────────┘

* * *

七、CLI 工具扩展
----------

### 7.1 Phase 3 新增命令

text

api-debug
├── coverage                       # 覆盖率管理
│   ├── upload <file>             # 上传覆盖率报告
│   ├── summary                   # 查看覆盖率概览
│   └── trend                     # 查看覆盖率趋势
├── repo                          # 代码仓库管理
│   ├── add <url>                 # 添加代码仓库
│   ├── list                      # 列出仓库
│   ├── sync <id>                 # 同步代码结构
│   └── remove <id>               # 移除仓库
├── defect                        # 缺陷管理
│   ├── list                      # 列出缺陷
│   ├── create                    # 创建缺陷
│   ├── update <id>               # 更新缺陷
│   ├── from-execution <log_id>   # 从执行记录创建缺陷
│   └── export                    # 导出缺陷列表
├── quality-gate                  # 质量门禁
│   ├── list                      # 列出门禁
│   ├── evaluate <id>             # 执行门禁评估
│   ├── result <id>               # 查看评估结果
│   └── check                     # CI 集成检查命令
└── integration                   # 集成管理
    ├── jira setup                # 配置 Jira
    ├── tapd setup                # 配置 TAPD
    └── test-connection           # 测试连接

### 7.2 CI 集成示例

**GitLab CI 配置**：

yaml

# .gitlab-ci.yml

stages:

- test
- coverage
- quality-gate
- deploy
  
  # 运行单元测试并生成覆盖率
  
  unit-test:
  stage: test
  script:
  - pytest --cov=src --cov-report=xml --junitxml=report.xml
    artifacts:
    reports:
    junit: report.xml
    coverage_report:
      coverage_format: cobertura
      path: coverage.xml
    
    # 上传覆盖率到平台
    
    upload-coverage:
    stage: coverage
    script:
  - api-debug coverage upload coverage.xml --repo 1 --commit $CI_COMMIT_SHA
    
    # 执行质量门禁
    
    quality-check:
    stage: quality-gate
    script:
  - api-debug quality-gate check --gate-id 1 --commit $CI_COMMIT_SHA
    allow_failure: false
    
    # 部署到生产（只有门禁通过才执行）
    
    deploy-prod:
    stage: deploy
    script:
  - echo "Deploying to production..."
    only:
  - main
    when: on_success

* * *

八、项目结构扩展
--------

### 8.1 后端新增目录结构

text

backend/app/
├── services/                     # 新增服务
│   ├── coverage_parser.py       # 覆盖率解析器
│   ├── unittest_parser.py       # 单测结果解析器
│   ├── code_analyzer.py         # 代码分析器
│   ├── defect_manager.py        # 缺陷管理器
│   ├── defect_adapter.py        # 第三方缺陷适配器基类
│   ├── adapters/                # 适配器实现
│   │   ├── jira_adapter.py
│   │   ├── tapd_adapter.py
│   │   └── zentao_adapter.py
│   ├── quality_gate_engine.py   # 质量门禁引擎
│   └── repo_sync_service.py     # 仓库同步服务
├── routers/                      # 新增路由
│   ├── repositories.py
│   ├── coverage.py
│   ├── defects.py
│   ├── integrations.py
│   └── quality_gates.py
├── models/                       # 新增模型
│   ├── repository.py
│   ├── code_file.py
│   ├── coverage.py
│   ├── defect.py
│   └── quality_gate.py
└── webhooks/                     # Webhook 处理
    ├── jira_webhook.py
    └── git_webhook.py

### 8.2 前端新增目录结构

text

frontend/src/
├── views/                        # 新增页面
│   ├── CodeQuality/
│   │   ├── RepositoryList.vue
│   │   ├── CoverageDashboard.vue
│   │   ├── FileCoverageDetail.vue
│   │   └── CoverageTrend.vue
│   ├── Defect/
│   │   ├── DefectBoard.vue
│   │   ├── DefectDetail.vue
│   │   ├── DefectForm.vue
│   │   └── DefectStats.vue
│   ├── QualityGate/
│   │   ├── GateList.vue
│   │   ├── GateEditor.vue
│   │   └── GateResult.vue
│   └── Integration/
│       ├── DefectSystemConfig.vue
│       └── CICDConfig.vue
├── components/                   # 新增组件
│   ├── coverage/
│   │   ├── CoverageTreemap.vue
│   │   └── CoverageBadge.vue
│   ├── defect/
│   │   ├── DefectCard.vue
│   │   ├── DefectStatusTag.vue
│   │   └── OneClickDefect.vue
│   └── quality/
│       └── GateStatusBadge.vue
└── api/                          # 新增 API
    ├── repository.js
    ├── coverage.js
    ├── defect.js
    ├── integration.js
    └── qualityGate.js

* * *

九、里程碑与交付物
---------

### 9.1 四周计划

| 周次          | 主题       | 核心交付物           | 验收标准                |
| ----------- | -------- | --------------- | ------------------- |
| **Week 9**  | 代码仓库与覆盖率 | 仓库管理 + 覆盖率解析    | 可添加仓库，上传并解析覆盖率报告    |
| **Week 10** | 用例-代码关联  | 代码绑定 + 覆盖率视图    | 用例可关联代码，查看对应覆盖率     |
| **Week 11** | 缺陷管理     | 内置缺陷工作流 + 第三方对接 | 可创建缺陷，同步到 Jira/TAPD |
| **Week 12** | 质量门禁     | 门禁规则引擎 + CI 集成  | CI 中可调用门禁检查         |

### 9.2 验收清单

| 序号  | 验收项            | 验收方式           |
| --- | -------------- | -------------- |
| 1   | 代码仓库 CRUD 功能完整 | 手动测试           |
| 2   | 覆盖率报告解析正确      | 上传标准报告验证       |
| 3   | 覆盖率数据可视化       | 前端图表展示验证       |
| 4   | 用例-代码关联功能      | 手动绑定验证         |
| 5   | 缺陷 CRUD 功能完整   | 手动测试           |
| 6   | 一键提缺陷功能        | 从执行记录创建验证      |
| 7   | Jira/TAPD 对接   | 配置后同步验证        |
| 8   | 质量门禁规则配置       | 创建门禁验证         |
| 9   | 门禁评估执行         | API 调用验证       |
| 10  | CI 集成示例        | GitLab CI 配置验证 |

* * *

十、Phase 3 与 Phase 4 衔接
----------------------

Phase 3 完成后，平台已打通代码与测试的完整链路。Phase 4 将进一步扩展团队协作与智能分析能力：

| Phase 3 产出 | Phase 4 扩展方向                              |
| ---------- | ----------------------------------------- |
| 代码仓库管理     | → 多项目/多仓库管理                               |
| 覆盖率数据      | → 团队覆盖率排行与对比                              |
| 缺陷管理       | → 缺陷根因分析与智能分配                             |
| 质量门禁       | → 门禁策略模板与共享                               |
| 单用户模式      | → 多用户与 RBAC 权限                            |
| 执行记录       | → AI 辅助失败原因分析 |
