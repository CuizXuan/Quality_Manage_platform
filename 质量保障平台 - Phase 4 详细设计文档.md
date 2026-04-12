API Debug Tool 质量保障平台 - Phase 4 详细设计文档
======================================

一、Phase 4 概述
------------

### 1.1 阶段定位

在前三个阶段建立的质量保障能力基础上，Phase 4 聚焦**平台化与智能化**，将单机/单团队工具升级为**企业级质量中台**，支持多团队协作、智能分析与决策辅助。

### 1.2 核心目标

| 目标      | 说明                    | 成功标准                 |
| ------- | --------------------- | -------------------- |
| 多租户与权限  | 支持多团队、多项目隔离，RBAC 权限模型 | 不同团队数据隔离，权限精细化控制     |
| 项目与版本管理 | 按项目组织测试资产，支持版本追溯      | 项目 CRUD，版本质量报告       |
| 团队协作    | 共享用例库、场景模板、环境配置       | 团队内共享资产，跨团队复用        |
| 智能分析引擎  | 失败模式聚类、变更影响分析、智能告警    | AI 辅助定位问题，智能推荐       |
| 质量大盘    | 多维度可视化，全局质量视图         | 项目/团队/全局质量仪表盘        |
| 开放 API  | 完整的 REST API，支持二次开发   | API 文档完整，支持 Token 认证 |
| 插件体系    | 支持自定义插件扩展             | 脚本插件、通知插件、报告插件       |
| 性能基线与回归 | 建立性能基准，自动检测性能劣化       | 基准配置、劣化告警            |

### 1.4 与前三阶段的关系

text

Phase 1               Phase 2               Phase 3               Phase 4 扩展
────────────────────────────────────────────────────────────────────────────────
用例管理 ──────────► 数据驱动 ──────────► 用例-代码关联 ──────► 资产共享与复用
环境管理 ──────────► 定时任务 ──────────► CI 集成 ────────────► 项目环境隔离
执行记录 ──────────► 报告生成 ──────────► 质量门禁 ──────────► 质量大盘聚合
CLI 工具 ──────────► 压力测试 ──────────► 缺陷管理 ──────────► AI 根因分析
单用户模式 ──────────────────────────────────────────────────► 多租户 RBAC

* * *

二、系统架构升级
--------

### 2.1 Phase 4 架构全景图

text

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   Phase 4 架构                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                            接入层                                          │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │ │
│  │  │ Web 前端  │ │ CLI 工具  │ │ IDE 插件 │ │ Open API │ │ 第三方集成    │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                          │
│                                      ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                         认证与授权层                                        │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐   │ │
│  │  │  JWT 认证 │ SSO 集成 │ RBAC 权限 │ 租户隔离 │ API 限流 │ 审计日志   │   │ │
│  │  └────────────────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                          │
│                                      ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                          业务服务层                                         │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐   │ │
│  │  │  项目服务  │ 版本服务  │ 团队服务  │ 资产共享  │ 开放 API 服务        │   │ │
│  │  └────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                           │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐   │ │
│  │  │               Phase 1-3 核心服务（用例/场景/执行/覆盖率/缺陷）         │   │ │
│  │  └────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                           │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    智能分析引擎（Phase 4 新增）                       │   │ │
│  │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │   │ │
│  │  │  │ 失败聚类   │ │ 变更影响   │ │ 智能告警   │ │ 质量预测       │  │   │ │
│  │  │  │ 分析器     │ │ 分析器     │ │ 引擎       │ │ 模型           │  │   │ │
│  │  │  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │   │ │
│  │  └────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                           │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    插件体系（Phase 4 新增）                          │   │ │
│  │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │   │ │
│  │  │  │ 脚本插件   │ │ 通知插件   │ │ 报告插件   │ │ 自定义插件     │  │   │ │
│  │  │  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │   │ │
│  │  └────────────────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                          │
│                                      ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                          数据存储层                                        │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │ │
│  │  │ PostgreSQL   │ │ Redis 缓存   │ │ MinIO/OSS    │ │ ClickHouse   │     │ │
│  │  │ (主数据库)    │ │ (会话/限流)   │ │ (文件存储)    │ │ (时序数据)    │     │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

### 2.2 新增模块职责说明

| 模块         | 职责                          | 依赖              |
| ---------- | --------------------------- | --------------- |
| **认证授权**   | 用户认证、JWT 管理、RBAC 权限控制       | JWT、OAuth2      |
| **多租户管理**  | 租户（团队）数据隔离、资源配额             | 数据库行级安全         |
| **项目管理**   | 项目 CRUD、成员管理、资产归属           | 租户管理            |
| **版本管理**   | 版本创建、质量报告绑定、基线管理            | Git 集成          |
| **资产共享**   | 用例/场景/环境模板的团队内与跨团队共享        | 权限控制            |
| **智能分析引擎** | AI 驱动的失败分析、变更影响预测           | 机器学习/规则引擎       |
| **插件体系**   | 插件加载、生命周期管理、热更新             | 动态加载            |
| **开放 API** | REST API 文档、Token 管理、SDK 生成 | OpenAPI/Swagger |
| **质量大盘**   | 多维度聚合展示、实时刷新                | 数据仓库            |

* * *

三、数据模型扩展
--------

### 3.1 Phase 4 新增表 ER 图

text

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Tenant        │       │   Project       │       │   Version       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │◄──────│ tenant_id       │◄──────│ project_id      │
│ name            │       │ name            │       │ name            │
│ code            │       │ key             │       │ tag             │
│ status          │       │ description     │       │ description     │
│ quota           │       │ status          │       │ commit_hash     │
│ created_at      │       │ created_by      │       │ baseline_id     │
└─────────────────┘       │ created_at      │       │ quality_report  │
                          └─────────────────┘       │ released_at     │
                                   │                │ created_at      │
                                   │ 1:N            └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  ProjectMember  │
                          ├─────────────────┤
                          │ project_id      │
                          │ user_id         │
                          │ role            │
                          └─────────────────┘
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   User          │       │   Role          │       │   Permission    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │◄──┐   │ id              │◄──┐   │ id              │
│ tenant_id       │   │   │ name            │   │   │ resource        │
│ username        │   │   │ description     │   │   │ action          │
│ email           │   ├───│ tenant_id       │   ├───│ role_id         │
│ password_hash   │   │   └─────────────────┘   │   └─────────────────┘
│ avatar          │   │                         │
│ status          │   │   ┌─────────────────┐   │
│ last_login      │   │   │  UserRole       │   │
│ created_at      │   └───│ user_id         │───┘
└─────────────────┘       │ role_id         │
                          └─────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                         资产共享相关表                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐       ┌─────────────────┐                      │
