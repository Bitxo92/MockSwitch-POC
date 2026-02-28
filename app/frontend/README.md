<h1 align="center">
  <img src="src/assets/tai_logo.png" alt="TAI Logo" width="500"/>
  <br/>
  <b>Plantilla Frontend</b>
</h1>
<h3 align="center">
  
</h3>

## 📝 Sobre este Repositorio

Este repositorio consiste en una plantilla lista para producción diseñada para acelerar el desarrollo de aplicaciones frontend con despliegues rápidos en **Vercel**.

### Características Principales

- **React 19** - Librería moderna para construir interfaces de usuario
- **TypeScript** - Tipado estático para mayor seguridad de código
- **Vite** - Herramienta de construcción rápida y eficiente
- **Tailwind CSS** - Framework de utilidades CSS para diseño rápido
- **shadcn/ui** - Componentes UI reutilizables y accesibles
- **React Router** - Enrutamiento dinámico y protegido
- **Autenticación Integrada** - Sistema de login y gestión de sesiones
- **Responsive Design** - Diseño completamente adaptable a todos los dispositivos
- **Vercel Ready** - Configurado y optimizado para desplegar en Vercel

### Estructura del Proyecto

```
src/
├── components/
│   ├── ui/               # Componentes shadcn/ui y personalizados
│   ├── login-form.tsx    # Componente de formulario de login
│   └── placeholder/      # Componentes de placeholder
├── pages/
│   ├── home/
│   │   └── page.tsx      # Página principal
│   └── login/
│       └── page.tsx      # Página de autenticación
├── contexts/
│   └── AuthContext.tsx   # Contexto global de autenticación
├── hooks/
│   └── use-mobile.ts     # Hook para detectar dispositivos móviles
├── lib/
│   └── utils.ts          # Funciones utilitarias compartidas
├── services/             # Servicios API y lógica de negocio
│   └── api.ts            # Llamadas HTTP a la API
├── assets/               # Imágenes y recursos estáticos
├── App.tsx               # Componente raíz de la aplicación
├── main.tsx              # Punto de entrada de React
├── index.css             # Estilos globales
└── App.css               # Estilos de la aplicación
```

## 🚀 Inicio Rápido

### Instalación

1. Instala las dependencias:

```bash
npm install
```

2. Inicia el servidor de desarrollo:

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

> [!NOTE]
> Credentiales para login:
>
> - usuario: `user`
> - contraseña: `user`

### Agregar Nuevos Componentes shadcn/ui

Para agregar componentes adicionales de la librería shadcn/ui:

```bash
npx shadcn-ui@latest add [nombre-componente]
```

**Ejemplos:**

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add form
```

Consulta el catálogo completo de componentes disponibles en [shadcn/ui Documentation](https://ui.shadcn.com/docs/components)

Los componentes se instalarán automáticamente en `src/components/ui/`

## 🎨 Personalizar Colores y Temas

Los colores están definidos como variables CSS y mapeados a utilidades de Tailwind en `src/index.css`. Puedes customizarlos de varias formas:

#### 1. Usar Clases Tailwind Directamente (Recomendado)

Una vez que modifiques las variables CSS, automáticamente tendrás disponibles las clases Tailwind correspondientes:

```tsx
// Usar directamente en componentes
<div className="bg-primary text-primary-foreground">Fondo primario</div>
<button className="bg-secondary hover:bg-secondary/80">Botón secundario</button>
<div className="border border-border">Con borde</div>
<div className="text-accent">Texto con color de acento</div>
```

**Ejemplo completo de componente:**

```tsx
export function CardExample() {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <h2 className="text-foreground font-bold">Título</h2>
      <p className="text-muted-foreground">Descripción con color atenuado</p>
      <button className="bg-primary text-primary-foreground hover:opacity-90 px-4 py-2 rounded">
        Botón primario
      </button>
    </div>
  );
}
```

**Clases disponibles:**

- Background: `bg-primary`, `bg-secondary`, `bg-accent`, `bg-destructive`, `bg-card`, `bg-popover`
- Text: `text-primary`, `text-secondary`, `text-foreground`, `text-muted-foreground`
- Border: `border-border`, `border-input`, `border-ring`
- Sidebar: `bg-sidebar`, `text-sidebar-foreground`, `bg-sidebar-primary`

#### 2. Modificar Variables CSS Raíz

Abre `src/index.css` y modifica los valores en formato OKLCH. Por ejemplo, para cambiar el color primario a azul:

```css
:root {
  --primary: oklch(0.5 0.2 240); /* Azul */
  --secondary: oklch(0.7 0.15 180); /* Cian */
  --accent: oklch(0.6 0.18 300); /* Púrpura */
}

.dark {
  --primary: oklch(0.7 0.2 240); /* Azul más claro */
  --secondary: oklch(0.6 0.15 180);
  --accent: oklch(0.5 0.18 300);
}
```

Ahora todos tus botones y elementos con `bg-primary` mostrarán azul automáticamente.

#### 3. Crear Nuevas Variables CSS

Agrega tus propias variables en `:root` y en `.dark`:

```css
:root {
  /* Variables de shadcn existentes */
  --primary: oklch(0.205 0 0);

  /* Tus variables personalizadas */
  --warning: oklch(0.65 0.2 41); /* Naranja/Amarillo */
  --success: oklch(0.6 0.15 142); /* Verde */
  --info: oklch(0.55 0.2 240); /* Azul info */
  --error: oklch(0.6 0.25 20); /* Rojo error */
}

.dark {
  --warning: oklch(0.75 0.15 41);
  --success: oklch(0.7 0.12 142);
  --info: oklch(0.65 0.2 240);
  --error: oklch(0.7 0.2 20);
}
```

Luego mapea en `@theme` para crear clases Tailwind:

```css
@theme inline {
  --color-warning: var(--warning);
  --color-success: var(--success);
  --color-info: var(--info);
  --color-error: var(--error);
}
```

**Ahora puedes usar en tus componentes:**

```tsx
<div className="bg-warning text-black">Advertencia</div>
<div className="bg-success text-white">Éxito</div>
<div className="bg-info text-white">Información</div>
<div className="bg-error text-white">Error</div>

// En botones
<button className="bg-success hover:bg-success/90">Guardar</button>
<button className="bg-error hover:bg-error/90">Eliminar</button>
```

> [!TIP]
> Los colores en `index.css` están en formato OKLCH. Para convertir de colores que tienes en mente o HSL a OKLCH, usa [oklch.com](https://oklch.com) o herramientas similares.

### Construir para Producción

```bash
npm run build
```

El resultado se generará en la carpeta `dist/`
