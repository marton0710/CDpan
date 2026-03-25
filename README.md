# CDPan

一个基于 `FastAPI + SQLite + Vue 3 + Element Plus` 的 PDF 管理平台，支持：

- 用户注册、登录和 JWT 鉴权
- PDF 上传、下载、删除、验签
- 文件哈希、数字签名、追踪记录
- 文件版本识别与安全等级展示
- 前端工作台、搜索和分页

## 项目结构

```text
.
├─ app/              # 后端业务代码、模型、服务、工具
├─ CDPan/            # Vue 前端
├─ main.py           # FastAPI 入口
├─ requirements.txt  # Python 依赖
└─ Smart_Signing_Guardian.db  # 运行后自动生成的 SQLite 数据库
```

## 环境要求

- Python 3.10+
- Node.js 18+
- npm

## 后端启动

1. 创建并激活虚拟环境

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 启动后端

```bash
python main.py
```

默认会启动在：

```text
http://127.0.0.1:80
```

后端首次启动时会自动：

- 创建 SQLite 数据库 `Smart_Signing_Guardian.db`
- 执行表初始化和必要的数据库迁移
- 创建文件存储目录和签名密钥目录

## 前端启动

1. 进入前端目录

```bash
cd CDPan
```

2. 安装依赖

```bash
npm install
```

3. 启动开发环境

```bash
npm run dev
```

默认开发地址通常为：

```text
http://127.0.0.1:5173
```

## 前端接口配置

前端默认请求同域 `/api`。

开发环境下如果前后端分开启动，可以在 `CDPan/.env` 中写：

```env
VITE_API_BASE_URL=/api
VITE_PROXY_TARGET=http://127.0.0.1:80
```

示例文件见 [CDPan/.env.example](/D:/ComputerDesign/CDPan/.env.example)。

## 前端构建

```bash
cd CDPan
npm run build
```

构建产物位于：

```text
CDPan/dist
```

## 主要功能

- 用户注册 / 登录
- PDF 上传与下载
- 文件二进制哈希校验
- 基于用户身份的数字签名
- 文件追踪记录
- 同版本重复上传识别
- 文件版本链追踪
- 安全等级展示
- 按归属账号区分文件
- 文件搜索与分页

## 说明

- 后端当前使用 SQLite，适合开发和中小规模部署。
- 前端依赖由 [CDPan/package.json](/D:/ComputerDesign/CDPan/package.json) 管理，不在 `requirements.txt` 中。
- 文件内容和用户密钥目录会在运行时自动创建，不需要手动预建。