│  │  SharedAsset    │       │  AssetTemplate  │                      │
│  ├─────────────────┤       ├─────────────────┤                      │
│  │ id              │       │ id              │                      │
│  │ asset_type      │       │ name            │                      │
│  │ asset_id        │       │ type            │                      │
│  │ owner_tenant_id │       │ content         │                      │
│  │ owner_project_id│       │ tags            │                      │
│  │ shared_to_tenant│       │ usage_count     │                      │
│  │ shared_to_project│      │ created_by      │                      │
│  │ permission      │       │ tenant_id       │                      │
│  │ created_at      │       │ is_public       │                      │
│  └─────────────────┘       └─────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                         智能分析相关表                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐       ┌─────────────────┐                      │
│  │ FailureCluster  │       │ ChangeImpact    │                      │
│  ├─────────────────┤       ├─────────────────┤                      │
│  │ id              │       │ id              │                      │
│  │ cluster_name    │       │ project_id      │                      │
│  │ error_pattern   │       │ commit_hash     │                      │
│  │ root_cause      │       │ changed_files   │                      │
│  │ occurrence_count│       │ impacted_cases  │                      │
│  │ first_seen      │       │ risk_level      │                      │
│  │ last_seen       │       │ recommendation  │                      │
│  │ resolved        │       │ created_at      │                      │
│  └─────────────────┘       └─────────────────┘                      │
│                                                                     │
│  ┌─────────────────┐       ┌─────────────────┐                      │
│  │ PerformanceBaseline│    │ AlertRule       │                      │
│  ├─────────────────┤       ├─────────────────┤                      │
│  │ id              │       │ id              │                      │
│  │ case_id         │       │ name            │                      │
│  │ scenario_id     │       │ type            │                      │
│  │ metric_name     │       │ condition       │                      │
│  │ baseline_value  │       │ threshold       │                      │
│  │ upper_bound     │       │ severity        │                      │
│  │ lower_bound     │       │ enabled         │                      │
│  │ updated_at      │       │ notify_channels │                      │
│  └─────────────────┘       └─────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                         质量大盘相关表                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐       ┌─────────────────┐                      │
│  │ Dashboard       │       │ DashboardWidget │                      │
│  ├─────────────────┤       ├─────────────────┤                      │
│  │ id              │       │ id              │                      │
│  │ name            │       │ dashboard_id    │                      │
│  │ type            │       │ widget_type     │                      │
│  │ owner_id        │       │ config          │                      │
│  │ is_default      │       │ position        │                      │
│  │ layout_config   │       │ refresh_interval│                      │
│  │ created_at      │       │ created_at      │                      │
│  └─────────────────┘       └─────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

### 3.2 新增表详细设计

#### 3.2.1 租户表 `tenant`

| 字段                   | 类型           | 约束                        | 说明                       |
| -------------------- | ------------ | ------------------------- | ------------------------ |
| id                   | INTEGER      | PRIMARY KEY               | 自增主键                     |
| name                 | VARCHAR(100) | NOT NULL                  | 租户名称（团队/公司名）             |
| code                 | VARCHAR(50)  | UNIQUE, NOT NULL          | 租户编码，用于数据隔离              |
| description          | TEXT         |                           | 租户描述                     |
| status               | VARCHAR(20)  | DEFAULT 'active'          | active/suspended/expired |
| logo_url             | VARCHAR(500) |                           | Logo 地址                  |
| quota_config         | TEXT         |                           | JSON，资源配额配置              |
| subscription_plan    | VARCHAR(50)  |                           | free/pro/enterprise      |
| subscription_expires | TIMESTAMP    |                           | 订阅过期时间                   |
| created_at           | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                     |
| updated_at           | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                     |

**quota_config 示例**：

json

{
  "max_projects": 10,
  "max_users": 50,
  "max_cases": 5000,
  "max_scenarios": 500,
  "max_executions_per_day": 10000,
  "max_concurrent_loadtest": 100,
  "storage_limit_gb": 10,
  "data_retention_days": 90,
  "features": {
    "loadtest": true,
    "mock": true,
    "ai_analysis": true,
    "custom_plugins": false
  }
}

#### 3.2.2 用户表 `user`

| 字段            | 类型           | 约束                        | 说明                      |
| ------------- | ------------ | ------------------------- | ----------------------- |
| id            | INTEGER      | PRIMARY KEY               | 自增主键                    |
| tenant_id     | INTEGER      | FOREIGN KEY               | 所属租户                    |
| username      | VARCHAR(100) | UNIQUE, NOT NULL          | 用户名                     |
| email         | VARCHAR(200) | UNIQUE, NOT NULL          | 邮箱                      |
| password_hash | VARCHAR(200) | NOT NULL                  | 密码哈希                    |
| avatar        | VARCHAR(500) |                           | 头像地址                    |
| phone         | VARCHAR(20)  |                           | 手机号                     |
| status        | VARCHAR(20)  | DEFAULT 'active'          | active/disabled/invited |
| last_login_at | TIMESTAMP    |                           | 最后登录时间                  |
| last_login_ip | VARCHAR(50)  |                           | 最后登录 IP                 |
| settings      | TEXT         |                           | JSON，用户偏好设置             |
| created_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                    |
| updated_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                    |

**settings 示例**：

json

{
  "theme": "dark",
  "language": "zh-CN",
  "notifications": {
    "email": true,
    "dingtalk": false
  },
  "default_environment": 1,
  "editor_preferences": {
    "font_size": 14,
    "word_wrap": true
  }
}

#### 3.2.3 角色表 `role`

| 字段          | 类型          | 约束                        | 说明                |
| ----------- | ----------- | ------------------------- | ----------------- |
| id          | INTEGER     | PRIMARY KEY               | 自增主键              |
| name        | VARCHAR(50) | NOT NULL                  | 角色名称              |
| description | TEXT        |                           | 角色描述              |
| tenant_id   | INTEGER     | FOREIGN KEY               | 所属租户（null 表示系统角色） |
| is_system   | BOOLEAN     | DEFAULT 0                 | 是否系统内置角色          |
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间              |

**系统内置角色**：

| 角色           | 说明    | 权限范围       |
| ------------ | ----- | ---------- |
| SuperAdmin   | 超级管理员 | 全系统        |
| TenantAdmin  | 租户管理员 | 租户内所有资源    |
| ProjectAdmin | 项目管理员 | 项目内所有资源    |
| Developer    | 开发者   | 用例/场景编辑、执行 |
| Tester       | 测试工程师 | 用例/场景/缺陷管理 |
| Viewer       | 观察者   | 只读权限       |

#### 3.2.4 权限表 `permission`

| 字段       | 类型           | 约束            | 说明                                       |
| -------- | ------------ | ------------- | ---------------------------------------- |
| id       | INTEGER      | PRIMARY KEY   | 自增主键                                     |
| role_id  | INTEGER      | FOREIGN KEY   | 关联角色                                     |
| resource | VARCHAR(100) | NOT NULL      | 资源类型：case/scenario/project/...           |
| action   | VARCHAR(50)  | NOT NULL      | 操作：create/read/update/delete/execute/... |
| scope    | VARCHAR(20)  | DEFAULT 'all' | all/own/project/tenant                   |

