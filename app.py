from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from neo4j import GraphDatabase, basic_auth
import random

uri = "bolt://neo4j:7687"
user = "neo4j"
password = "Admin1234!"
driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

app = Flask(__name__)
CORS(app)

swagger = Swagger(app, template={
    "info": {"title": "Recomendador de Electivos API", "version": "1.0"}
})

def run_query(cypher, **params):
    try:
        with driver.session() as session:
            res = session.run(cypher, **params)
            return [r.data() for r in res]
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    """
    Health check
    ---
    tags:
      - Sistema
    responses:
      200:
        description: OK
        examples:
          application/json: { "ok": true }
    """
    try:
        run_query("RETURN 1 AS ok")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.post("/login")
def login():
    """
    Login simplificado por código UPC del alumno.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            codigo:
              type: string
              example: "U202310187"
    responses:
      200:
        description: Alumno encontrado (devuelve el nodo Alumno completo)
      400:
        description: Falta parámetro
      404:
        description: Alumno no encontrado
    """
    payload = request.get_json() or {}
    codigo = payload.get("codigo")

    if not codigo:
        return jsonify({"error": "El campo 'codigo' es obligatorio."}), 400

    q = """
    MATCH (a:Alumno {codigo:$codigo})
    RETURN a{.*} AS alumno
    """
    data = run_query(q, codigo=codigo)

    # Si run_query devolvió {"error": ...}
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500

    if not data:
        return jsonify({"error": "Alumno no encontrado"}), 404

    # En el front puedes guardar alumno.id para llamar al resto de endpoints
    return jsonify(data[0])


@app.get("/cursos")
def get_cursos():
    """
    Lista de cursos
    ---
    tags:
      - Cursos
    parameters:
      - in: query
        name: tipo
        type: string
        required: false
        description: obligatorio | electivo
      - in: query
        name: mencion
        type: string
        required: false
      - in: query
        name: limit
        type: integer
        required: false
        default: 50
    responses:
      200:
        description: Lista de cursos
    """
    """?tipo=obligatorio|electivo  ?mencion=...  ?limit=50"""
    tipo = request.args.get("tipo")
    mencion = request.args.get("mencion")
    limit = int(request.args.get("limit", 50))

    where = []
    if tipo:
        where.append("c.tipo_curso = $tipo")
    if mencion:
        where.append("c.mencion = $mencion")
    where_clause = ("WHERE " + " AND ".join(where)) if where else ""

    q = f"""
    MATCH (c:Curso)
    {where_clause}
    RETURN c.id AS id, c.codigo AS codigo, c.nombre AS nombre,
           c.tipo_curso AS tipo_curso, c.mencion AS mencion, c.ciclo_tipo_curso AS ciclo
    ORDER BY c.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, tipo=tipo, mencion=mencion, limit=limit))

@app.get("/temas")
def get_temas():
    """
    Lista de temas
    ---
    tags:
      - Temas
    responses:
      200:
        description: Lista de temas
    """
    q = """
    MATCH (t:Tema)
    RETURN t{.*} AS tema
    ORDER BY t.nombre
    """
    return jsonify(run_query(q))

@app.get("/menciones")
def get_menciones():
    """
    Lista de menciones
    ---
    tags:
      - Menciones
    responses:
      200:
        description: Lista de menciones
    """
    q = """
    MATCH (m:Mencion)
    RETURN m{.*} AS mencion
    ORDER BY m.nombre
    """
    return jsonify(run_query(q))

@app.get("/cursos/<id_curso>")
def get_curso(id_curso):
    """
    Detalle de curso
    ---
    tags:
      - Cursos
    parameters:
      - in: path
        name: id_curso
        type: string
        required: true
    responses:
      200:
        description: Curso encontrado
      404:
        description: No encontrado
    """
    q = """
    MATCH (c:Curso {id:$id})
    RETURN c{.*} AS curso
    """
    data = run_query(q, id=id_curso)
    return (jsonify(data[0]) if data else (jsonify({"error":"No encontrado"}), 404))

@app.get("/cursos/<id_curso>/temas")
def get_temas_de_curso(id_curso):
    """
    Temas de un curso
    ---
    tags:
      - Cursos
    parameters:
      - in: path
        name: id_curso
        type: string
        required: true
        description: ID del curso
      - in: query
        name: rel_type
        type: string
        default: Directed
        required: false
        description: Tipo de relación usado en r.type
    responses:
      200:
        description: Lista de temas asociados al curso
    """
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (c:Curso {id:$id})-[r:REL]->(t:Tema)
    WHERE r.type = $rel
    RETURN t{.*} AS tema, r{.*} AS relacion
    ORDER BY t.nombre
    """
    return jsonify(run_query(q, id=id_curso, rel=rel_type))

