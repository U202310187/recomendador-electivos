# Guía rápida de inicio (Flask + Neo4j + Docker)

Esta guía está hecha para levantar el proyecto paso a paso.

---

## ✅ 0. Antes de empezar
Asegúrate de tener instalado en tu computadora:

- **Docker Desktop**
- **Git**

> No es necesario instalar Python ni Neo4j manualmente.

---

## ✅ 1. Abrir PowerShell en modo normal (NO como administrador)

1. Presiona **Windows + S**
2. Escribe: `PowerShell`
3. Ábrelo (sin "Ejecutar como administrador").

> Usaremos PowerShell porque funciona igual para todos.

---

## ✅ 2. Clonar el repositorio
Ejecuta en **PowerShell**:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd <nombre-del-repo>
```

Ejemplo:
```powershell
git clone https://github.com/usuario/flask_graph_app.git
cd flask_graph_app
```

---

## ✅ 3. Crear tu archivo `.env`
Esto se hace **dentro de la carpeta del proyecto**, en **PowerShell**:

### Windows (PowerShell / CMD):
```powershell
copy .env.example .env
```

Luego abre VS Code para editarlo:
```powershell
code .
```

Dentro de `.env` cambia la contraseña:
```
NEO4J_PASS=CAMBIAR_ESTA_CONTRASEÑA
```

> **No** se sube `.env` al repositorio.

---

## ✅ 4. Levantar los contenedores (iniciar la app y Neo4j)
Ejecutar en **PowerShell en la carpeta del proyecto**:

```powershell
docker compose up -d
```

Cuando termine, verificas que todo se haya ejecutado correctamente:
- API: http://localhost:5000/health

- Neo4j Browser: http://localhost:7474

Usuario: `neo4j`  
Contraseña: la que está en `.env`

---

## ✅ 5. Restaurar la base de datos (SOLO LO HACES UNA VEZ)

### Paso 5.1 — Detener el contenedor de Neo4j
Ejecutar en **PowerShell dentro del proyecto**:
```powershell
docker compose stop neo4j
```

### Paso 5.2 — Ejecutar la restauración (COPIAR Y PEGAR TAL CUAL)
Ejecutar en **PowerShell dentro del proyecto**:

```powershell
docker run --rm -v app_neo4j_data:/data -v ${PWD}/db_seed:/seed $(docker inspect -f "{{.Config.Image}}" app_graph_db) neo4j-admin database restore --from-path=/seed neo4j --overwrite-destination=true
```

### Paso 5.3 — Volver a iniciar Neo4j
```powershell
docker compose up -d
```

Listo ✅ Ya tienes la misma base de datos que el resto del equipo.

---

## ✅ 6. Comandos útiles del día a día

```powershell
# Ver contenedores corriendo
docker compose ps

# Parar contenedores (sin borrarlos)
docker compose stop

# Volver a levantarlos
docker compose up -d
```

---

## ✅ 7. Flujo de trabajo para colaborar

```powershell
# Crear una nueva rama para una tarea
git checkout -b feature/nueva-funcion

# Guardar cambios
git add .
git commit -m "feat: agrego nueva funcionalidad"

# Subir la rama
git push -u origin feature/nueva-funcion
```

---

## 🎉 ¡Listo!
Si seguiste estos pasos, ya estás trabajando con:
- El backend funcionando
- Neo4j con la base de datos inicial
- Un entorno idéntico al del resto del equipo