**资源类型定义**：

| 资源           | 说明   | 支持的操作                                        |
| ------------ | ---- | -------------------------------------------- |
| project      | 项目   | create, read, update, delete, manage_members |
| case         | 测试用例 | create, read, update, delete, execute        |
| scenario     | 测试场景 | create, read, update, delete, execute        |
| environment  | 环境配置 | create, read, update, delete, set_default    |
| schedule     | 定时任务 | create, read, update, delete, toggle         |
| defect       | 缺陷   | create, read, update, delete, assign         |
| repository   | 代码仓库 | create, read, update, delete, sync           |
| quality_gate | 质量门禁 | create, read, update, delete, evaluate       |
| report       | 报告   | read, generate, download                     |
| dashboard    | 仪表盘  | read, create, update, delete                 |
| team         | 团队管理 | manage_users, manage_roles                   |
| billing      | 计费   | read, update                                 |

#### 3.2.5 用户角色关联表 `user_role`

| 字段         | 类型        | 约束                        | 说明    |
| ---------- | --------- | ------------------------- | ----- |
| id         | INTEGER   | PRIMARY KEY               | 自增主键  |
| user_id    | INTEGER   | FOREIGN KEY               | 用户 ID |
| role_id    | INTEGER   | FOREIGN KEY               | 角色 ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间  |

#### 3.2.6 项目表 `project`

| 字段            | 类型           | 约束                        | 说明                      |
| ------------- | ------------ | ------------------------- | ----------------------- |
| id            | INTEGER      | PRIMARY KEY               | 自增主键                    |
| tenant_id     | INTEGER      | FOREIGN KEY               | 所属租户                    |
| name          | VARCHAR(200) | NOT NULL                  | 项目名称                    |
| key           | VARCHAR(20)  | UNIQUE                    | 项目唯一标识                  |
| description   | TEXT         |                           | 项目描述                    |
| avatar        | VARCHAR(500) |                           | 项目图标                    |
| status        | VARCHAR(20)  | DEFAULT 'active'          | active/archived/deleted |
| repository_id | INTEGER      | FOREIGN KEY               | 关联的默认代码仓库               |
| settings      | TEXT         |                           | JSON，项目配置               |
| created_by    | INTEGER      | FOREIGN KEY               | 创建人                     |
| created_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                    |
| updated_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                    |

#### 3.2.7 项目成员表 `project_member`

| 字段         | 类型          | 约束                        | 说明                                  |
| ---------- | ----------- | ------------------------- | ----------------------------------- |
| id         | INTEGER     | PRIMARY KEY               | 自增主键                                |
| project_id | INTEGER     | FOREIGN KEY               | 项目 ID                               |
| user_id    | INTEGER     | FOREIGN KEY               | 用户 ID                               |
| role       | VARCHAR(50) | NOT NULL                  | 项目内角色：admin/developer/tester/viewer |
| created_at | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 加入时间                                |

#### 3.2.8 版本表 `version`

| 字段                | 类型           | 约束                        | 说明                              |
| ----------------- | ------------ | ------------------------- | ------------------------------- |
| id                | INTEGER      | PRIMARY KEY               | 自增主键                            |
| project_id        | INTEGER      | FOREIGN KEY               | 所属项目                            |
| name              | VARCHAR(100) | NOT NULL                  | 版本名称                            |
| tag               | VARCHAR(50)  |                           | Git Tag                         |
| commit_hash       | VARCHAR(64)  |                           | 关联的 Git Commit                  |
| description       | TEXT         |                           | 版本描述                            |
| baseline_id       | INTEGER      |                           | 关联的基准版本 ID                      |
| quality_report_id | VARCHAR(100) |                           | 关联的质量报告                         |
| test_summary      | TEXT         |                           | JSON，测试摘要                       |
| status            | VARCHAR(20)  | DEFAULT 'draft'           | draft/testing/released/archived |
| released_at       | TIMESTAMP    |                           | 发布时间                            |
| created_at        | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                            |
| updated_at        | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                            |

**test_summary 示例**：

json

{
  "total_cases": 156,
  "executed_cases": 156,
  "passed_cases": 148,
  "failed_cases": 5,
  "skipped_cases": 3,
  "pass_rate": 94.87,
  "coverage": {
    "line": 78.5,
    "branch": 65.2
  },
  "defects": {
    "total": 12,
    "open": 3,
    "resolved": 9
  },
  "performance": {
    "avg_rt": 234,
    "p95_rt": 456,
    "tps": 125.3
  }
}

#### 3.2.9 共享资产表 `shared_asset`

| 字段                   | 类型          | 约束                        | 说明                                 |
| -------------------- | ----------- | ------------------------- | ---------------------------------- |
| id                   | INTEGER     | PRIMARY KEY               | 自增主键                               |
| asset_type           | VARCHAR(50) | NOT NULL                  | case/scenario/environment/template |
| asset_id             | INTEGER     | NOT NULL                  | 资产原始 ID                            |
| owner_tenant_id      | INTEGER     | NOT NULL                  | 所有者租户                              |
| owner_project_id     | INTEGER     |                           | 所有者项目                              |
| shared_to_tenant_id  | INTEGER     |                           | 共享目标租户（null 表示公开）                  |
| shared_to_project_id | INTEGER     |                           | 共享目标项目                             |
| permission           | VARCHAR(20) | DEFAULT 'read'            | read/copy/execute                  |
| created_by           | INTEGER     | FOREIGN KEY               | 分享人                                |
| created_at           | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 分享时间                               |
| expires_at           | TIMESTAMP   |                           | 过期时间                               |

#### 3.2.10 资产模板表 `asset_template`

| 字段          | 类型           | 约束                        | 说明                               |
| ----------- | ------------ | ------------------------- | -------------------------------- |
| id          | INTEGER      | PRIMARY KEY               | 自增主键                             |
| name        | VARCHAR(200) | NOT NULL                  | 模板名称                             |
| type        | VARCHAR(50)  | NOT NULL                  | case/scenario/report/environment |
| content     | TEXT         | NOT NULL                  | 模板内容（JSON）                       |
| description | TEXT         |                           | 模板描述                             |
| tags        | TEXT         |                           | JSON 数组，标签                       |
| icon        | VARCHAR(500) |                           | 图标                               |
| usage_count | INTEGER      | DEFAULT 0                 | 使用次数                             |
| tenant_id   | INTEGER      | FOREIGN KEY               | 所属租户（null 表示系统模板）                |
| created_by  | INTEGER      | FOREIGN KEY               | 创建人                              |
| is_public   | BOOLEAN      | DEFAULT 0                 | 是否公开                             |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                             |
| updated_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                             |

#### 3.2.11 失败聚类表 `failure_cluster`

