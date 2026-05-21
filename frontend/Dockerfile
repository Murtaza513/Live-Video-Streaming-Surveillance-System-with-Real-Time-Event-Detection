# ── Stage 1: build React app ─────────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first for layer caching
COPY package.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# ── Stage 2: serve with Nginx ────────────────────────────────────────────────
FROM nginx:stable-alpine AS final

# Replace default config with our SPA-aware config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
