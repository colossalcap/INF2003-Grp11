# ═══════════════════════════════════════════════════════════
# Stage 1: Install dependencies (cached unless package.json changes)
# ═══════════════════════════════════════════════════════════
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json ./
RUN npm install

# ═══════════════════════════════════════════════════════════
# Stage 2: Runtime (with pre-installed node_modules + source)
# ═══════════════════════════════════════════════════════════
FROM node:20-alpine

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