| 字段               | 类型           | 约束                        | 说明                                     |
| ---------------- | ------------ | ------------------------- | -------------------------------------- |
| id               | INTEGER      | PRIMARY KEY               | 自增主键                                   |
| project_id       | INTEGER      | FOREIGN KEY               | 所属项目                                   |
| cluster_name     | VARCHAR(200) | NOT NULL                  | 聚类名称                                   |
| error_pattern    | TEXT         | NOT NULL                  | 错误特征模式                                 |
| error_type       | VARCHAR(50)  |                           | timeout/assertion/connection/parse/... |
| root_cause       | TEXT         |                           | 根因分析结果                                 |
| suggested_fix    | TEXT         |                           | 建议修复方案                                 |
| occurrence_count | INTEGER      | DEFAULT 1                 | 发生次数                                   |
| affected_cases   | TEXT         |                           | JSON 数组，受影响的用例 ID                      |
| first_seen_at    | TIMESTAMP    |                           | 首次出现时间                                 |
| last_seen_at     | TIMESTAMP    |                           | 最后出现时间                                 |
| resolved         | BOOLEAN      | DEFAULT 0                 | 是否已解决                                  |
| resolved_at      | TIMESTAMP    |                           | 解决时间                                   |
| created_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                                   |

#### 3.2.12 变更影响分析表 `change_impact`

| 字段                  | 类型          | 约束                        | 说明                       |
| ------------------- | ----------- | ------------------------- | ------------------------ |
| id                  | INTEGER     | PRIMARY KEY               | 自增主键                     |
| project_id          | INTEGER     | FOREIGN KEY               | 所属项目                     |
| commit_hash         | VARCHAR(64) | NOT NULL                  | 变更 Commit                |
| changed_files       | TEXT        |                           | JSON 数组，变更文件列表           |
| impacted_cases      | TEXT        |                           | JSON 数组，受影响的用例 ID        |
| impacted_scenarios  | TEXT        |                           | JSON 数组，受影响的场景 ID        |
| risk_level          | VARCHAR(20) |                           | low/medium/high/critical |
| recommendation      | TEXT        |                           | 建议执行的测试                  |
| actual_failures     | TEXT        |                           | 实际失败的用例                  |
| prediction_accuracy | FLOAT       |                           | 预测准确率                    |
| created_at          | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                     |

#### 3.2.13 性能基线表 `performance_baseline`

| 字段             | 类型          | 约束                        | 说明                    |
| -------------- | ----------- | ------------------------- | --------------------- |
| id             | INTEGER     | PRIMARY KEY               | 自增主键                  |
| project_id     | INTEGER     | FOREIGN KEY               | 所属项目                  |
| case_id        | INTEGER     | FOREIGN KEY               | 关联用例                  |
| scenario_id    | INTEGER     | FOREIGN KEY               | 关联场景                  |
| environment_id | INTEGER     | FOREIGN KEY               | 环境                    |
| metric_name    | VARCHAR(50) | NOT NULL                  | rt/tps/error_rate/... |
| baseline_value | FLOAT       | NOT NULL                  | 基准值                   |
| upper_bound    | FLOAT       |                           | 上界（告警阈值）              |
| lower_bound    | FLOAT       |                           | 下界                    |
| sample_count   | INTEGER     |                           | 样本数量                  |
| std_deviation  | FLOAT       |                           | 标准差                   |
| version_id     | INTEGER     | FOREIGN KEY               | 关联版本                  |
| updated_at     | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 更新时间                  |

#### 3.2.14 智能告警规则表 `alert_rule`

| 字段               | 类型           | 约束                        | 说明                                      |
| ---------------- | ------------ | ------------------------- | --------------------------------------- |
| id               | INTEGER      | PRIMARY KEY               | 自增主键                                    |
| name             | VARCHAR(200) | NOT NULL                  | 规则名称                                    |
| type             | VARCHAR(50)  | NOT NULL                  | failure_rate/rt_spike/coverage_drop/... |
| project_id       | INTEGER      | FOREIGN KEY               | 所属项目                                    |
| scope            | TEXT         |                           | JSON，作用范围（用例/场景 ID 列表）                  |
| condition        | TEXT         |                           | JSON，触发条件                               |
| threshold        | FLOAT        |                           | 阈值                                      |
| duration         | INTEGER      |                           | 持续时间（秒）                                 |
| severity         | VARCHAR(20)  |                           | critical/high/medium/low/info           |
| enabled          | BOOLEAN      | DEFAULT 1                 | 是否启用                                    |
| notify_channels  | TEXT         |                           | JSON，通知渠道                               |
| cooldown_minutes | INTEGER      | DEFAULT 30                | 冷却时间（分钟）                                |
| created_by       | INTEGER      | FOREIGN KEY               | 创建人                                     |
| created_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                                    |

**condition 示例**：

json

{
  "metric": "failure_rate",
  "operator": ">",
  "value": 5,
  "compared_to": "last_10_executions"
}

#### 3.2.15 仪表盘表 `dashboard`

| 字段            | 类型           | 约束                        | 说明                             |
| ------------- | ------------ | ------------------------- | ------------------------------ |
| id            | INTEGER      | PRIMARY KEY               | 自增主键                           |
| name          | VARCHAR(200) | NOT NULL                  | 仪表盘名称                          |
| type          | VARCHAR(20)  | NOT NULL                  | personal/project/tenant/system |
| owner_id      | INTEGER      |                           | 所有者 ID（用户/项目/租户）               |
| is_default    | BOOLEAN      | DEFAULT 0                 | 是否默认仪表盘                        |
| layout_config | TEXT         |                           | JSON，布局配置                      |
| created_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                           |
| updated_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                           |

#### 3.2.16 仪表盘组件表 `dashboard_widget`

| 字段               | 类型           | 约束                        | 说明                   |
| ---------------- | ------------ | ------------------------- | -------------------- |
| id               | INTEGER      | PRIMARY KEY               | 自增主键                 |
| dashboard_id     | INTEGER      | FOREIGN KEY               | 关联仪表盘                |
| widget_type      | VARCHAR(50)  | NOT NULL                  | 组件类型                 |
| title            | VARCHAR(200) |                           | 组件标题                 |
| config           | TEXT         |                           | JSON，组件配置            |
| position         | TEXT         |                           | JSON，位置 {x, y, w, h} |
| refresh_interval | INTEGER      |                           | 刷新间隔（秒）              |
| created_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                 |

**支持的组件类型**：

| 类型          | 说明   | 配置项                            |
| ----------- | ---- | ------------------------------ |
| metric_card | 指标卡片 | metric, title, format, color   |
| line_chart  | 折线图  | metrics, time_range, group_by  |
| bar_chart   | 柱状图  | metrics, dimension, time_range |
| pie_chart   | 饼图   | metric, dimension              |
| table       | 数据表格 | columns, data_source, limit    |
| heatmap     | 热力图  | metrics, x_axis, y_axis        |
| gauge       | 仪表盘  | metric, min, max, thresholds   |
| text        | 文本   | content, markdown              |
| iframe      | 嵌入页面 | url, height                    |

