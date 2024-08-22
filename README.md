# StockMonitor

## 项目概述

StockMonitor 是一个用于实时监控股票市场的微服务系统。该系统允许用户订阅股票代码，并在股票市场发生重要变动时收到通知。系统通过多个微服务协同工作，从公开 API 获取数据，进行数据清洗和分析，并通过消息队列通知用户。

## 功能描述

### 用户管理服务（User Management）
- 用户可以订阅或取消订阅股票代码。
- 处理用户的订阅请求，并将订阅信息发送给股票数据获取服务。
- 提供 API 接口，供前端应用与用户管理服务进行交互。

### 股票数据获取服务（Stock Fetcher）
- 定时从公开 API 获取订阅股票的最新数据。
- 根据市场状态判断是否继续获取数据，并将数据发送到股票数据处理服务。
- 接收市场状态的更新，并根据状态调整数据获取逻辑。

### 股票数据处理服务（Stock Processor）
- 对从数据获取服务接收到的股票数据进行清洗和解析。
- 基于清洗后的数据执行预定义的策略，判断是否需要触发通知。
- 将市场状态发送回股票数据获取服务，以控制数据获取流程。

### 通知服务（Notification）
- 接收来自股票数据处理服务的通知请求，并将通知发送给用户。
- 可以使用不同的通知方式，如短信、电子邮件或推送通知。

### 管理监控服务（Admin Monitoring）
- 提供系统状态监控功能，确保各微服务正常运行。
- 提供接口供管理员查询和管理系统状态。

## 系统架构

StockMonitor 系统由多个微服务构成，每个微服务通过 RabbitMQ 消息队列进行通信。各微服务通过 Docker 容器进行部署，确保系统的高可用性和可扩展性。

## 运行环境

### 必要条件
- Docker
- Docker Compose
- Python 3.12
- RabbitMQ
- MySQL
- Redis

### 环境变量
系统通过 `.env` 文件管理环境变量。以下是常用的环境变量：
- `DATABASE_URL`: 数据库连接字符串
- `REDIS_URL`: Redis 连接字符串
- `RABBITMQ_URL`: RabbitMQ 连接字符串
- `API_STOCK_INFO`: 股票信息的 API URL
- `LOG_LEVEL`: 日志级别（可选值：DEBUG, INFO, WARNING, ERROR）

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/GalenBlabla/StockMonitor.git
cd StockMonitor
```
### 2.进入 docker 目录并启动服务
```bash
cd docker
docker-compose up -d --build
```
### 3. 访问服务
服务启动后，可以通过以下方式访问各微服务：

- 用户管理服务：http://localhost:8000
- 股票数据获取服务：内部通信，无需直接访问
- 股票数据处理服务：内部通信，无需直接访问
- 通知服务：内部通信，无需直接访问
- 管理监控服务：待实现

### 目录结构
- `user_management`: 用户管理服务
- `stock_fetcher`: 股票数据获取服务
- `stock_processor`: 股票数据处理服务
- `notification`: 通知服务
- `admin_monitoring`: 管理监控服务
- `docker`: Docker 和 Docker Compose 配置文件
- `logs`: 日志目录

### 贡献指南
欢迎贡献代码！请确保所有更改都符合项目的代码风格，并且在提交之前通过了所有测试。

### 许可证
本项目遵循 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
