import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from neo4j import GraphDatabase, basic_auth
# (No importamos bcrypt porque tu login es simulado y no lo necesitamos)

# --- Configuración y Conexión (Tu código) ---
uri = "bolt://neo4j:7687"
user = "neo4j"
password = "Admin1234!"  # (Tu contraseña de .env)
driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
swagger = Swagger(app, template={
    "info": {"title": "Recomendador de Electivos API", "version": "1.0"}
})

def run_query(cypher, **params):
    """ Función helper para ejecutar consultas """
    try:
        with driver.session() as session:
            res = session.run(cypher, **params)
            return [r.data() for r in res]
    except Exception as e:
        # Devolvemos un error que Flask pueda entender
        app.logger.error(f"Error en consulta Cypher: {e}")
        return {"error": str(e)}

# --- Endpoints del Sistema ---

@app.get("/health")
def health():
    """ Health check """
    try:
        run_query("RETURN 1 AS ok")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/stats")
def stats():
    """ Estadísticas generales """
    q = """
    CALL { MATCH (c:Curso) RETURN count(c) AS cursos }
    CALL { MATCH (t:Tema) RETURN count(t) AS temas }
    CALL { MATCH (m:Mencion) RETURN count(m) AS menciones }
    CALL { MATCH (a:Alumno) RETURN count(a) AS alumnos }
    CALL { MATCH ()-[r]->() RETURN count(r) AS relaciones }
    RETURN cursos, temas, menciones, alumnos, relaciones
    """
    return jsonify(run_query(q)[0])

# --- Endpoints de Cursos, Temas, Menciones (CORREGIDOS) ---
# Nota: Eliminamos el get_cursos() duplicado

@app.get("/cursos")
def get_cursos():
    """ Lista de cursos (CORREGIDO: sin .*) """
    limit = request.args.get("limit", default=1000, type=int)
    tipo = request.args.get("tipo", default=None, type=str)
    mencion = request.args.get("mencion", default=None, type=str)

    q = "MATCH (c:Curso) "
    params = {"limit": limit}

    if tipo:
        q += "WHERE c.tipo_curso = $tipo "
        params["tipo"] = tipo
    if mencion:
        q += "{} (c)-[:TIENE_MENCION]->(:Mencion {{nombre: $mencion}}) ".format("AND" if tipo else "WHERE")
        params["mencion"] = mencion

    q += """
    OPTIONAL MATCH (c)-[:TIENE_MENCION]->(m:Mencion)
    RETURN c{
        .id, .nombre, .tipo_curso, .ciclo_tipo_curso, 
        .descripcion, mencion: m.nombre, labels: labels(c)
    } AS curso
    ORDER BY curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, **params))

@app.get("/cursos/<id_curso>")
def get_curso(id_curso):
    """ Detalle de curso (CORREGIDO: sin .*) """
    q = """
    MATCH (c:Curso {id:$id})
    OPTIONAL MATCH (c)-[:TIENE_MENCION]->(m:Mencion)
    RETURN c{
        .id, .nombre, .tipo_curso, .ciclo_tipo_curso, 
        .descripcion, mencion: m.nombre, labels: labels(c)
    } AS curso
    """
    data = run_query(q, id=id_curso)
    return (jsonify(data[0]) if data else (jsonify({"error":"No encontrado"}), 404))

@app.get("/cursos/<id_curso>/relaciones")
def get_relaciones_de_curso(id_curso):
    """ Relaciones de un curso (CORREGIDO: solo a otros Cursos) """
    q = """
    MATCH (c:Curso {id:$id})-[r]->(n:Curso)
    RETURN type(r) AS relNeo4j, r.type AS relCSV, 
           n{ .id, .nombre, labels: labels(n) } AS vecino, 
           startNode(r).id AS from, endNode(r).id AS to
    """
    return jsonify(run_query(q, id=id_curso))

@app.get("/cursos/<id_curso>/temas")
def get_temas_de_curso(id_curso):
    """ Temas de un curso (CORREGIDO: sin .*) """
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (c:Curso {id:$id})-[r:REL]->(t:Tema)
    WHERE r.type = $rel
    RETURN t{.id, .nombre, .family} AS tema, r{.type} AS relacion
    ORDER BY t.nombre
    """
    return jsonify(run_query(q, id=id_curso, rel=rel_type))

@app.get("/temas")
def get_temas():
    """ Lista de temas (CORREGIDO: sin .*) """
    q = """
    MATCH (t:Tema)
    RETURN t{.id, .nombre, .family} AS tema
    ORDER BY t.nombre
    """
    return jsonify(run_query(q))