* * *

四、核心引擎设计
--------

### 4.1 多租户与权限引擎

**设计目标**：实现租户级数据隔离，精细化权限控制

**租户隔离策略**：

text

┌─────────────────────────────────────────────────────────────┐
│                    租户数据隔离策略                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 数据库级隔离                                            │
│     - 每个租户独立 Schema（PostgreSQL）                      │
│     - 或使用 tenant_id 行级安全策略                          │
│                                                             │
│  2. 请求级拦截                                              │
│     - JWT Token 携带 tenant_id                              │
│     - 中间件自动注入租户上下文                                │
│     - 所有查询自动添加 tenant_id 过滤条件                     │
│                                                             │
│  3. 资源配额检查                                            │
│     - 创建资源前检查配额                                      │
│     - 超配额返回 429 错误                                    │
│     - 支持配额告警通知                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

**RBAC 权限模型**：

text

┌─────────────────────────────────────────────────────────────┐
│                    RBAC 权限模型                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────────┐                          │
│                    │   Tenant    │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│              ┌────────────┼────────────┐                    │
│              │            │            │                    │
│              ▼            ▼            ▼                    │
│        ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│        │  User    │ │  Role    │ │ Project  │              │
│        └────┬─────┘ └────┬─────┘ └────┬─────┘              │
│             │            │            │                     │
│             └────────────┼────────────┘                     │
│                          │                                 │
│                    ┌─────▼─────┐                           │
│                    │ UserRole  │                           │
│                    └─────┬─────┘                           │
│                          │                                 │
│                    ┌─────▼─────┐                           │
│                    │Permission │                           │
│                    └───────────┘                           │
│                                                             │
│  权限判断流程：                                              │
│  1. 解析 JWT 获取 user_id, tenant_id                        │
│  2. 查询用户的角色列表                                        │
│  3. 聚合所有角色的权限                                        │
│  4. 检查请求的 resource + action 是否在权限列表中              │
│  5. 检查 scope 限制（own/project/tenant/all）                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.2 智能分析引擎

**设计目标**：利用 AI/ML 技术辅助问题定位和质量预测

**失败聚类分析**：

text

┌─────────────────────────────────────────────────────────────┐
│                    失败聚类分析流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：失败用例的执行记录                                      │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              特征提取                                 │   │
│  │  - 错误信息（脱敏后）                                  │   │
│  │  - 错误类型（超时/断言/连接/解析）                      │   │
│  │  - 响应状态码                                          │   │
│  │  - 接口路径                                            │   │
│  │  - 时间特征                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              相似度计算                               │   │
│  │  - 文本相似度（TF-IDF + 余弦相似度）                    │   │
│  │  - 错误类型匹配                                        │   │
│  │  - 接口路径相似度                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              聚类算法                                 │   │
│  │  - DBSCAN / 层次聚类                                  │   │
│  │  - 动态阈值调整                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  输出：失败聚类簇 + 根因分析建议                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

**变更影响预测**：

text

┌─────────────────────────────────────────────────────────────┐
│                    变更影响预测流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：代码变更（Commit）                                     │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              变更分析                                 │   │
│  │  - 解析变更文件列表                                    │   │
│  │  - 识别变更的方法/函数                                  │   │
│  │  - 计算变更影响范围                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              用例匹配                                 │   │
│  │  - 根据用例-代码映射关系                               │   │
│  │  - 匹配直接关联的用例                                  │   │
│  │  - 计算间接关联（调用链）                              │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              风险评估                                 │   │
│  │  - 变更类型（新增/修改/删除）                          │   │
│  │  - 变更代码复杂度                                      │   │
│  │  - 历史失败关联度                                      │   │
│  │  - 覆盖率影响                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  输出：受影响用例列表 + 风险等级 + 建议测试范围                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

**智能告警引擎**：

text

┌─────────────────────────────────────────────────────────────┐
│                    智能告警引擎                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  告警类型：                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. 失败率突增                                          │   │
│  │    - 检测：与历史基线对比，失败率超过阈值                 │   │
│  │    - 自动聚类失败原因                                   │   │
│  │                                                       │   │
│  │ 2. 响应时间劣化                                        │   │
│  │    - 检测：P95/P99 超过基线 x 倍                        │   │
│  │    - 关联代码变更分析                                   │   │
│  │                                                       │   │
│  │ 3. 覆盖率下降                                          │   │
│  │    - 检测：与上一版本对比，覆盖率下降超过阈值              │   │
│  │    - 定位新增未覆盖代码                                 │   │
│  │                                                       │   │
│  │ 4. 异常模式检测                                        │   │
│  │    - 检测：特定时间段/特定接口的异常模式                  │   │
│  │    - 使用孤立森林算法                                   │   │
│  │                                                       │   │
│  │ 5. 缺陷积压告警                                        │   │
│  │    - 检测：未解决缺陷数量/存在时长超过阈值                │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  告警收敛策略：                                              │
│  - 相同告警在冷却期内不重复发送                              │
│  - 父子告警自动关联                                          │
│  - 告警升级机制（持续存在则升级严重程度）                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.3 插件体系

**设计目标**：支持用户自定义扩展功能，实现平台能力开放

**插件类型**：

| 类型    | 说明           | 接口方法                            |
| ----- | ------------ | ------------------------------- |
| 脚本插件  | 自定义前置/后置处理脚本 | execute(context)                |
| 通知插件  | 自定义通知渠道      | send(message, config)           |
| 报告插件  | 自定义报告格式      | generate(data, template)        |
| 断言插件  | 自定义断言规则      | assert(response, config)        |
| 数据源插件 | 自定义数据源       | fetch(config) → rows            |
| 认证插件  | 自定义认证方式      | authenticate(context) → headers |

**插件加载机制**：

text

┌─────────────────────────────────────────────────────────────┐
│                    插件加载机制                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              插件注册中心                             │   │
│  │  - 扫描插件目录                                        │   │
│  │  - 解析 plugin.json 配置                              │   │
│  │  - 验证插件接口实现                                    │   │
│  │  - 注册到插件管理器                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  plugin.json 示例：                                         │
│  {                                                         │
│    "id": "custom-assertion",                               │
│    "name": "自定义断言",                                    │
│    "version": "1.0.0",                                     │
│    "type": "assertion",                                    │
│    "entry": "plugin.py:CustomAssertion",                    │
│    "config_schema": {...},                                 │
│    "permissions": ["read_response"]                         │
│  }                                                         │
│                                                             │
│  生命周期管理：                                              │
│  - 加载：动态 import 模块                                    │
│  - 初始化：调用 initialize() 方法                            │
│  - 执行：沙箱环境执行                                        │
│  - 卸载：清理资源                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

### 4.4 开放 API 设计

