FROM node:22-alpine AS dependencies
WORKDIR /app
RUN npm install --global pnpm@9.15.0
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend/package.json frontend/package.json
RUN pnpm install --frozen-lockfile --ignore-scripts=false

FROM node:22-alpine AS builder
WORKDIR /app
RUN corepack enable
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/frontend/node_modules ./frontend/node_modules
COPY frontend ./frontend
WORKDIR /app/frontend
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN mkdir -p public
RUN npx --yes pnpm@9.15.0 build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/frontend/public ./frontend/public
COPY --from=builder /app/frontend/.next/standalone ./frontend
COPY --from=builder /app/node_modules/.pnpm ./node_modules/.pnpm
COPY --from=builder /app/frontend/.next/static ./frontend/.next/static
# The standalone tree is relocated under /app/frontend, while pnpm's package
# store is copied separately so the runtime links resolve after relocation.
RUN rm frontend/node_modules/next frontend/node_modules/react \
    && ln -s /app/node_modules/.pnpm/next@*/node_modules/next frontend/node_modules/next \
    && ln -s /app/node_modules/.pnpm/react@*/node_modules/react frontend/node_modules/react
WORKDIR /app/frontend
EXPOSE 3000
CMD ["node", "server.js"]
