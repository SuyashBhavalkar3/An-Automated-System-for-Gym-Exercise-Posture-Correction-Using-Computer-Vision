# Frontend - Multi-stage build for Vite React app
# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* package-lock.json* yarn.lock* ./

# Install dependencies
RUN npm install || npm ci || true

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production server with Nginx
FROM nginx:alpine

# Copy built application from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