@app.get("/menciones/<nombre>/cursos")
def get_cursos_por_mencion(nombre):
    """
    Cursos asociados a una mención
    ---
    tags:
      - Menciones
    parameters:
      - in: path
        name: nombre
        type: string
        required: true
        description: Nombre de la mención
      - in: query
        name: rel_type
        type: string
        default: Directed
        required: false
        description: Tipo de relación usado en r.type
    responses:
      200:
        description: Lista de cursos asociados a la mención
    """
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (m:Mencion {nombre:$nom})<-[r:REL]-(c:Curso)
    WHERE r.type = $rel
    RETURN c{.*} AS curso
    ORDER BY c.nombre
    """
    return jsonify(run_query(q, nom=nombre, rel=rel_type))

@app.get("/cursos/<id_curso>/relaciones")
def get_relaciones_de_curso(id_curso):
    """
    Relaciones de un curso (vecinos + etiqueta de relación)
    ---
    tags:
      - Cursos
    parameters:
      - in: path
        name: id_curso
        type: string
        required: true
        description: ID del curso
    responses:
      200:
        description: Vecinos y relaciones del curso
    """
    """Devuelve vecinos y la etiqueta real de la relación almacenada en r.type"""
    q = """
    MATCH (c:Curso {id:$id})-[r]->(n)
    RETURN type(r) AS relNeo4j, r.type AS relCSV, n{.*} AS vecino, startNode(r).id AS from, endNode(r).id AS to
    """
    return jsonify(run_query(q, id=id_curso))

@app.get("/stats")
def stats():
    """
    Estadísticas generales
    ---
    tags:
      - Sistema
    responses:
      200:
        description: Conteos de nodos y relaciones
    """
    q = """
    CALL {
      MATCH (c:Curso) RETURN count(c) AS cursos
    }
    CALL {
      MATCH (t:Tema) RETURN count(t) AS temas
    }
    CALL {
      MATCH (m:Mencion) RETURN count(m) AS menciones
    }
    CALL {
      MATCH ()-[r]->() RETURN count(r) AS relaciones
    }
    RETURN cursos, temas, menciones, relaciones
    """
    return jsonify(run_query(q)[0])

@app.get("/grafo")
def grafo():
    """
    Grafo simplificado para visualización
    ---
    tags:
      - Grafo
    parameters:
      - in: query
        name: limit
        type: integer
        required: false
        default: 200
        description: Límite de relaciones a devolver para evitar cargas grandes
    responses:
      200:
        description: Nodos y relaciones para visualización
        examples:
          application/json:
            nodes:
              - id: CURSO001
                nombre: Matemática I
                labels: ["Curso"]
            edges:
              - from: CURSO001
                to: TEMA045
                rel: REL
                relCSV: incluye_tema
    """
    """?limit=200  — devuelve nodos + relaciones simples para pintar en el front"""
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
    # unir nodos fuente y destino en un solo arreglo único
    seen, nodes = set(), []
    for n in rows["sourceNodes"] + rows["targetNodes"]:
        if n["id"] not in seen:
            seen.add(n["id"])
            nodes.append(n)
    return jsonify({"nodes": nodes, "edges": rows["rels"]})

@app.get("/alumnos")
def get_alumnos():
    """
    Lista de alumnos (paginada)
    ---
    tags:
      - Alumnos
    parameters:
      - in: query
        name: q
        type: string
        required: false
      - in: query
        name: limit
        type: integer
        default: 50
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: sort
        type: string
        default: id
        enum: [id, nombre]
      - in: query
        name: order
        type: string
        default: asc
        enum: [asc, desc]
    responses:
      200:
        description: Lista de alumnos
    """
    """
    ?q=texto
    ?limit=50
    ?page=1
    ?sort=id|nombre  (default: id)
    ?order=asc|desc  (default: asc)
    """
    qtext = request.args.get("q", "")
    limit = int(request.args.get("limit", 50))
    page = max(int(request.args.get("page", 1)), 1)
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc").lower()
    skip = (page - 1) * limit

    order_by = {
        ("id","asc"):  "ORDER BY toInteger(split(a.id,'_')[1]) ASC",
        ("id","desc"): "ORDER BY toInteger(split(a.id,'_')[1]) DESC",
        ("nombre","asc"):  "ORDER BY toLower(coalesce(a.nombre,'')) ASC",
        ("nombre","desc"): "ORDER BY toLower(coalesce(a.nombre,'')) DESC",
    }.get((sort, order), "ORDER BY toInteger(split(a.id,'_')[1]) ASC")

    q = f"""
    MATCH (a:Alumno)
    WHERE $q = '' OR toLower(coalesce(a.nombre,'')) CONTAINS toLower($q)
    RETURN a{{.*}} AS alumno
    {order_by}
    SKIP $skip
    LIMIT $limit
    """
    return jsonify(run_query(q, q=qtext, skip=skip, limit=limit))

@app.get("/alumnos/<id_alumno>")
def get_alumno(id_alumno):
    """
    Detalle de alumno
    ---
    tags:
      - Alumnos
    parameters:
      - in: path
        name: id_alumno
        type: string
        required: true
    responses:
      200:
        description: Alumno encontrado
      404:
        description: No encontrado
    """
    q = """
    MATCH (a:Alumno {id:$id})
    RETURN a{.*} AS alumno
    """
    data = run_query(q, id=id_alumno)
    return (jsonify(data[0]) if data else (jsonify({"error":"No encontrado"}), 404))

@app.get("/alumnos/by_codigo/<codigo>")
def get_alumno_por_codigo(codigo):
    """
    Buscar alumno por código universitario.
    ---
    tags:
      - Alumnos
    parameters:
      - in: path
        name: codigo
        type: string
        required: true
        description: Código del alumno (ej. "A_1")
    responses:
      200:
        description: Alumno encontrado
      404:
        description: Alumno no encontrado
    """
    q = """
    MATCH (a:Alumno {id:$codigo})
    RETURN a{.*} AS alumno
    """
    data = run_query(q, codigo=codigo)

    if not data:
        return jsonify({"error": "Alumno no encontrado"}), 404

    return jsonify(data[0])

@app.get("/alumnos/<id_alumno>/cursos")
def get_cursos_de_alumno(id_alumno):
    """
    Cursos vinculados a un alumno
    ---
    tags:
      - Alumnos
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno (ej. "ALU_001")
      - name: rel_type
        in: query
        type: string
        required: false
        default: Directed
        description: Tipo lógico de relación almacenado en r.type
    responses:
      200:
        description: Lista de cursos relacionados con el alumno
        examples:
          application/json:
            - curso:
                id: CURSO001
                nombre: Matemática I
                tipo_curso: obligatorio
              relacion:
                type: Directed
                label: incluye_tema
    """
    """Cursos vinculados al alumno por cualquier dirección. Usa r.type='Directed' por defecto."""
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (a:Alumno {id:$id})-[r:REL]-(c:Curso)
    WHERE r.type = $rel
    RETURN c{.*} AS curso, r{.*} AS relacion
    ORDER BY c.nombre
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type))

@app.get("/alumnos/<id_alumno>/temas")
def get_temas_de_alumno(id_alumno):
    """
    Temas alcanzados por un alumno a través de cursos
    ---
    tags:
      - Alumnos
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno
      - name: rel_type
        in: query
        type: string
        required: false
        default: Directed
        description: Tipo lógico de relación almacenado en r.type
    responses:
      200:
        description: Lista de temas vinculados al alumno
        examples:
          application/json:
            - tema:
                id: TEMA045
                nombre: Derivadas
    """
    """Temas alcanzados por el alumno vía cursos relacionados."""
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(c:Curso)
    WHERE r1.type = $rel
    MATCH (c)-[r2:REL]->(t:Tema)
    WHERE r2.type = $rel
    WITH DISTINCT t
    ORDER BY t.nombre
    RETURN t{.*} AS tema
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type))

@app.get("/alumnos/<id_alumno>/recomendaciones")
def recomendar_cursos(id_alumno):
    """
    Recomendación simple de cursos electivos basada en la intersección de temas con los cursos del alumno.
    ---
    tags:
      - Recomendador
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno (ej. "ALU_001")
      - name: rel_type
        in: query
        type: string
        required: false
        default: Directed
        description: Tipo de relación lógica almacenada en r.type
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
        description: Número máximo de cursos recomendados
    responses:
      200:
        description: Cursos sugeridos con base en coincidencias de temas
        examples:
          application/json:
            - curso:
                id: CUR_ELEC045
                nombre: Introducción al Machine Learning
                tipo_curso: electivo
              temasCompartidos: 6
              menciones:
                - Data Science & Analytics
                - Computación Científica
    """
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
    RETURN c2{.*} AS curso, temasCompartidos, menciones
    ORDER BY temasCompartidos DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type, limit=limit))

@app.get("/alumnos/<id_alumno>/grafo")
def grafo_alumno(id_alumno):
    """
    Subgrafo del alumno (nodos y aristas para visualización)
    ---
    tags:
      - Grafo
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno (ej. "ALU_001")
      - name: rel_type
        in: query
        type: string
        required: false
        default: Directed
        description: Valor lógico almacenado en r.type a filtrar
      - name: limit
        in: query
        type: integer
        required: false
        default: 300
        description: Límite de relaciones para acotar el subgrafo
    responses:
      200:
        description: Nodos y aristas del subgrafo del alumno
        examples:
          application/json:
            nodes:
              - id: ALU_001
                nombre: "Juan Pérez"
                labels: ["Alumno"]
              - id: CUR_010
                nombre: "Algoritmos"
                labels: ["Curso"]
            edges:
              - from: ALU_001
                to: CUR_010
                rel: "REL"
                relCSV: "inscripcion"
    """
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

@app.get("/alumnos/<id_alumno>/recomendar")
def recomendar(id_alumno):
    """
    Calcula recomendaciones de electivos combinando la preparación del alumno (en prerrequisitos) y la afinidad temática.
    ---
    tags:
      - Recomendador
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno (ej. "ALU_001")
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Número máximo de cursos recomendados
    responses:
      200:
        description: Lista de electivos con métricas de preparación y afinidad
        examples:
          application/json:
            - curso:
                id: CUR_ELEC_032
                nombre: "Minería de Datos"
                tipo_curso: "electivo"
              prep: 0.78
              affinity: 0.62
              score: 0.71
    """
    limit = int(request.args.get("limit", 20))
    q = """
    //Cursos obligatorios aprobados por el alumno
    MATCH (a:Alumno {id:$id})-[r:REL {label:'inscripcion'}]->(co:Curso {tipo_curso:'obligatorio'})
    WITH a, co, coalesce(toFloat(r.nota), -1) AS nota
    WHERE nota >= 11 OR toLower(coalesce(r.estado,'')) IN ['aprobado','aprobada','passed']

    // Fortaleza
    WITH a, co,
     CASE
       WHEN ((nota-13)/7.0) < 0 THEN 0.0
       WHEN ((nota-13)/7.0) > 1 THEN 1.0
       ELSE (nota-13)/7.0
     END AS frac
    WITH a, co, (frac*frac) AS w_mastery

    // Familias del obligatorio
    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    WITH a, co, w_mastery, collect(DISTINCT toLower(to.family)) AS famObl
    WHERE size(famObl) > 0
    WITH a, collect({curso:co, w:w_mastery, fam:famObl}) AS obligs
    WHERE size(obligs) > 0

    // Electivos y familias (propios + heredados si los añadiste)
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size(famE) > 0

    // Preparación usando prerrequisitos
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, famE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, famE, [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, famE,
     CASE WHEN size(wlist)=0 THEN 0.0
          ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
     END AS prep

    // Afinidad (Jaccard ponderado por familias)
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

    WITH
        ce,
        round(prep*100)/100.0     AS prep,
        round(affinity*100)/100.0 AS affinity,
        round((0.6*prep + 0.4*affinity)*100)/100.0 AS score
    WHERE score > 0
    RETURN ce{.*} AS curso, prep, affinity, score
    ORDER BY score DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, limit=limit))