@app.get("/menciones")
def get_menciones():
    """ Lista de menciones (CORREGIDO: sin .*) """
    q = """
    MATCH (m:Mencion)
    RETURN m{.id, .nombre} AS mencion
    ORDER BY m.nombre
    """
    return jsonify(run_query(q))

@app.get("/menciones/<nombre>/cursos")
def get_cursos_por_mencion(nombre):
    """ Cursos asociados a una mención (CORREGIDO: sin .*) """
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (m:Mencion {nombre:$nom})<-[r:REL]-(c:Curso)
    WHERE r.type = $rel
    RETURN c{.id, .nombre, .tipo_curso} AS curso
    ORDER BY c.nombre
    """
    return jsonify(run_query(q, nom=nombre, rel=rel_type))

# --- Endpoints de Alumnos (CORREGIDOS) ---

@app.get("/alumnos")
def get_alumnos():
    """ Lista de alumnos (CORREGIDO: sin .*) """
    q_search = request.args.get("q", default="", type=str)
    limit = request.args.get("limit", default=100, type=int)
    page = request.args.get("page", default=1, type=int)
    skip = (page - 1) * limit

    q = """
    MATCH (a:Alumno)
    WHERE a.nombre CONTAINS $q_search OR a.id CONTAINS $q_search
    RETURN a{ 
        .id, .nombre, .carrera, .ciclo_alumno, .ciclo_completado 
    } AS alumno
    SKIP $skip
    LIMIT $limit
    """
    return jsonify(run_query(q, q_search=q_search, skip=skip, limit=limit))

@app.get("/alumnos/<id_alumno>")
def get_alumno(id_alumno):
    """ Detalle de alumno (CORREGIDO: sin .*) """
    q = """
    MATCH (a:Alumno {id:$id})
    RETURN a{ 
        .id, .nombre, .carrera, .ciclo_alumno, .ciclo_completado 
    } AS alumno
    """
    data = run_query(q, id=id_alumno)
    return (jsonify(data[0]) if data else (jsonify({"error":"No encontrado"}), 404))

# ---
# NUEVO ENDPOINT (GET /alumnos/<id>/cursos)
# Este endpoint FALTABA y es necesario para el Dashboard
# ---
@app.get("/alumnos/<id_alumno>/cursos")
def get_cursos_de_alumno(id_alumno):
    """
    Cursos en los que un alumno está inscrito (p.ej. APROBADO)
    """
    rel_type = request.args.get("rel_type", "APROBADO")
    q = """
    MATCH (a:Alumno {id:$id})-[r]->(c:Curso)
    WHERE type(r) = $rel_type
    RETURN c{ .id, .nombre } AS curso, r{ .nota, .w_mastery } AS relacion
    ORDER BY c.nombre
    """
    return jsonify(run_query(q, id=id_alumno, rel_type=rel_type))

@app.post("/alumnos/<id_alumno>/cursos")
def add_curso_a_alumno(id_alumno):
    """ Inscribe a un alumno en un curso (Aprobado) (CORREGIDO: sin duplicados) """
    data = request.get_json()
    id_curso = data.get('id_curso')
    nota = data.get('nota', 13)
    ciclo_tomado = data.get('ciclo_tomado', 2025)

    if not id_curso:
        return jsonify({"error": "Falta id_curso"}), 400

    # Fórmula de fortaleza del informe
    w_mastery = ((max(0, min(nota - 13, 7))) / 7) ** 2

    q_create = """
    MATCH (a:Alumno {id: $id_alumno})
    MATCH (c:Curso {id: $id_curso})
    MERGE (a)-[r:APROBADO]->(c)
    SET r.nota = $nota, r.w_mastery = $w_mastery, r.ciclo_tomado = $ciclo_tomado
    RETURN a.nombre AS alumno, c.nombre AS curso, r.nota AS nota
    """
    try:
        result = run_query(q_create, 
                           id_alumno=id_alumno, id_curso=id_curso, 
                           nota=nota, w_mastery=w_mastery, ciclo_tomado=ciclo_tomado)
        if not result:
            return jsonify({"error": "No se pudo crear la relación. Revisa los IDs."}), 404
        return jsonify(result[0]), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/alumnos/<id_alumno>/temas")
def get_temas_de_alumno(id_alumno):
    """ Temas alcanzados por un alumno (CORREGIDO: sin .*) """
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(c:Curso)
    WHERE r1.type = $rel
    MATCH (c)-[r2:REL]->(t:Tema)
    WHERE r2.type = $rel
    WITH DISTINCT t
    ORDER BY t.nombre
    RETURN t{.id, .nombre, .family} AS tema
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type))

# --- Endpoints de Grafo y Recomendador (CORREGIDOS) ---
# Nota: Eliminamos las rutas duplicadas de recomendación

@app.get("/grafo")
def grafo():
    """ Grafo simplificado para visualización """
    limit = int(request.args.get("limit", 200))
    q = """
    MATCH (a)-[r]->(b)
    WITH a, r, b LIMIT $limit
    RETURN
      collect(DISTINCT a{.id, .nombre, labels:labels(a)}) AS sourceNodes,
      collect(DISTINCT b{.id, .nombre, labels:labels(b)}) AS targetNodes,
      collect({from:startNode(r).id, to:endNode(r).id, rel:type(r), relCSV:r.type}) AS rels
    """
    rows = run_query(q, limit=limit)[0]
    seen, nodes = set(), []
    for n in rows["sourceNodes"] + rows["targetNodes"]:
        if n["id"] not in seen:
            seen.add(n["id"])
            nodes.append(n)
    return jsonify({"nodes": nodes, "edges": rows["rels"]})

@app.get("/alumnos/<id_alumno>/grafo")
def grafo_alumno(id_alumno):
    """ Subgrafo del alumno """
    rel_type = request.args.get("rel_type", "Directed")
    limit = int(request.args.get("limit", 300))
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(n1)
    WHERE r1.type = $rel
    WITH a, r1, n1
    LIMIT $limit
    OPTIONAL MATCH (n1)-[r2:REL]->(n2)
    WHERE r2.type = $rel
    WITH a,
      collect(DISTINCT r1) + collect(DISTINCT r2) AS rels,
      collect(DISTINCT n1) + collect(DISTINCT n2) AS allNodes
    UNWIND allNodes AS n
    WITH collect(DISTINCT n) AS nodes, rels
    RETURN
      [x IN nodes | x{.id, .nombre, labels:labels(x)}] AS nodes,
      [r IN rels  | {from:startNode(r).id, to:endNode(r).id, rel:type(r), relCSV:r.type}] AS edges
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type, limit=limit))

@app.get("/alumnos/<id_alumno>/recomendaciones")
def recomendar_cursos(id_alumno):
    """ Recomendación simple (CORREGIDO: sin .*) """
    rel_type = request.args.get("rel_type", "Directed")
    limit = int(request.args.get("limit", 10))
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(c:Curso)
    WHERE r1.type = $rel
    WITH a, collect(DISTINCT c) AS cursosAlumno
    MATCH (c1:Curso)-[rc:REL]->(t:Tema)
    WHERE rc.type = $rel AND c1 IN cursosAlumno
    WITH a, cursosAlumno, collect(DISTINCT t) AS temasAlumno
    MATCH (c2:Curso {tipo_curso:'electivo'})-[rct:REL]->(t2:Tema)
    WHERE rct.type = $rel
      AND t2 IN temasAlumno
      AND NOT c2 IN cursosAlumno
    OPTIONAL MATCH (c2)-[rm:REL]->(m:Mencion)
    WHERE rm.type = $rel
    WITH c2, count(DISTINCT t2) AS temasCompartidos, collect(DISTINCT m.nombre) AS menciones
    RETURN c2{.id, .nombre, .tipo_curso} AS curso, temasCompartidos, menciones
    ORDER BY temasCompartidos DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type, limit=limit))

@app.get("/alumnos/<id_alumno>/recomendar")
def recomendar(id_alumno):
    """ Recomendación avanzada (prep + affinity) (CORREGIDO: sin .*) """
    limit = int(request.args.get("limit", 20))
    q = """
    MATCH (a:Alumno {id:$id})-[r:REL {label:'inscripcion'}]->(co:Curso {tipo_curso:'obligatorio'})
    WITH a, co, coalesce(toFloat(r.nota), -1) AS nota
    WHERE nota >= 11 OR toLower(coalesce(r.estado,'')) IN ['aprobado','aprobada','passed']
    WITH a, co,
      CASE
        WHEN ((nota-13)/7.0) < 0 THEN 0.0
        WHEN ((nota-13)/7.0) > 1 THEN 1.0
        ELSE (nota-13)/7.0
      END AS frac
    WITH a, co, (frac*frac) AS w_mastery
    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    WITH a, co, w_mastery, collect(DISTINCT toLower(to.family)) AS famObl
    WHERE size(famObl) > 0
    WITH a, collect({curso:co, w:w_mastery, fam:famObl}) AS obligs
    WHERE size(obligs) > 0
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size(famE) > 0
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, famE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, famE, [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, famE,
      CASE WHEN size(wlist)=0 THEN 0.0
           ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
      END AS prep
    UNWIND obligs AS ob
    WITH ce, prep, ob, famE,
      size([k IN ob.fam WHERE k IN famE]) AS inter,
      size(ob.fam) + size(famE) - size([k IN ob.fam WHERE k IN famE]) AS uni,
      ob.w AS w
    WITH ce, prep,
      CASE WHEN uni = 0 THEN 0.0 ELSE inter / toFloat(uni) END AS sim_jaccard,
      CASE WHEN uni = 0 THEN 0.0 ELSE w * (inter / toFloat(uni)) END AS part
    WITH ce, prep, sum(part) AS numerator, sum(sim_jaccard) AS denominator
    WITH ce, prep, CASE WHEN denominator=0 THEN 0.0 ELSE numerator/denominator END AS affinity
    RETURN
      ce{.id, .nombre, .tipo_curso} AS curso,
      round(prep*100)/100.0     AS prep,
      round(affinity*100)/100.0 AS affinity,
      round((0.6*prep + 0.4*affinity)*100)/100.0 AS score
    ORDER BY score DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, limit=limit))

