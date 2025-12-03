# Frontend - Sistema de Seguridad IoT

Frontend del sistema de seguridad IoT desarrollado con React + TypeScript + Vite.

## 🚀 Tecnologías

- **React 18.2** - Librería UI
- **TypeScript 5.2** - Tipado estático
- **Vite 5.0** - Build tool
- **React Router 6.20** - Navegación
- **TanStack Query 5.8** - Data fetching y caché
- **Zustand 4.4** - State management
- **Axios 1.6** - HTTP client
- **Tailwind CSS 3.3** - Estilos
- **Recharts 2.10** - Gráficos
- **React Hot Toast** - Notificaciones

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/        # Componentes reutilizables
│   │   ├── ui/           # Componentes UI base
│   │   └── Layout.tsx    # Layout principal
│   ├── pages/            # Páginas de la aplicación
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Zones.tsx
│   │   ├── Devices.tsx
│   │   ├── Events.tsx
│   │   ├── Evidences.tsx
│   │   └── Measurements.tsx
│   ├── services/         # Clientes API
│   │   ├── api.ts       # Axios instance
│   │   ├── authService.ts
│   │   ├── zonesService.ts
│   │   ├── devicesService.ts
│   │   ├── eventsService.ts
│   │   ├── evidencesService.ts
│   │   └── measurementsService.ts
│   ├── stores/           # Estado global (Zustand)
│   │   └── authStore.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Componente raíz
│   ├── main.tsx          # Entry point
│   └── index.css         # Estilos globales
├── public/               # Assets estáticos
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🛠️ Instalación

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
VITE_API_URL=http://localhost:5000/api
```

### Configuración de API

El archivo `src/services/api.ts` contiene la configuración de Axios con:
- Base URL desde variables de entorno
- Interceptor de request para JWT
- Interceptor de response para manejo de errores y refresh token

## 📱 Características

### Autenticación
- Login con email y contraseña
- Registro de nuevos usuarios
- JWT con refresh token automático
- Persistencia de sesión en localStorage

### Dashboard
- Resumen de estadísticas del sistema
- Eventos recientes
- Estado de zonas
- Dispositivos activos

### Gestión de Zonas
- CRUD completo de zonas
- Asignación de dispositivos
- Configuración personalizada

### Gestión de Dispositivos
- CRUD completo de dispositivos
- Comandos MQTT (ON/OFF)
- Filtros por zona y tipo
- Estado en tiempo real

### Monitoreo de Eventos
- Timeline de eventos
- Filtros por dispositivo y tipo
- Metadata detallada
- Timestamps relativos

### Evidencias de Seguridad
- Galería de imágenes
- Análisis de IA integrado
- Detección de personas
- Descarga de imágenes

### Telemetría
- Gráficos de temperatura y humedad
- Comparación por dispositivo
- Rangos de tiempo personalizables
- Estadísticas en tiempo real

## 🎨 Componentes UI

### Componentes Base
- `Button` - Botones con variantes (primary, secondary, danger, success, ghost)
- `Card` - Contenedor con título opcional
- `Modal` - Ventana modal con tamaños configurables
- `Input` - Input con label y errores
- `Badge` - Etiquetas de estado
- `Loading` - Indicador de carga
- `Table` - Tabla con tipos genéricos

### Layout
- Sidebar responsivo con navegación
- Header con información de usuario
- Menu desplegable de perfil
- Indicador de página actual

## 🔐 Rutas

### Públicas
- `/login` - Inicio de sesión
- `/register` - Registro de usuarios

### Privadas (requieren autenticación)
- `/dashboard` - Dashboard principal
- `/zones` - Gestión de zonas
- `/devices` - Gestión de dispositivos
- `/events` - Historial de eventos
- `/evidences` - Evidencias de seguridad
- `/measurements` - Telemetría

## 📊 Estado Global

### Auth Store (Zustand)
```typescript
{
  user: User | null,
  accessToken: string | null,
  refreshToken: string | null,
  isAuthenticated: boolean,
  setAuth: (user, accessToken, refreshToken) => void,
  logout: () => void
}
```

Persistido en localStorage con middleware `persist`.

## 🌐 Integración con Backend

### Endpoints API

- **Auth**: `/auth/login`, `/auth/register`, `/auth/me`, `/auth/refresh`
- **Zones**: `/zones` (GET, POST), `/zones/:id` (GET, PUT, DELETE)
- **Devices**: `/devices` (GET, POST), `/devices/:id` (GET, PUT, DELETE), `/devices/:id/command`
- **Device Types**: `/device-types`
- **Events**: `/events`, `/events/:id`, `/events/stats`
- **Evidences**: `/evidences`, `/evidences/:id/ai`
- **Measurements**: `/measurements`, `/measurements/device/:id`, `/measurements/latest`, `/measurements/summary`

### Autenticación JWT

Todas las rutas privadas incluyen automáticamente el header:
```
Authorization: Bearer <access_token>
```

Si el token expira (401), se realiza refresh automático y se reintenta la petición.

## 🚢 Despliegue con Docker

El frontend está configurado para ejecutarse en contenedor Docker con Nginx:

```dockerfile
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📝 Notas de Desarrollo

- Todos los errores de lint son esperados hasta ejecutar `npm install`
- Los tipos TypeScript están completos para todas las entidades
- React Query gestiona el caché y revalidación automática
- Tailwind CSS proporciona estilos utility-first
- Los gráficos Recharts son responsivos y personalizables

## 🔄 Próximos Pasos

- [ ] Agregar tests unitarios (Vitest)
- [ ] Agregar tests E2E (Playwright)
- [ ] Implementar WebSocket para updates en tiempo real
- [ ] Agregar soporte para PWA
- [ ] Implementar modo oscuro
- [ ] Agregar i18n para múltiples idiomas