@app.get("/alumnos/<id_alumno>/recomendacion")
def recomendacion(id_alumno):
    """
    Recomendación que limita electivos a las mismas facultades del alumno y permite fijar un umbral mínimo de afinidad.
    ---
    tags:
      - Recomendador
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno (p.ej. "A_34")
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Número máximo de cursos recomendados
      - name: afinidad_min
        in: query
        type: number
        required: false
        default: 0.30
        description: Umbral mínimo de afinidad (0..1) para filtrar recomendaciones
    responses:
      200:
        description: Lista de electivos recomendados con métricas de preparación y afinidad
        examples:
          application/json:
            - curso:
                id: "C_1403"
                nombre: "ELEC-03-203"
                tipo_curso: "electivo"
              prep: 0.25
              affinity: 0.75
              score: 0.45
    """
    limit = int(request.args.get("limit", 20))
    afinidad_min = float(request.args.get("afinidad_min", 0.30))

    q = """
    // RECOMENDADOR POR FAMILIAS + FILTRO DE RELEVANCIA (sin APOC)
    MATCH (a:Alumno {id:$id})-[r:REL {label:'inscripcion'}]->(co:Curso {tipo_curso:'obligatorio'})
    WITH a, co, coalesce(toFloat(r.nota), -1) AS nota
    WHERE nota >= 11 OR toLower(coalesce(r.estado,'')) IN ['aprobado','aprobada','passed']

    // Fortaleza
    WITH a, co,
         CASE
           WHEN ((nota-13)/7.0) < 0 THEN 0.0
           WHEN ((nota-13)/7.0) > 1 THEN 1.0
           ELSE (nota-13)/7.0
         END AS frac
    WITH a, co, (frac*frac) AS w_mastery

    // Familias del obligatorio + facultades del alumno
    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    OPTIONAL MATCH (co)<-[:REL {label:'ofrece'}]-(ca1:Carrera)<-[:REL {label:'pertenece'}]-(fa1:Facultad)
    WITH a, co, w_mastery,
         collect(DISTINCT toLower(to.family)) AS famObl,
         collect(DISTINCT fa1.id) AS facsObl
    WHERE size(famObl) > 0

    // Junta obligatorios y lista de facultades (aplanado sin APOC)
    WITH a,
         collect({curso:co, w:w_mastery, fam:famObl}) AS obligs,
         collect(DISTINCT facsObl) AS facLists
    WITH a, obligs,
         reduce(acc=[], lst IN facLists | acc + lst) AS facsAll
    WITH a, obligs, [x IN facsAll WHERE x IS NOT NULL] AS alumnoFacIds
    WHERE size(obligs) > 0

    // Electivos ofrecidos en las MISMAS facultades
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ca2:Carrera)-[:REL {label:'ofrece'}]->(ce)
    OPTIONAL MATCH (fa2:Facultad)-[:REL {label:'pertenece'}]->(ca2)
    WITH a, obligs, alumnoFacIds, ce, collect(DISTINCT fa2.id) AS facCe
    WHERE size([f IN facCe WHERE f IN alumnoFacIds]) > 0

    // Familias de temas del electivo
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size(famE) > 0

    // Preparación por prerrequisitos
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, famE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, famE, [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, famE,
         CASE WHEN size(wlist)=0 THEN 0.0
              ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
         END AS prep

    // Afinidad (Jaccard ponderado por familias)
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

    // Filtro de afinidad mínima
    WHERE affinity >= $afinidad_min

    RETURN
      ce{.*} AS curso,
      round(prep*100)/100.0     AS prep,
      round(affinity*100)/100.0 AS affinity,
      round((0.6*prep + 0.4*affinity)*100)/100.0 AS score
    ORDER BY score DESC, curso.nombre
    LIMIT $limit
    """

    return jsonify(run_query(q, id=id_alumno, limit=limit, afinidad_min=afinidad_min))