@app.get("/alumnos/<id_alumno>/recomendacion")
def recomendacion(id_alumno):
    """ Recomendación avanzada con filtro de facultad (CORREGIDO: sin .*) """
    limit = int(request.args.get("limit", 20))
    afinidad_min = float(request.args.get("afinidad_min", 0.30))

    q = """
    MATCH (a:Alumno {id:$id})-[r:REL {label:'inscripcion'}]->(co:Curso {tipo_curso:'obligatorio'})
    WITH a, co, coalesce(toFloat(r.nota), -1) AS nota
    WHERE nota >= 11 OR toLower(coalesce(r.estado,'')) IN ['aprobado','aprobada','passed']
    WITH a, co,
         CASE
           WHEN ((nota-13)/7.0) < 0 THEN 0.0
           WHEN ((nota-13)/7.0) > 1 THEN 1.0
           ELSE (nota-13)/7.0
         END AS frac
    WITH a, co, (frac*frac) AS w_mastery
    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    OPTIONAL MATCH (co)<-[:REL {label:'ofrece'}]-(ca1:Carrera)<-[:REL {label:'pertenece'}]-(fa1:Facultad)
    WITH a, co, w_mastery,
         collect(DISTINCT toLower(to.family)) AS famObl,
         collect(DISTINCT fa1.id) AS facsObl
    WHERE size(famObl) > 0
    WITH a,
         collect({curso:co, w:w_mastery, fam:famObl}) AS obligs,
         collect(DISTINCT facsObl) AS facLists
    WITH a, obligs,
         reduce(acc=[], lst IN facLists | acc + lst) AS facsAll
    WITH a, obligs, [x IN facsAll WHERE x IS NOT NULL] AS alumnoFacIds
    WHERE size(obligs) > 0
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ca2:Carrera)-[:REL {label:'ofrece'}]->(ce)
    OPTIONAL MATCH (fa2:Facultad)-[:REL {label:'pertenece'}]->(ca2)
    WITH a, obligs, alumnoFacIds, ce, collect(DISTINCT fa2.id) AS facCe
    WHERE size([f IN facCe WHERE f IN alumnoFacIds]) > 0
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size(famE) > 0
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, famE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, famE, [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, famE,
         CASE WHEN size(wlist)=0 THEN 0.0
              ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
         END AS prep
    UNWIND obligs AS ob
    WITH ce, prep, ob, famE,
         size([k IN ob.fam WHERE k IN famE]) AS inter,
         size(ob.fam) + size(famE) - size([k IN ob.fam WHERE k IN famE]) AS uni,
         ob.w AS w
    WITH ce, prep,
         CASE WHEN uni = 0 THEN 0.0 ELSE inter / toFloat(uni) END AS sim_jaccard,
         CASE WHEN uni = 0 THEN 0.0 ELSE w * (inter / toFloat(uni)) END AS part
    WITH ce, prep, sum(part) AS numerator, sum(sim_jaccard) AS denominator
    WITH ce, prep, CASE WHEN denominator=0 THEN 0.0 ELSE numerator/denominator END AS affinity
    WHERE affinity >= $afinidad_min
    RETURN
      ce{.id, .nombre, .tipo_curso} AS curso,
      round(prep*100)/100.0     AS prep,
      round(affinity*100)/100.0 AS affinity,
      round((0.6*prep + 0.4*affinity)*100)/100.0 AS score
    ORDER BY score DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, limit=limit, afinidad_min=afinidad_min))

# --- Inicio de la App ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_RUN_PORT", 5000)))