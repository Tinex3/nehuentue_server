# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copiar package.json e instalar dependencias
COPY package*.json ./
RUN npm ci

# Copiar código fuente y compilar
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos compilados
COPY --from=build /app/dist /usr/share/nginx/html

# Puerto
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