**设计目标**：提供完整的 REST API，支持外部系统集成

**API 认证方式**：

| 方式        | 说明       | 适用场景     |
| --------- | -------- | -------- |
| JWT Token | 用户登录后获取  | Web 前端   |
| API Key   | 在个人设置中生成 | CLI/脚本调用 |
| OAuth2    | 第三方应用授权  | 集成其他平台   |

**API 版本管理**：

text

API 版本策略：

- URL 路径版本：/api/v1/cases
- 请求头版本：Accept: application/vnd.api-debug.v1+json
  版本生命周期：
- v1: 稳定版本，长期支持
- v2: 当前开发版本
- 废弃版本提前 6 个月通知

**OpenAPI 文档**：

text

访问地址：/api/docs
支持：

- Swagger UI 交互式文档
- ReDoc 文档
- 导出 OpenAPI 3.0 规范
- SDK 代码生成（TypeScript/Python/Java）

* * *

五、前端页面扩展
--------

### 5.1 新增页面结构

text

Phase 4 新增页面
├── 团队管理
│   ├── 租户设置
│   ├── 用户管理
│   ├── 角色权限配置
│   └── 配额管理
├── 项目管理
│   ├── 项目列表
│   ├── 项目设置
│   ├── 版本管理
│   └── 成员管理
├── 资产中心
│   ├── 模板市场
│   ├── 共享资产
│   └── 我的模板
├── 质量大盘
│   ├── 全局概览
│   ├── 项目仪表盘
│   ├── 个人仪表盘
│   └── 自定义仪表盘
├── 智能分析
│   ├── 失败聚类分析
│   ├── 变更影响预测
│   ├── 告警规则配置
│   └── 告警历史
├── 插件市场
│   ├── 插件列表
│   ├── 已安装插件
│   └── 插件配置
└── 系统设置
    ├── 开放 API 管理
    ├── SSO 配置
    ├── 审计日志
    └── 系统监控

### 5.2 核心页面设计

#### 5.2.1 质量大盘

text

┌─────────────────────────────────────────────────────────────────────────────────┐
│  质量大盘 - 全局概览                                              [自定义] [刷新] │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 时间范围：[最近 30 天 ▼]  项目：[全部项目 ▼]  版本：[全部版本 ▼]          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │ 📊 项目总数   │ │ 🧪 总用例数   │ │ ✅ 今日通过率 │ │ 🐛 未解决缺陷 │          │
│  │    8         │ │   1,256      │ │   96.8%      │ │     23       │          │
│  │   ↑ 2        │ │   ↑ 56       │ │   ↑ 1.2%     │ │   ↓ 5        │          │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘          │
│                                                                                 │
│  ┌─────────────────────────────────────────┐ ┌───────────────────────────────┐ │
│  │           测试通过率趋势                  │ │         缺陷状态分布            │ │
│  │  100% │                    ╭─╮          │ │        ┌────────────────┐      │ │
│  │   95% │        ╭───╮     ╭─╯ ╰─╮        │ │        │  🔴 待处理  8   │      │ │
│  │   90% │      ╭─╯   ╰─╮ ╭─╯     ╰─╮      │ │        │  🟡 处理中  5   │      │ │
│  │   85% │    ╭─╯       ╰─╯         ╰─╮    │ │        │  🟢 已解决 12   │      │ │
│  │   80% └────────────────────────────────  │ │        │  ⚪ 已关闭 18   │      │ │
│  │         1/1   1/8   1/15  1/22  1/29    │ │        └────────────────┘      │ │
│  └─────────────────────────────────────────┘ └───────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────┐ ┌───────────────────────────────┐ │
│  │           项目质量排行榜                  │ │         覆盖率趋势              │ │
│  │  ┌─────────────────────────────────┐    │ │                               │ │
│  │  │ 排名 │ 项目     │ 通过率 │ 覆盖率│    │ │  100% │                         │ │
│  │  ├─────────────────────────────────┤    │ │   80% │      ╭───╮              │ │
│  │  │  1  │ 用户服务  │ 99.2% │ 82.5%│    │ │   60% │    ╭─╯   ╰─╮            │ │
│  │  │  2  │ 订单服务  │ 98.1% │ 78.3%│    │ │   40% │  ╭─╯       ╰─╮          │ │
│  │  │  3  │ 支付服务  │ 96.5% │ 75.8%│    │ │   20% │──╯           ╰──        │ │
│  │  │  4  │ 商品服务  │ 95.2% │ 72.1%│    │ │    0% └────────────────────────  │ │
│  │  │  5  │ 营销服务  │ 93.8% │ 68.4%│    │ │                               │ │
│  │  └─────────────────────────────────┘    │ └───────────────────────────────┘ │
│  └─────────────────────────────────────────┘                                    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          近期告警                                        │   │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │   │
│  │  │ 时间         │ 级别   │ 项目     │ 告警内容                         │  │   │
│  │  ├───────────────────────────────────────────────────────────────────┤  │   │
│  │  │ 10:32:15    │ 🔴高   │ 订单服务 │ 订单创建接口失败率突增至 8.5%      │  │   │
│  │  │ 09:15:42    │ 🟡中   │ 用户服务 │ 响应时间 P95 超过基线 2.3 倍      │  │   │
│  │  │ 昨日 22:10  │ 🔴高   │ 支付服务 │ 覆盖率下降 5.2%                  │  │   │
│  │  └───────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

#### 5.2.2 智能分析 - 失败聚类

text

