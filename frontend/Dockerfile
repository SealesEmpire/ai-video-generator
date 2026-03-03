# ---------- Stage 1: Build ----------
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json ./
# --legacy-peer-deps is needed because react-scripts 5 declares peer deps
# that conflict with React 19; this is safe for CRA-based projects.
RUN npm install --legacy-peer-deps

COPY . .

# Build-time env var – override at docker build or compose
ARG REACT_APP_BACKEND_URL=http://localhost:8001
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN npm run build

# ---------- Stage 2: Serve ----------
FROM nginx:1.25-alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
