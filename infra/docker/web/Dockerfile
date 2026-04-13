FROM node:22-alpine

WORKDIR /workspace
ENV PNPM_HOME=/pnpm/home
ENV PNPM_STORE_DIR=/pnpm/store
ENV PATH=$PNPM_HOME:$PATH

RUN apk add --no-cache libc6-compat && corepack enable
RUN mkdir -p /pnpm/home /pnpm/store

CMD ["sh", "/workspace/infra/docker/web/entrypoint.sh"]
