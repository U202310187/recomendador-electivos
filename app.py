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

@app.get("/alumnos")
def get_alumnos():
    """
    Lista de alumnos paginada
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

@app.get("/alumnos/<id_alumno>/recomendar")
def recomendar(id_alumno):
    """
    Calcula recomendaciones de electivos combinando la preparación del alumno y la afinidad temática.
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

    //Fortaleza
    WITH a, co,
     CASE
       WHEN ((nota-13)/7.0) < 0 THEN 0.0
       WHEN ((nota-13)/7.0) > 1 THEN 1.0
       ELSE (nota-13)/7.0
     END AS frac
    WITH a, co, (frac*frac) AS w_mastery

    //Cursos obligatorios
    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    WITH a, co, w_mastery, collect(DISTINCT toLower(to.family)) AS famObl
    WHERE size(famObl) > 0
    WITH a, collect({curso:co, w:w_mastery, fam:famObl}) AS obligs
    WHERE size(obligs) > 0

    //Cursos electivos
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size(famE) > 0

    //Preparación usando prerrequisitos
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, famE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, famE, [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, famE,
     CASE WHEN size(wlist)=0 THEN 0.0
          ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
     END AS prep

    //Afinidad Jaccard
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
    ce{.*} AS curso,
    round(prep*100)/100.0     AS prep,
    round(affinity*100)/100.0 AS affinity,
    round((0.6*prep + 0.4*affinity)*100)/100.0 AS score
    ORDER BY score DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, limit=limit))

@app.get("/alumnos/<id_alumno>/recomendacion")
def recomendacion(id_alumno):
    """
    Recomendación que limita electivos a las mismas facultades del alumno.
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
    //Cursos obligatorios aprobados por el alumno
    MATCH (a:Alumno {id:$id})-[r:REL {label:'inscripcion'}]->(co:Curso {tipo_curso:'obligatorio'})
    WITH a, co, coalesce(toFloat(r.nota), -1) AS nota
    WHERE nota >= 11 OR toLower(coalesce(r.estado,'')) IN ['aprobado','aprobada','passed']

    //Fortaleza
    WITH a, co,
         CASE
           WHEN ((nota-13)/7.0) < 0 THEN 0.0
           WHEN ((nota-13)/7.0) > 1 THEN 1.0
           ELSE (nota-13)/7.0
         END AS frac
    WITH a, co, (frac*frac) AS w_mastery

    //Facultad del alumno
    OPTIONAL MATCH (co)-[:REL {label:'incluye_tema'}]->(to:Tema)
    OPTIONAL MATCH (co)<-[:REL {label:'ofrece'}]-(ca1:Carrera)<-[:REL {label:'pertenece'}]-(fa1:Facultad)
    WITH a, co, w_mastery,
         collect(DISTINCT toLower(to.family)) AS famObl,
         collect(DISTINCT fa1.id) AS facsObl
    WHERE size(famObl) > 0

    //Junta obligatorios y lista de facultades
    WITH a,
         collect({curso:co, w:w_mastery, fam:famObl}) AS obligs,
         collect(DISTINCT facsObl) AS facLists
    WITH a, obligs,
         reduce(acc=[], lst IN facLists | acc + lst) AS facsAll
    WITH a, obligs, [x IN facsAll WHERE x IS NOT NULL] AS alumnoFacIds
    WHERE size(obligs) > 0

    //Electivos ofrecidos en la misma facultad
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ca2:Carrera)-[:REL {label:'ofrece'}]->(ce)
    OPTIONAL MATCH (fa2:Facultad)-[:REL {label:'pertenece'}]->(ca2)
    WITH a, obligs, alumnoFacIds, ce, collect(DISTINCT fa2.id) AS facCe
    WHERE size([f IN facCe WHERE f IN alumnoFacIds]) > 0

    //Familias de temas del electivo
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT toLower(te.family)) AS famE
    WHERE size(famE) > 0

    //Preparación por prerrequisitos
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, famE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, famE, [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, famE,
         CASE WHEN size(wlist)=0 THEN 0.0
              ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
         END AS prep

    //Afinidad Jaccard
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
    Recomendación aleatoria sobre electivos candidatos.
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

    random.shuffle(candidatos)

    return jsonify(candidatos[:limit])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)