@app.get("/alumnos/<id_alumno>/recomendaciones_aleatorio")
def recomendar_aleatorio(id_alumno):
    """
    Recomendación aleatoria (extra) sobre electivos candidatos.
    ---
    tags:
      - Recomendador
    parameters:
      - name: id_alumno
        in: path
        type: string
        required: true
        description: ID del alumno (ej. "ALU_001")
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Número máximo de cursos a devolver
    responses:
      200:
        description: Lista de cursos electivos en orden aleatorio
    """
    limit = int(request.args.get("limit", 20))

    # Candidatos: electivos relacionados temáticamente con los cursos del alumno
    q = """
    MATCH (a:Alumno {id:$id})-[r:REL {label:'inscripcion'}]->(co:Curso {tipo_curso:'obligatorio'})
    WITH a, co, coalesce(toFloat(r.nota), -1) AS nota
    WHERE nota >= 11 OR toLower(coalesce(r.estado,'')) IN ['aprobado','aprobada','passed']

    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    WITH a, collect(DISTINCT toLower(to.family)) AS famObl
    WHERE size(famObl) > 0

    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH ce, famObl, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size([f IN famE WHERE f IN famObl]) > 0

    RETURN ce{.*} AS curso
    """
    candidatos = run_query(q, id=id_alumno)

    if isinstance(candidatos, dict) and "error" in candidatos:
        return jsonify(candidatos), 500

    # Fisher–Yates / random.shuffle (O(n))
    random.shuffle(candidatos)

    return jsonify(candidatos[:limit])

@app.get("/alumnos/by_codigo/<codigo>/cursos_aprobados")
def get_cursos_aprobados_por_codigo(codigo):
    """
    Cursos obligatorios aprobados por un alumno (búsqueda por código)
    ---
    tags:
      - Alumnos
    parameters:
      - name: codigo
        in: path
        type: string
        required: true
        description: Código del alumno (ej. "A_1")
    responses:
      200:
        description: Lista de cursos obligatorios aprobados
        examples:
          application/json:
            - curso:
                id: C_1234
                nombre: CURSO-01-001
                tipo_curso: obligatorio
              relacion:
                type: APROBADO
                nota: 15
    """
    q = """
    MATCH (a:Alumno {id: $codigo})-[r:REL]->(c:Curso)
    WHERE r.type = 'APROBADO'
      AND c.tipo_curso = 'obligatorio'
    RETURN c{.*} AS curso, r{.*} AS relacion
    ORDER BY c.nombre
    """
    return jsonify(run_query(q, codigo=codigo))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)