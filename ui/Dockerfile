FROM node:18-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* ./

RUN \
  if [ -f package-lock.json ]; then npm ci; \
  else echo "Lockfile not found." && exit 1; \
  fi

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
