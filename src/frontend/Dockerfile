# ==================== 构建阶段 ====================
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --legacy-peer-deps

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# ==================== 运行阶段 ====================
FROM nginx:1.25-alpine

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 创建非 root 用户
RUN addgroup -g 1000 neuralnote && \
    adduser -D -u 1000 -G neuralnote neuralnote && \
    chown -R neuralnote:neuralnote /usr/share/nginx/html && \
    chown -R neuralnote:neuralnote /var/cache/nginx && \
    chown -R neuralnote:neuralnote /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R neuralnote:neuralnote /var/run/nginx.pid

# 切换到非 root 用户
USER neuralnote

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

