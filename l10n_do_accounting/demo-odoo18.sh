#!/bin/bash
# ========================================
# DEMO RÁPIDA ODOO 18 - l10n_do_accounting
# ========================================
echo "🚀 Iniciando entorno de prueba Odoo 18..."

# 1. Crear estructura de directorios
mkdir -p ./odoo-demo/postgresql
mkdir -p ./odoo-demo/addons
mkdir -p ./odoo-demo/data

# 2. Copiar el módulo migrado
echo "📦 Copiando módulo l10n_do_accounting..."
cp -r ~/l10n-dominicana/l10n_do_accounting ./odoo-demo/addons/

# 3. Crear docker-compose.yml
echo "🐳 Configurando Docker Compose..."
cat > ./odoo-demo/docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - ./postgresql:/var/lib/postgresql/data
    restart: unless-stopped

  odoo:
    image: odoo:18.0
    depends_on:
      - postgres
    ports:
      - "18069:8069"
    environment:
      - HOST=postgres
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - ./addons:/mnt/extra-addons
      - ./data:/var/lib/odoo
    restart: unless-stopped
    command: >
      odoo
      --dev xml
      --database odoo_demo_db
      --init l10n_do,l10n_do_accounting
      --without-demo=all
      --stop-after-init
      && odoo
EOF

# 4. Iniciar los contenedores
echo "🔧 Iniciando Odoo 18 y PostgreSQL..."
cd ./odoo-demo
docker-compose down 2>/dev/null
docker-compose up -d

# 5. Esperar a que Odoo esté listo
echo "⏳ Esperando que Odoo esté listo (esto puede tomar 40-60 segundos)..."
sleep 45

# 6. Mostrar información de acceso
echo ""
echo "========================================="
echo "✅ ENTORNO DE PRUEBA ODOO 18 LISTO"
echo "========================================="
echo "🌐 URL de acceso: http://localhost:18069"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: admin"
echo "📋 Base de datos: odoo_demo_db"
echo ""
echo "⚙️  Para detener el entorno ejecuta:"
echo "    cd odoo-demo && docker-compose down"
echo "========================================="