┌─────────────────────────────────────────────────────────────────────────────────┐
│  智能分析 - 失败聚类分析                                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  项目：[用户服务 ▼]  时间：[最近 7 天 ▼]                    [刷新分析]           │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          失败聚类概览                                    │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │                                                           │    │   │
│  │  │     ╭───────╮                                              │    │   │
│  │  │    ╭┤ 集群1  │  连接超时 (45 次)                              │    │   │
│  │  │   ╭┤│ 45次  │  主要接口：/api/login, /api/verify             │    │   │
│  │  │  ╭┤│╰───────╯  首次出现：2026-01-05 10:23                    │    │   │
│  │  │ ╭┤││                                                         │    │   │
│  │  │ ││││  ╭───────╮                                              │    │   │
│  │  │ │││╰─┤ 集群2  │  断言失败 - code!=0 (32 次)                    │    │   │
│  │  │ │││  │ 32次  │  主要接口：/api/user/info, /api/user/update    │    │   │
│  │  │ │││  ╰───────╯  首次出现：2026-01-03 14:52                    │    │   │
│  │  │ │││                                                           │    │   │
│  │  │ │││      ╭───────╮                                            │    │   │
│  │  │ │╰──────┤ 集群3  │  JSON 解析错误 (12 次)                       │    │   │
│  │  │ │       │ 12次  │  主要接口：/api/export/data                  │    │   │
│  │  │ │       ╰───────╯  首次出现：2026-01-06 09:15                  │    │   │
│  │  │ │                                                              │    │   │
│  │  │ ╰─────────────╮                                                │    │   │
│  │  │               ╰──╮  ╭───────╮                                  │    │   │
│  │  ╰──────────────────╰──┤ 集群4  │  500 内部错误 (8 次)               │    │   │
│  │                        │ 8次   │  主要接口：/api/payment/create      │    │   │
│  │                        ╰───────╯  首次出现：2026-01-07 16:30        │    │   │
│  │                                                           │    │   │
│  └─────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 集群详情：集群1 - 连接超时                                                 │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                         │   │
│  │  错误模式：ReadTimeoutError / ConnectTimeoutError                         │   │
│  │                                                                         │   │
│  │  影响范围：                                                              │   │
│  │  - 用例：TC-001(登录), TC-002(验证), TC-015(刷新Token)                    │   │
│  │  - 环境：测试环境、预发布环境                                              │   │
│  │                                                                         │   │
│  │  时间分布：                                                              │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  20 │     ■                                                      │    │   │
│  │  │  15 │   ■ ■ ■                                                    │    │   │
│  │  │  10 │ ■ ■ ■ ■ ■                                                  │    │   │
│  │  │   5 │ ■ ■ ■ ■ ■ ■ ■                                              │    │   │
│  │  │   0 └──────────────────────────────────────────────────────────  │    │   │
│  │  │      01/05 01/06 01/07 01/08 01/09 01/10 01/11                    │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                         │   │
│  │  🤖 AI 根因分析：                                                        │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 该问题可能与 2026-01-05 部署的代码变更有关。                        │    │   │
│  │  │ 相关 Commit: abc123 - "优化数据库连接池配置"                        │    │   │
│  │  │ 建议：检查连接池超时配置，当前配置为 5s，建议调整为 30s。              │    │   │
│  │  │ 受影响用例已自动添加到回归测试集。                                   │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                         │   │
│  │  [查看详细日志] [关联缺陷] [标记为已知问题] [忽略此集群]                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

#### 5.2.3 变更影响分析

text

┌─────────────────────────────────────────────────────────────────────────────────┐
│  智能分析 - 变更影响预测                                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Commit：[abc123def ▼]  分支：[main]                              [分析]        │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          变更摘要                                        │   │
│  │                                                                         │   │
│  │  Commit: abc123def456                                                   │   │
│  │  Author: 张三                                                            │   │
│  │  Message: feat: 重构用户服务认证逻辑                                      │   │
│  │  Time: 2026-01-11 09:30:00                                              │   │
│  │                                                                         │   │
│  │  变更文件 (5)：                                                          │   │
│  │  - src/services/UserService.java (修改, +45/-12)                         │   │
│  │  - src/controllers/AuthController.java (修改, +23/-8)                    │   │
│  │  - src/utils/TokenUtil.java (修改, +15/-3)                               │   │
│  │  - src/models/User.java (修改, +8/-2)                                    │   │
│  │  - src/config/SecurityConfig.java (新增)                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          影响预测                                        │   │
│  │                                                                         │   │
│  │  风险等级：🔴 高风险                                                      │   │
│  │                                                                         │   │
│  │  直接影响的用例 (8)：                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ ☑ TC-001 用户登录                    │ 关联代码: AuthController   │    │   │
│  │  │ ☑ TC-002 Token 验证                  │ 关联代码: TokenUtil        │    │   │
│  │  │ ☑ TC-003 用户登出                    │ 关联代码: AuthController   │    │   │
│  │  │ ☑ TC-015 Token 刷新                  │ 关联代码: TokenUtil        │    │   │
│  │  │ ☑ TC-021 获取用户信息                │ 关联代码: UserService      │    │   │
│  │  │ ☑ TC-022 更新用户信息                │ 关联代码: UserService      │    │   │
│  │  │ ☑ TC-035 用户注册                    │ 关联代码: UserService      │    │   │
│  │  │ ☑ TC-042 密码重置                    │ 关联代码: UserService      │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                         │   │
│  │  间接影响的场景 (3)：                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ ☑ 用户登录流程（包含 TC-001, TC-021）                              │    │   │
│  │  │ ☑ 用户注册流程（包含 TC-035, TC-001）                              │    │   │
│  │  │ ☑ 个人中心流程（包含 TC-021, TC-022）                              │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                         │   │
│  │  覆盖率影响：                                                            │   │
│  │  - 新增代码行覆盖率预估：0%（建议补充单测）                               │   │
│  │  - 变更文件覆盖率变化：UserService.java 82% → 68% (-14%)                 │   │
│  │                                                                         │   │
│  │  🤖 AI 建议：                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 1. 建议立即执行以上 8 个用例和 3 个场景的回归测试                    │    │   │
│  │  │ 2. 新增代码缺少单元测试覆盖，建议补充以下测试：                       │    │   │
│  │  │    - SecurityConfig 的配置测试                                    │    │   │
│  │  │    - TokenUtil 新增方法的边界测试                                  │    │   │
│  │  │ 3. 该变更涉及认证核心逻辑，建议在测试环境充分验证后再合并              │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [立即执行推荐测试] [创建测试任务] [添加到质量门禁]                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

* * *

六、CLI 工具扩展
----------

### 6.1 Phase 4 新增命令

text

api-debug
├── auth                           # 认证管理
│   ├── login                     # 登录
│   ├── logout                    # 登出
│   └── whoami                    # 查看当前用户
├── project                        # 项目管理
│   ├── list                      # 列出项目
│   ├── create <name>             # 创建项目
│   ├── switch <id>               # 切换当前项目
│   └── members                   # 成员管理
├── version                        # 版本管理
│   ├── list                      # 列出版本
│   ├── create <name>             # 创建版本
│   ├── release <id>              # 发布版本
│   └── report <id>               # 查看版本报告
├── dashboard                      # 大盘数据
│   ├── overview                  # 全局概览
│   ├── project [id]              # 项目大盘
│   └── export                    # 导出数据
├── ai                             # 智能分析
│   ├── analyze-failures          # 失败分析
│   ├── predict-impact <commit>   # 变更影响预测
│   └── suggest-tests <commit>    # 推荐测试用例
├── plugin                         # 插件管理
│   ├── list                      # 列出插件
│   ├── install <path>            # 安装插件
│   ├── uninstall <id>            # 卸载插件
│   └── enable/disable <id>       # 启用/禁用
└── config                         # 配置管理
    ├── get <key>                 # 获取配置
    ├── set <key> <value>         # 设置配置
    └── init                      # 初始化配置

### 6.2 命令示例

bash

# 登录

api-debug auth login --username admin --password xxx

# 切换项目

api-debug project switch user-service

# 创建版本

api-debug version create v2.1.0 --tag v2.1.0 --commit abc123

# 查看质量大盘

api-debug dashboard overview --format table

# AI 分析失败

