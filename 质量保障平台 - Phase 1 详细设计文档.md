# API Debug Tool 质量保障平台 - Phase 1 详细设计文档

## 一、Phase 1 概述

### 1.1 阶段定位

将当前**单机 API 调试工具**升级为**具备数据持久化能力的基础测试平台**。

### 1.2 核心目标

| 目标       | 说明                          | 成功标准                  |
| :--------- | :---------------------------- | :------------------------ |
| 数据持久化 | 从 LocalStorage 迁移到 SQLite | 关闭浏览器后数据不丢失    |
| 用例管理   | 接口请求保存为可复用用例      | 支持 CRUD、文件夹组织     |
| 环境管理   | 多环境配置与切换              | 变量正确替换              |
| 断言机制   | 自动校验响应结果              | 支持状态码、JSONPath 断言 |
| 场景编排   | 多用例串联执行                | 支持变量提取与传递        |
| CLI 工具   | 命令行执行测试                | 输出 JUnit 格式报告       |

### 1.3 不包含内容

- 单元测试与覆盖率集成（Phase 3）
- 缺陷管理模块（Phase 3）
- 多用户与权限（Phase 4）
- 定时任务与监控（Phase 2）

------

## 二、系统架构设计

### 2.1 整体架构图

text

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户接入层                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │   Web 前端        │  │   CLI 工具        │  │   API 调用     │ │
│  │  (Vue 3 + Vite)   │  │  (Python + Click) │  │   (HTTP Client)│ │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘ │
└───────────┼─────────────────────┼─────────────────────┼─────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      核心服务层 (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      API Router                            │ │
│  │  /cases  │  /environments  │  /scenarios  │  /logs        │ │
│  └────────────────────────────┬───────────────────────────────┘ │
│                               ▼                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    核心引擎模块                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │ 变量引擎     │ │ 断言引擎     │ │ 请求执行器           │  │ │
│  │  │ Variable    │ │ Assertion   │ │ RequestExecutor     │  │ │
│  │  │ Engine      │ │ Engine      │ │                     │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  │  ┌─────────────┐ ┌─────────────┐                           │ │
│  │  │ 提取引擎     │ │ 脚本引擎     │                           │ │
│  │  │ Extract     │ │ Script      │                           │ │
│  │  │ Engine      │ │ Engine      │                           │ │
│  │  └─────────────┘ └─────────────┘                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │   SQLite 数据库   │  │   文件存储         │  │   缓存层       │ │
│  │  (SQLAlchemy)    │  │  (响应体/附件)     │  │   (Redis可选)  │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```



### 2.2 模块职责说明

| 模块           | 职责                                                      | 依赖             |
| :------------- | :-------------------------------------------------------- | :--------------- |
| **变量引擎**   | 管理多层级变量（环境/场景/步骤），支持 `{{var}}` 语法替换 | 无               |
| **断言引擎**   | 执行断言规则，支持状态码/JSONPath/响应头/响应时间         | JSONPath 库      |
| **提取引擎**   | 从响应中提取变量（JSONPath/正则/Header）                  | 变量引擎         |
| **脚本引擎**   | 执行前置/后置脚本（Python 安全沙箱）                      | RestrictedPython |
| **请求执行器** | 统一请求执行入口，协调各引擎完成请求                      | 上述所有引擎     |
| **数据访问层** | ORM 模型定义与数据库操作                                  | SQLAlchemy       |

------

## 三、数据模型设计

### 3.1 ER 图

text

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│ Environment │       │  TestCase   │       │    Scenario     │
├─────────────┤       ├─────────────┤       ├─────────────────┤
│ id          │       │ id          │       │ id              │
│ name        │       │ name        │       │ name            │
│ variables   │       │ method      │       │ description     │
│ is_default  │       │ url         │       │ folder_path     │
└─────────────┘       │ headers     │       │ variables       │
                      │ body        │       └────────┬────────┘
                      │ assertions  │                │
                      │ pre_script  │                │ 1:N
                      │ post_script │                │
                      │ folder_path │       ┌────────▼────────┐
                      └──────┬──────┘       │ ScenarioStep    │
                             │              ├─────────────────┤
                             │ 1:N          │ id              │
                             │              │ scenario_id     │
                      ┌──────▼──────┐       │ case_id         │
                      │ ExecutionLog│◄──────┤ step_order      │
                      ├─────────────┤       │ extract_rules   │
                      │ id          │       │ skip_on_failure │
                      │ case_id     │       └─────────────────┘
                      │ scenario_id │
                      │ status      │
                      │ response    │
                      │ assertion   │
                      └─────────────┘
```



### 3.2 数据表详细设计

#### 3.2.1 用例表 `test_case`

| 字段             | 类型         | 约束                      | 说明                            |
| :--------------- | :----------- | :------------------------ | :------------------------------ |
| id               | INTEGER      | PRIMARY KEY               | 自增主键                        |
| name             | VARCHAR(200) | NOT NULL                  | 用例名称                        |
| description      | TEXT         |                           | 用例描述                        |
| method           | VARCHAR(10)  | NOT NULL                  | GET/POST/PUT/DELETE/PATCH       |
| url              | TEXT         | NOT NULL                  | 请求 URL，支持变量              |
| headers          | TEXT         |                           | JSON 格式请求头                 |
| params           | TEXT         |                           | JSON 格式 Query 参数            |
| body             | TEXT         |                           | 请求体内容                      |
| body_type        | VARCHAR(20)  | DEFAULT 'json'            | json/form/xml/raw/binary        |
| auth_type        | VARCHAR(20)  | DEFAULT 'none'            | none/basic/bearer/api_key       |
| auth_config      | TEXT         |                           | JSON 格式认证配置               |
| folder_path      | VARCHAR(500) |                           | 文件夹路径，如 "/用户模块/登录" |
| sort_order       | INTEGER      | DEFAULT 0                 | 排序序号                        |
| assertions       | TEXT         |                           | JSON 数组，断言规则             |
| pre_script       | TEXT         |                           | 前置脚本                        |
| post_script      | TEXT         |                           | 后置脚本                        |
| timeout          | INTEGER      | DEFAULT 30                | 超时时间（秒）                  |
| follow_redirects | BOOLEAN      | DEFAULT 1                 | 是否跟随重定向                  |
| verify_ssl       | BOOLEAN      | DEFAULT 1                 | 是否验证 SSL                    |
| created_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                        |
| updated_at       | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                        |

**索引**：

- `idx_test_case_folder` ON (folder_path)
- `idx_test_case_method` ON (method)

#### 3.2.2 断言规则 JSON 结构

json

```
[
  {
    "id": "assert_1",
    "type": "status_code",
    "operator": "equals",
    "expected": 200,
    "enabled": true
  },
  {
    "id": "assert_2", 
    "type": "json_path",
    "path": "$.code",
    "operator": "equals",
    "expected": 0,
    "enabled": true
  },
  {
    "id": "assert_3",
    "type": "response_time",
    "operator": "less_than",
    "expected": 1000,
    "enabled": true
  },
  {
    "id": "assert_4",
    "type": "header",
    "header_name": "Content-Type",
    "operator": "contains",
    "expected": "application/json",
    "enabled": true
  }
]
```



**断言类型与操作符对照表**：

| 断言类型      | 适用操作符                                                   | 说明             |
| :------------ | :----------------------------------------------------------- | :--------------- |
| status_code   | equals, not_equals                                           | HTTP 状态码      |
| json_path     | equals, not_equals, contains, exists, not_exists, greater_than, less_than | JSONPath 取值    |
| response_time | less_than, greater_than                                      | 响应耗时（毫秒） |
| header        | equals, contains, exists                                     | 响应头校验       |
| body_contains | contains, not_contains                                       | 响应体包含文本   |

#### 3.2.3 环境表 `environment`

| 字段        | 类型        | 约束                      | 说明                  |
| :---------- | :---------- | :------------------------ | :-------------------- |
| id          | INTEGER     | PRIMARY KEY               | 自增主键              |
| name        | VARCHAR(50) | UNIQUE, NOT NULL          | 环境名称              |
| description | TEXT        |                           | 环境描述              |
| variables   | TEXT        |                           | JSON 对象，变量键值对 |
| is_default  | BOOLEAN     | DEFAULT 0                 | 是否为默认环境        |
| sort_order  | INTEGER     | DEFAULT 0                 | 排序序号              |
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间              |
| updated_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 更新时间              |

**variables 字段示例**：

json

```
{
  "base_url": "http://localhost:8080",
  "api_key": "dev-api-key-12345",
  "timeout": 30
}
```



#### 3.2.4 场景表 `scenario`

| 字段        | 类型         | 约束                      | 说明                        |
| :---------- | :----------- | :------------------------ | :-------------------------- |
| id          | INTEGER      | PRIMARY KEY               | 自增主键                    |
| name        | VARCHAR(200) | NOT NULL                  | 场景名称                    |
| description | TEXT         |                           | 场景描述                    |
| folder_path | VARCHAR(500) |                           | 文件夹路径                  |
| variables   | TEXT         |                           | JSON 对象，场景级变量初始值 |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 创建时间                    |
| updated_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | 更新时间                    |

#### 3.2.5 场景步骤表 `scenario_step`

| 字段            | 类型    | 约束         | 说明                    |
| :-------------- | :------ | :----------- | :---------------------- |
| id              | INTEGER | PRIMARY KEY  | 自增主键                |
| scenario_id     | INTEGER | FOREIGN KEY  | 关联场景 ID             |
| case_id         | INTEGER | FOREIGN KEY  | 关联用例 ID             |
| step_order      | INTEGER | NOT NULL     | 步骤顺序                |
| extract_rules   | TEXT    |              | JSON 数组，变量提取规则 |
| skip_on_failure | BOOLEAN | DEFAULT 1    | 失败时是否跳过后续步骤  |
| retry_times     | INTEGER | DEFAULT 0    | 失败重试次数            |
| retry_interval  | INTEGER | DEFAULT 1000 | 重试间隔（毫秒）        |
| enabled         | BOOLEAN | DEFAULT 1    | 是否启用                |

**唯一索引**：`idx_scenario_step_order` ON (scenario_id, step_order)

#### 3.2.6 变量提取规则 JSON 结构

json

```
[
  {
    "id": "extract_1",
    "name": "access_token",
    "source": "response_body",
    "path": "$.data.token",
    "scope": "scenario",
    "enabled": true
  },
  {
    "id": "extract_2",
    "name": "user_id",
    "source": "response_body",
    "path": "$.data.user.id",
    "scope": "scenario",
    "enabled": true
  },
  {
    "id": "extract_3",
    "name": "request_id",
    "source": "response_header",
    "header_name": "X-Request-Id",
    "scope": "scenario",
    "enabled": true
  }
]
```



**提取源类型**：

| source          | 说明        | 需要字段                   |
| :-------------- | :---------- | :------------------------- |
| response_body   | 响应体 JSON | path (JSONPath)            |
| response_header | 响应头      | header_name                |
| response_cookie | Cookie      | cookie_name                |
| regex           | 正则提取    | pattern (从响应体文本提取) |

#### 3.2.7 执行记录表 `execution_log`

| 字段              | 类型        | 约束                      | 说明                                          |
| :---------------- | :---------- | :------------------------ | :-------------------------------------------- |
| id                | INTEGER     | PRIMARY KEY               | 自增主键                                      |
| case_id           | INTEGER     | FOREIGN KEY               | 关联用例 ID                                   |
| scenario_id       | INTEGER     | FOREIGN KEY               | 关联场景 ID                                   |
| scenario_step_id  | INTEGER     | FOREIGN KEY               | 关联场景步骤 ID                               |
| execution_type    | VARCHAR(20) |                           | single/scenario/schedule                      |
| execution_id      | VARCHAR(50) |                           | 批量执行的统一 ID                             |
| request_url       | TEXT        |                           | 最终请求 URL（变量已替换）                    |
| request_method    | VARCHAR(10) |                           | 请求方法                                      |
| request_headers   | TEXT        |                           | 请求头快照                                    |
| request_body      | TEXT        |                           | 请求体快照                                    |
| response_status   | INTEGER     |                           | 响应状态码                                    |
| response_headers  | TEXT        |                           | 响应头快照                                    |
| response_body     | TEXT        |                           | 响应体快照                                    |
| response_size     | INTEGER     |                           | 响应体大小（字节）                            |
| response_time_ms  | INTEGER     |                           | 响应耗时（毫秒）                              |
| status            | VARCHAR(20) |                           | pending/running/success/failure/error/skipped |
| error_message     | TEXT        |                           | 错误信息                                      |
| assertion_results | TEXT        |                           | JSON 数组，断言执行结果                       |
| environment_id    | INTEGER     | FOREIGN KEY               | 使用的环境 ID                                 |
| triggered_by      | VARCHAR(50) |                           | user/schedule/cli                             |
| created_at        | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 执行时间                                      |

**索引**：

- `idx_execution_log_case` ON (case_id)
- `idx_execution_log_scenario` ON (scenario_id)
- `idx_execution_log_created` ON (created_at)
- `idx_execution_log_status` ON (status)

------

## 四、API 接口设计

### 4.1 接口总览

| 模块         | 方法   | 路径                                  | 说明                                 |
| :----------- | :----- | :------------------------------------ | :----------------------------------- |
| **用例管理** | GET    | `/api/cases`                          | 获取用例列表（支持分页、文件夹筛选） |
|              | POST   | `/api/cases`                          | 创建用例                             |
|              | GET    | `/api/cases/{id}`                     | 获取用例详情                         |
|              | PUT    | `/api/cases/{id}`                     | 更新用例                             |
|              | DELETE | `/api/cases/{id}`                     | 删除用例                             |
|              | POST   | `/api/cases/{id}/run`                 | 执行单个用例                         |
|              | POST   | `/api/cases/{id}/duplicate`           | 复制用例                             |
|              | POST   | `/api/cases/batch-delete`             | 批量删除                             |
|              | GET    | `/api/folders`                        | 获取文件夹树                         |
| **环境管理** | GET    | `/api/environments`                   | 获取环境列表                         |
|              | POST   | `/api/environments`                   | 创建环境                             |
|              | PUT    | `/api/environments/{id}`              | 更新环境                             |
|              | DELETE | `/api/environments/{id}`              | 删除环境                             |
|              | POST   | `/api/environments/{id}/set-default`  | 设为默认环境                         |
| **场景管理** | GET    | `/api/scenarios`                      | 获取场景列表                         |
|              | POST   | `/api/scenarios`                      | 创建场景                             |
|              | GET    | `/api/scenarios/{id}`                 | 获取场景详情                         |
|              | PUT    | `/api/scenarios/{id}`                 | 更新场景                             |
|              | DELETE | `/api/scenarios/{id}`                 | 删除场景                             |
|              | POST   | `/api/scenarios/{id}/run`             | 执行场景                             |
|              | POST   | `/api/scenarios/{id}/steps`           | 添加场景步骤                         |
|              | PUT    | `/api/scenarios/{id}/steps/{step_id}` | 更新步骤                             |
|              | DELETE | `/api/scenarios/{id}/steps/{step_id}` | 删除步骤                             |
|              | PUT    | `/api/scenarios/{id}/steps/reorder`   | 调整步骤顺序                         |
| **执行记录** | GET    | `/api/logs`                           | 获取执行记录列表                     |
|              | GET    | `/api/logs/{id}`                      | 获取执行详情                         |
|              | DELETE | `/api/logs/{id}`                      | 删除执行记录                         |
|              | DELETE | `/api/logs/batch-delete`              | 批量删除执行记录                     |
| **数据迁移** | GET    | `/api/migrate/export`                 | 导出 LocalStorage 数据               |
|              | POST   | `/api/migrate/import`                 | 导入数据到数据库                     |
| **系统**     | GET    | `/api/health`                         | 健康检查                             |

### 4.2 核心接口详细说明

#### 4.2.1 执行用例

**请求**：

text

```
POST /api/cases/{id}/run
Content-Type: application/json

{
  "environment_id": 1,        // 可选，不传使用默认环境
  "variables": {              // 可选，临时覆盖变量
    "user_id": "12345"
  }
}
```



**响应**：

json

```
{
  "code": 0,
  "message": "success",
  "data": {
    "execution_id": "exec_20260110_001",
    "case_id": 1,
    "status": "success",
    "response": {
      "status_code": 200,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "code": 0,
        "data": {
          "token": "eyJhbGciOiJIUzI1NiIs..."
        }
      },
      "size": 1024,
      "time_ms": 156
    },
    "assertion_results": [
      {
        "id": "assert_1",
        "type": "status_code",
        "passed": true,
        "expected": 200,
        "actual": 200,
        "message": "状态码断言通过"
      },
      {
        "id": "assert_2",
        "type": "json_path",
        "path": "$.code",
        "passed": true,
        "expected": 0,
        "actual": 0,
        "message": "JSONPath 断言通过"
      }
    ],
    "extracted_variables": {
      "token": "eyJhbGciOiJIUzI1NiIs..."
    }
  }
}
```



#### 4.2.2 执行场景

**请求**：

text

```
POST /api/scenarios/{id}/run
Content-Type: application/json

{
  "environment_id": 1,
  "variables": {
    "test_user": "demo@example.com"
  }
}
```



**响应**：

json

```
{
  "code": 0,
  "message": "success",
  "data": {
    "execution_id": "exec_20260110_002",
    "scenario_id": 1,
    "status": "success",
    "summary": {
      "total_steps": 3,
      "passed_steps": 3,
      "failed_steps": 0,
      "skipped_steps": 0,
      "total_time_ms": 1245
    },
    "steps": [
      {
        "step_order": 1,
        "case_id": 1,
        "case_name": "用户登录",
        "status": "success",
        "response_time_ms": 234,
        "extracted": {
          "token": "eyJhbGciOiJIUzI1NiIs...",
          "user_id": "12345"
        }
      },
      {
        "step_order": 2,
        "case_id": 2,
        "case_name": "获取用户信息",
        "status": "success",
        "response_time_ms": 156,
        "extracted": {}
      },
      {
        "step_order": 3,
        "case_id": 3,
        "case_name": "更新用户资料",
        "status": "success",
        "response_time_ms": 198,
        "extracted": {}
      }
    ],
    "final_variables": {
      "token": "eyJhbGciOiJIUzI1NiIs...",
      "user_id": "12345",
      "test_user": "demo@example.com"
    }
  }
}
```



#### 4.2.3 数据导入

**请求**：

text

```
POST /api/migrate/import
Content-Type: application/json

{
  "collections": [
    {
      "name": "用户模块",
      "cases": [
        {
          "name": "用户登录",
          "method": "POST",
          "url": "{{base_url}}/api/login",
          "headers": {...},
          "body": {...}
        }
      ]
    }
  ],
  "environments": [
    {
      "name": "测试环境",
      "variables": {...}
    }
  ],
  "history": [...]
}
```



**响应**：

json

```
{
  "code": 0,
  "message": "success",
  "data": {
    "imported": {
      "cases": 25,
      "environments": 3,
      "folders": 5
    },
    "errors": []
  }
}
```



------

## 五、核心引擎设计

### 5.1 变量引擎

**设计目标**：管理多层级变量，支持 `{{variable}}` 语法替换

**变量优先级（从高到低）**：

| 优先级 | 作用域       | 生命周期     | 典型用途           |
| :----- | :----------- | :----------- | :----------------- |
| 1      | 步骤变量     | 单次请求     | 临时覆盖、动态生成 |
| 2      | 场景变量     | 场景执行期间 | 步骤间数据传递     |
| 3      | 数据驱动变量 | 单次迭代     | CSV/JSON 数据行    |
| 4      | 环境变量     | 当前环境     | base_url、api_key  |
| 5      | 全局变量     | 全局         | 跨环境共享配置     |

**处理流程**：

text

```
输入文本: "{{base_url}}/api/user/{{user_id}}"

1. 正则匹配所有 {{...}} 模式
2. 按优先级查询各作用域变量值
3. 递归替换（支持嵌套变量）
4. 未找到的变量保持原样并记录警告
5. 输出最终文本
```



### 5.2 断言引擎

**设计目标**：执行断言规则，判断测试是否通过

**支持的断言类型**：

| 类型          | 说明             | 示例               |
| :------------ | :--------------- | :----------------- |
| status_code   | HTTP 状态码      | 期望: 200          |
| json_path     | JSONPath 取值    | 路径: $.data.token |
| response_time | 响应耗时         | 期望: < 1000ms     |
| header        | 响应头           | 头名: Content-Type |
| body_contains | 响应体包含文本   | 期望: "success"    |
| schema        | JSON Schema 校验 | Schema 定义        |

**断言结果结构**：

json

```
{
  "id": "assert_1",
  "type": "json_path",
  "path": "$.code",
  "operator": "equals",
  "passed": true,
  "expected": 0,
  "actual": 0,
  "message": "断言通过"
}
```



### 5.3 请求执行器

**设计目标**：统一请求执行入口，协调各引擎完成请求处理

**执行流程**：

text

```
┌─────────────────────────────────────────────────────────────┐
│                    请求执行流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 加载用例数据                                              │
│         │                                                   │
│         ▼                                                   │
│  2. 加载环境变量                                              │
│         │                                                   │
│         ▼                                                   │
│  3. 执行前置脚本（可选）                                       │
│         │                                                   │
│         ▼                                                   │
│  4. 变量替换（URL/Headers/Body）                              │
│         │                                                   │
│         ▼                                                   │
│  5. 发送 HTTP 请求                                            │
│         │                                                   │
│         ▼                                                   │
│  6. 执行断言                                                  │
│         │                                                   │
│         ▼                                                   │
│  7. 执行后置脚本/提取变量                                      │
│         │                                                   │
│         ▼                                                   │
│  8. 保存执行记录                                              │
│         │                                                   │
│         ▼                                                   │
│  9. 返回执行结果                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```



### 5.4 场景执行器

**设计目标**：按顺序执行多个用例，支持变量传递和失败处理

**执行策略**：

| 策略     | 说明                                       |
| :------- | :----------------------------------------- |
| 顺序执行 | 按 step_order 依次执行                     |
| 失败继续 | skip_on_failure = false 时，步骤失败仍继续 |
| 失败重试 | 支持配置重试次数和间隔                     |
| 变量隔离 | 每个场景独立的变量空间                     |

------

## 六、前端页面设计

### 6.1 页面结构

text

```
┌─────────────────────────────────────────────────────────────────┐
│                        顶部导航栏                                │
│  [Logo] API Debug Tool    [用例] [场景] [环境] [历史] [设置]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┬────────────────────────────────────────────┐  │
│  │              │                                            │  │
│  │   左侧边栏    │               主内容区                      │  │
│  │              │                                            │  │
│  │  ┌────────┐  │  ┌──────────────────────────────────────┐  │  │
│  │  │ 集合树  │  │  │           请求配置区                   │  │  │
│  │  │        │  │  │  ┌─────────────────────────────────┐ │  │  │
│  │  │ 📁 用户 │  │  │  │ GET ▼ [URL输入框]        [发送] │ │  │  │
│  │  │   ├ 登录│  │  │  └─────────────────────────────────┘ │  │  │
│  │  │   ├ 注册│  │  │  ┌─────────────────────────────────┐ │  │  │
│  │  │   └ 登出│  │  │  │ Headers │ Params │ Body │ Auth  │ │  │  │
│  │  │ 📁 订单 │  │  │  └─────────────────────────────────┘ │  │  │
│  │  │ 📁 商品 │  │  └──────────────────────────────────────┘  │  │
│  │  └────────┘  │                                            │  │
│  │              │  ┌──────────────────────────────────────┐  │  │
│  │  [+ 新建]    │  │           断言配置区                   │  │  │
│  │              │  │  [+ 添加断言]                         │  │  │
│  │              │  │  • 状态码 = 200                   [×] │  │  │
│  │              │  │  • JSONPath $.code = 0           [×] │  │  │
│  │              │  │  • 响应时间 < 1000ms              [×] │  │  │
│  │              │  └──────────────────────────────────────┘  │  │
│  │              │                                            │  │
│  │              │  ┌──────────────────────────────────────┐  │  │
│  │              │  │           响应展示区                   │  │  │
│  │              │  │  Status: 200 OK  │  Time: 156ms     │  │  │
│  │              │  │  Size: 1.2KB      │  [格式化] [复制]  │  │  │
│  │              │  │  ┌─────────────────────────────────┐ │  │  │
│  │              │  │  │ {                               │ │  │  │
│  │              │  │  │   "code": 0,                    │ │  │  │
│  │              │  │  │   "message": "success",         │ │  │  │
│  │              │  │  │   "data": {...}                 │ │  │  │
│  │              │  │  │ }                               │ │  │  │
│  │              │  │  └─────────────────────────────────┘ │  │  │
│  │              │  └──────────────────────────────────────┘  │  │
│  │              │                                            │  │
│  └──────────────┴────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```



### 6.2 页面功能说明

#### 6.2.1 用例管理页

| 功能区域   | 功能点          | 说明                        |
| :--------- | :-------------- | :-------------------------- |
| 左侧集合树 | 文件夹展开/折叠 | 树形展示用例组织结构        |
|            | 新建文件夹/用例 | 右键菜单或底部按钮          |
|            | 拖拽排序        | 支持用例在不同文件夹间移动  |
|            | 右键菜单        | 重命名、删除、导出          |
| 主内容区   | 用例列表        | 表格展示，支持排序、筛选    |
|            | 快速执行        | 列表项悬浮显示执行按钮      |
|            | 批量操作        | 批量删除、批量导出          |
| 请求配置区 | 方法选择器      | GET/POST/PUT/DELETE/PATCH   |
|            | URL 输入        | 支持变量提示和高亮          |
|            | 参数编辑        | Headers/Params/Body 标签页  |
|            | 认证配置        | Basic/Bearer/API Key        |
| 断言配置区 | 断言列表        | 展示已配置的断言规则        |
|            | 添加断言        | 弹窗选择断言类型            |
|            | 启用/禁用       | 开关控制断言是否生效        |
| 响应展示区 | 状态信息        | 状态码、耗时、大小          |
|            | 响应体          | JSON 格式化高亮             |
|            | 断言结果        | 展示每个断言的通过/失败状态 |

#### 6.2.2 场景编排页

| 功能区域   | 功能点    | 说明                   |
| :--------- | :-------- | :--------------------- |
| 场景列表   | 场景 CRUD | 新建、编辑、删除场景   |
| 步骤编排区 | 添加步骤  | 从用例库选择添加       |
|            | 步骤排序  | 拖拽调整执行顺序       |
|            | 步骤配置  | 设置提取规则、失败处理 |
| 执行控制   | 执行场景  | 运行整个场景           |
|            | 单步执行  | 调试时逐步执行         |
| 变量监控   | 变量面板  | 实时展示场景变量值     |
| 执行报告   | 步骤结果  | 每个步骤的执行状态     |
|            | 提取结果  | 展示提取的变量值       |

#### 6.2.3 环境管理页

| 功能区域 | 功能点     | 说明                  |
| :------- | :--------- | :-------------------- |
| 环境列表 | 环境 CRUD  | 新建、编辑、删除环境  |
|          | 设为默认   | 标记默认环境          |
| 变量编辑 | 键值对编辑 | 表格形式编辑变量      |
|          | 变量预览   | 实时预览替换效果      |
| 导入导出 | 导出环境   | JSON 格式导出         |
|          | 导入环境   | 支持 Postman 环境格式 |

#### 6.2.4 执行历史页

| 功能区域 | 功能点   | 说明                   |
| :------- | :------- | :--------------------- |
| 历史列表 | 分页表格 | 展示执行记录           |
|          | 筛选条件 | 按状态、时间、类型筛选 |
|          | 快速回放 | 一键重新执行           |
| 执行详情 | 请求快照 | 展示发送的请求内容     |
|          | 响应快照 | 展示收到的响应内容     |
|          | 断言详情 | 每个断言的执行结果     |
| 对比功能 | 历史对比 | 两次执行结果的差异对比 |

------

## 七、CLI 工具设计

### 7.1 命令行结构

text

```
api-debug
├── run <case_id|scenario_id>     # 执行单个用例或场景
├── list [cases|scenarios]         # 列出用例或场景
├── env [list|use|show]            # 环境管理
└── report                         # 报告生成

选项：
  --env, -e        指定环境 ID 或名称
  --var, -v        传递临时变量 (key=value 格式)
  --output, -o     输出格式 (json|junit|console)
  --verbose        详细输出模式
  --config         指定配置文件路径
```



### 7.2 命令示例

bash

```
# 执行单个用例，输出 JUnit 报告
api-debug run case 1 --env test --output junit > report.xml

# 执行场景，传递临时变量
api-debug run scenario 2 -e prod -v "user_id=12345" -v "trace_id=abc"

# 列出所有用例
api-debug list cases --format table

# 查看当前环境变量
api-debug env show test
```



### 7.3 JUnit 报告格式

xml

```
<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="API Debug Tool - Scenario: 用户登录流程" 
             tests="3" failures="0" errors="0" time="1.245">
    <testcase name="步骤1: 用户登录" 
              classname="api-debug.case" time="0.234">
      <system-out>状态码: 200, 响应时间: 234ms</system-out>
    </testcase>
    <testcase name="步骤2: 获取用户信息" 
              classname="api-debug.case" time="0.156"/>
    <testcase name="步骤3: 更新用户资料" 
              classname="api-debug.case" time="0.198"/>
  </testsuite>
</testsuites>
```



------

## 八、数据迁移方案

### 8.1 迁移流程

text

```
┌─────────────────────────────────────────────────────────────┐
│                    数据迁移流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 前端读取 LocalStorage 数据                               │
│         │                                                   │
│         ▼                                                   │
│  2. 用户点击「导出数据」按钮                                   │
│         │                                                   │
│         ▼                                                   │
│  3. 生成 JSON 文件并下载                                      │
│         │                                                   │
│         ▼                                                   │
│  4. 在新版界面点击「导入数据」                                 │
│         │                                                   │
│         ▼                                                   │
│  5. 上传 JSON 文件到后端                                      │
│         │                                                   │
│         ▼                                                   │
│  6. 后端解析并写入 SQLite                                     │
│         │                                                   │
│         ▼                                                   │
│  7. 返回导入结果，显示成功/失败统计                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```



### 8.2 数据映射关系

| LocalStorage Key | 目标表        | 转换说明                       |
| :--------------- | :------------ | :----------------------------- |
| collections      | test_case     | 解析集合结构，生成 folder_path |
| environments     | environment   | 直接映射                       |
| history          | execution_log | 仅导入最近 N 条                |
| settings         | 配置文件      | 部分保留                       |

------

## 九、项目结构

### 9.1 后端目录结构

text

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # ORM 模型
│   │   ├── __init__.py
│   │   ├── case.py
│   │   ├── environment.py
│   │   ├── scenario.py
│   │   └── execution_log.py
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── case.py
│   │   ├── environment.py
│   │   ├── scenario.py
│   │   └── execution.py
│   ├── routers/                # API 路由
│   │   ├── __init__.py
│   │   ├── cases.py
│   │   ├── environments.py
│   │   ├── scenarios.py
│   │   ├── logs.py
│   │   └── migrate.py
│   ├── services/               # 核心服务
│   │   ├── __init__.py
│   │   ├── variable_engine.py
│   │   ├── assertion_engine.py
│   │   ├── extract_engine.py
│   │   ├── script_engine.py
│   │   ├── request_executor.py
│   │   └── scenario_executor.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── jsonpath_helper.py
│       └── logger.py
├── data/                       # 数据目录
│   └── api_debug.db           # SQLite 数据库
├── logs/                       # 日志目录
├── requirements.txt
└── 启动脚本.bat
```



### 9.2 前端目录结构

text

```
frontend/
├── src/
│   ├── api/                    # API 调用封装
│   │   ├── case.js
│   │   ├── environment.js
│   │   ├── scenario.js
│   │   └── log.js
│   ├── components/             # 公共组件
│   │   ├── CollectionTree.vue
│   │   ├── RequestPanel.vue
│   │   ├── ResponsePanel.vue
│   │   ├── AssertionConfig.vue
│   │   ├── VariableEditor.vue
│   │   └── JsonViewer.vue
│   ├── views/                  # 页面组件
│   │   ├── CaseManagement.vue
│   │   ├── ScenarioEditor.vue
│   │   ├── EnvironmentManage.vue
│   │   ├── ExecutionHistory.vue
│   │   └── DataMigration.vue
│   ├── stores/                 # Pinia 状态
│   │   ├── case.js
│   │   ├── environment.js
│   │   └── app.js
│   ├── utils/                  # 工具函数
│   │   ├── request.js
│   │   ├── variableParser.js
│   │   └── formatter.js
│   ├── router/                 # 路由配置
│   └── App.vue
├── package.json
└── vite.config.js
```



### 9.3 CLI 目录结构

text

```
cli/
├── api_debug/
│   ├── __init__.py
│   ├── main.py                 # CLI 入口
│   ├── commands/               # 命令模块
│   │   ├── __init__.py
│   │   ├── run.py
│   │   ├── list.py
│   │   └── env.py
│   ├── client/                 # API 客户端
│   │   ├── __init__.py
│   │   └── api_client.py
│   ├── formatters/             # 输出格式化
│   │   ├── __init__.py
│   │   ├── console.py
│   │   ├── json.py
│   │   └── junit.py
│   └── config.py
├── setup.py
└── requirements.txt
```



------

## 十、里程碑与交付物

### 10.1 四周计划

| 周次       | 主题       | 核心交付物              | 验收标准                       |
| :--------- | :--------- | :---------------------- | :----------------------------- |
| **Week 1** | 数据持久化 | SQLite 集成 + 用例 CRUD | 数据可保存到数据库，刷新不丢失 |
| **Week 2** | 环境与断言 | 环境管理 + 断言引擎     | 环境切换变量生效，断言自动校验 |
| **Week 3** | 场景编排   | 场景 CRUD + 步骤编排    | 多用例串联执行，变量正确传递   |
| **Week 4** | CLI 与集成 | CLI 工具 + JUnit 报告   | 命令行可执行测试，输出标准报告 |

### 10.2 验收清单

| 序号 | 验收项             | 验收方式          |
| :--- | :----------------- | :---------------- |
| 1    | 用例 CRUD 功能完整 | 手动测试          |
| 2    | 文件夹树形组织正常 | 手动测试          |
| 3    | 环境变量替换正确   | 编写测试用例验证  |
| 4    | 断言功能准确       | 编写测试用例验证  |
| 5    | 场景编排功能正常   | 编写示例场景验证  |
| 6    | 变量提取与传递正确 | 场景执行验证      |
| 7    | CLI 可执行用例     | 命令行验证        |
| 8    | JUnit 报告格式正确 | CI 工具验证       |
| 9    | 历史数据可迁移     | 导入导出验证      |
| 10   | API 文档完整       | Swagger UI 可访问 |