api-debug ai analyze-failures --project user-service --days 7

# 预测变更影响

api-debug ai predict-impact abc123def --format json

# 安装插件

api-debug plugin install ./custom-notifier.zip

# 导出配置

api-debug config export > config.yaml

* * *

七、部署架构
------

### 7.1 生产部署架构

text

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              生产部署架构                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                              ┌─────────────┐                                    │
│                              │   CDN/Nginx │                                    │
│                              │  静态资源    │                                    │
│                              └──────┬──────┘                                    │
│                                     │                                           │
│                              ┌──────▼──────┐                                    │
│                              │   负载均衡   │                                    │
│                              │   Nginx     │                                    │
│                              └──────┬──────┘                                    │
│                                     │                                           │
│              ┌──────────────────────┼──────────────────────┐                    │
│              │                      │                      │                    │
│       ┌──────▼──────┐        ┌──────▼──────┐        ┌──────▼──────┐            │
│       │  Web Server │        │  Web Server │        │  Web Server │            │
│       │  (FastAPI)  │        │  (FastAPI)  │        │  (FastAPI)  │            │
│       │  Port 8000  │        │  Port 8000  │        │  Port 8000  │            │
│       └──────┬──────┘        └──────┬──────┘        └──────┬──────┘            │
│              │                      │                      │                    │
│              └──────────────────────┼──────────────────────┘                    │
│                                     │                                           │
│       ┌─────────────────────────────┼─────────────────────────────┐             │
│       │                             │                             │             │
│  ┌────▼────┐                  ┌────▼────┐                  ┌─────▼─────┐       │
│  │PostgreSQL│                 │  Redis  │                  │ ClickHouse│       │
│  │  主从    │                 │  集群    │                  │   集群    │       │
│  └─────────┘                  └─────────┘                  └───────────┘       │
│                                                                                 │
│  ┌─────────┐                  ┌─────────┐                  ┌───────────┐       │
│  │ MinIO   │                  │ Celery  │                  │ Prometheus│       │
│  │ 对象存储 │                  │ Workers │                  │ + Grafana │       │
│  └─────────┘                  └─────────┘                  └───────────┘       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

### 7.2 容器化部署

yaml

# docker-compose.yml 示例

version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: api_debug
      POSTGRES_USER: api_debug
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://api_debug:${DB_PASSWORD}@postgres/api_debug
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
  worker:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://api_debug:${DB_PASSWORD}@postgres/api_debug
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
volumes:
  postgres_data:
  redis_data:

* * *

八、里程碑与交付物
---------

### 8.1 八周计划

| 周次             | 主题            | 核心交付物              | 验收标准            |
| -------------- | ------------- | ------------------ | --------------- |
| **Week 13-14** | 多租户与权限        | 用户系统 + RBAC + 租户隔离 | 多用户可登录，权限控制生效   |
| **Week 15-16** | 项目与版本         | 项目管理 + 版本追溯        | 按项目组织资产，版本报告可查  |
| **Week 17-18** | 智能分析引擎        | 失败聚类 + 变更影响预测      | AI 分析功能可用，准确率达标 |
| **Week 19-20** | 质量大盘 + 开放 API | 仪表盘 + 完整 API 文档    | 大盘可自定义，API 可调用  |

### 8.2 验收清单

| 序号  | 验收项           | 验收方式           |
| --- | ------------- | -------------- |
| 1   | 用户注册/登录功能     | 手动测试           |
| 2   | 租户数据隔离        | 不同租户数据不可见      |
| 3   | RBAC 权限控制     | 不同角色权限不同       |
| 4   | 项目 CRUD 与成员管理 | 手动测试           |
| 5   | 版本创建与质量报告     | 创建版本验证         |
| 6   | 资产模板与共享       | 分享用例到其他项目      |
| 7   | 失败聚类分析        | 分析历史失败数据验证     |
| 8   | 变更影响预测        | 提交代码后预测验证      |
| 9   | 智能告警规则        | 配置规则触发验证       |
| 10  | 自定义仪表盘        | 添加组件验证         |
| 11  | 开放 API 调用     | API Token 调用验证 |
| 12  | 插件安装与执行       | 安装自定义插件验证      |
| 13  | 性能基线建立        | 采集数据建立基线       |
| 14  | 审计日志记录        | 操作被记录可查        |

* * *

九、Phase 4 完成后的平台全景
------------------

text

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           API Debug Tool 质量保障平台                             │
│                                最终能力全景                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          开发阶段                                        │   │
│  │  • IDE 插件：代码变更自动推荐测试用例                                      │   │
│  │  • Pre-commit 钩子：本地质量检查                                          │   │
│  │  • 代码覆盖率实时反馈                                                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          测试阶段                                        │   │
│  │  • API 调试与用例管理                                                    │   │
│  │  • 场景编排与数据驱动                                                    │   │
│  │  • 自动化回归测试                                                        │   │
│  │  • 压力测试与性能分析                                                    │   │
│  │  • Mock 服务                                                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          质量保障                                        │   │
│  │  • 单元测试集成                                                          │   │
│  │  • 代码覆盖率采集                                                        │   │
│  │  • 缺陷管理（内置 + 第三方对接）                                          │   │
│  │  • 质量门禁                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          运维监控                                        │   │
│  │  • 定时巡检任务                                                          │   │
│  │  • 智能告警                                                              │   │
│  │  • 性能基线监控                                                          │   │
│  │  • 线上问题快速复现                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          管理与决策                                      │   │
│  │  • 质量大盘（全局/项目/个人）                                             │   │
│  │  • 趋势分析与预测                                                        │   │
│  │  • 团队协作与资产共享                                                    │   │
│  │  • 多租户权限管理                                                        │   │
│  │  • 审计日志与合规                                                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          开放能力                                        │   │
│  │  • 完整 REST API                                                        │   │
│  │  • 插件体系                                                              │   │
│  │  • Webhook 集成                                                          │   │
│  │  • CI/CD 原生支持                                                        │   │
│  │  • 多语言 SDK                                                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

* * *

十、总结
----

经过四个阶段的迭代，API Debug Tool 从一个简单的 API 调试工具，演进为一个**企业级质量保障平台**：

| 阶段      | 核心能力              | 解决的问题   |
| ------- | ----------------- | ------- |
| Phase 1 | 数据持久化 + 基础用例管理    | 从单机到平台化 |
| Phase 2 | 自动化测试 + 定时任务      | 从手动到自动化 |
| Phase 3 | 代码质量融合 + 缺陷管理     | 从黑盒到全链路 |
| Phase 4 | 多租户 + 智能分析 + 开放能力 | 从工具到平台  |

**核心价值总结**：

* **开发**：代码变更智能推荐测试，覆盖率实时反馈

* **测试**：一站式 API 测试管理，自动化回归

* **运维**：线上巡检与智能告警，问题快速定位

* **管理**：质量大盘一目了然，数据驱动决策
