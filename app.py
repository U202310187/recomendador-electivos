from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from neo4j import GraphDatabase, basic_auth

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
    try:
        run_query("RETURN 1 AS ok")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/cursos")
def get_cursos():
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
    q = """
    MATCH (t:Tema)
    RETURN t{.*} AS tema
    ORDER BY t.nombre
    """
    return jsonify(run_query(q))

@app.get("/menciones")
def get_menciones():
    q = """
    MATCH (m:Mencion)
    RETURN m{.*} AS mencion
    ORDER BY m.nombre
    """
    return jsonify(run_query(q))

@app.get("/cursos/<id_curso>")
def get_curso(id_curso):
    q = """
    MATCH (c:Curso {id:$id})
    RETURN c{.*} AS curso
    """
    data = run_query(q, id=id_curso)
    return (jsonify(data[0]) if data else (jsonify({"error":"No encontrado"}), 404))

@app.get("/cursos/<id_curso>/temas")
def get_temas_de_curso(id_curso):
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
    """Devuelve vecinos y la etiqueta real de la relación almacenada en r.type"""
    q = """
    MATCH (c:Curso {id:$id})-[r]->(n)
    RETURN type(r) AS relNeo4j, r.type AS relCSV, n{.*} AS vecino, startNode(r).id AS from, endNode(r).id AS to
    """
    return jsonify(run_query(q, id=id_curso))

@app.get("/search")
def search():
    """?q=texto ?limit=20 — busca por nombre de curso/tema/mención"""
    qtext = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))
    q = """
    CALL {
      MATCH (c:Curso)  WHERE toLower(c.nombre)  CONTAINS toLower($q)
      RETURN 'curso' AS tipo, c.id AS id, c.nombre AS nombre
      UNION
      MATCH (t:Tema)   WHERE toLower(t.nombre)  CONTAINS toLower($q)
      RETURN 'tema'  AS tipo, t.id AS id, t.nombre AS nombre
      UNION
      MATCH (m:Mencion) WHERE toLower(m.nombre) CONTAINS toLower($q)
      RETURN 'mencion' AS tipo, m.id AS id, m.nombre AS nombre
    }
    RETURN tipo,id,nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, q=qtext, limit=limit))

@app.get("/stats")
def stats():
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
    q = """
    MATCH (a:Alumno {id:$id})
    RETURN a{.*} AS alumno
    """
    data = run_query(q, id=id_alumno)
    return (jsonify(data[0]) if data else (jsonify({"error":"No encontrado"}), 404))

@app.get("/alumnos/<id_alumno>/cursos")
def get_cursos_de_alumno(id_alumno):
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
    """Temas alcanzados por el alumno vía cursos relacionados."""
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(c:Curso)
    WHERE r1.type = $rel
    MATCH (c)-[r2:REL]->(t:Tema)
    WHERE r2.type = $rel
    RETURN DISTINCT t{.*} AS tema
    ORDER BY t.nombre
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type))

@app.get("/alumnos/<id_alumno>/menciones")
def get_menciones_de_alumno(id_alumno):
    rel_type = request.args.get("rel_type", "Directed")
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(c:Curso)
    WHERE r1.type = $rel
    MATCH (c)-[r2:REL]->(m:Mencion)
    WHERE r2.type = $rel
    RETURN DISTINCT m{.*} AS mencion
    ORDER BY m.nombre
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type))

@app.get("/alumnos/<id_alumno>/recomendaciones")
def recomendar_cursos(id_alumno):
    rel_type = request.args.get("rel_type", "Directed")
    limit = int(request.args.get("limit", 10))
    q = """
   
    MATCH (a:Alumno {id:$id})-[r1:REL]-(c:Curso)
    WHERE r1.type = $rel
    WITH a, collect(DISTINCT c) AS cursosAlumno

    MATCH (c1:Curso)-[rc:REL]->(t:Tema)
    WHERE rc.type = $rel AND c1 IN cursosAlumno
    WITH a, cursosAlumno, collect(DISTINCT t) AS temasAlumno

    MATCH (c2:Curso)-[rct:REL]->(t2:Tema)
    WHERE rct.type = $rel AND t2 IN temasAlumno AND NOT c2 IN cursosAlumno

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
    rel_type = request.args.get("rel_type", "Directed")
    limit = int(request.args.get("limit", 300))
    q = """
    MATCH (a:Alumno {id:$id})-[r1:REL]-(n1)
    WHERE r1.type = $rel
    OPTIONAL MATCH (n1)-[r2:REL]->(n2)
    WHERE r2.type = $rel
    WITH a, collect(DISTINCT n1) AS n1s, collect(DISTINCT r1) + collect(DISTINCT r2) AS rels, collect(DISTINCT n2) AS n2s
    WITH a, apoc.coll.toSet(n1s + n2s) AS nodes, rels
    RETURN
      [x IN nodes | x{.id, .nombre, labels:labels(x)}] AS nodes,
      [r IN rels | {from:startNode(r).id, to:endNode(r).id, rel:type(r), relCSV:r.type}] AS edges
    """
    return jsonify(run_query(q, id=id_alumno, rel=rel_type, limit=limit))

@app.get("/alumnos/<id_alumno>/recomendar")
def recomendar(id_alumno):
    limit = int(request.args.get("limit", 20))
    q = """
    //Cursos obligatorios aprobados por el alumno
    MATCH (a:Alumno {id:$id})-[r_ins:REL {label:'inscripcion'}]->(c_obl:Curso {tipo_curso:'obligatorio'})
    WITH a, c_obl, coalesce(r_ins.nota, 0.0) AS nota

    //Cálculo de Fortaleza (w_mastery)
    WITH a, c_obl,
         CASE 
            WHEN ( (nota-13)/7.0 ) < 0 THEN 0.0
            WHEN ( (nota-13)/7.0 ) > 1 THEN 1.0
            ELSE (nota-13)/7.0
         END AS frac
    WITH a, c_obl, (frac * frac) AS w_mastery

    //Temas de cada obligatorio
    OPTIONAL MATCH (c_obl)-[:REL {label:'incluye_tema'}]->(t:Tema)
    WITH a, c_obl, w_mastery, collect(DISTINCT t) AS temasObl
    WITH a, collect({curso:c_obl, w:w_mastery, temas:temasObl}) AS obligs

    //Electivos candidatos y sus temas
    MATCH (ce:Curso {tipo_curso:'electivo'})
    OPTIONAL MATCH (ce)-[:REL {label:'incluye_tema'}]->(te:Tema)
    WITH a, obligs, ce, collect(DISTINCT te) AS temasE

    //Cálculo de Preparación (promedio de fortaleza en prerrequisitos)
    OPTIONAL MATCH (co:Curso {tipo_curso:'obligatorio'})-[:REL {label:'prerrequisito_obl_elec'}]->(ce)
    WITH a, obligs, ce, temasE, collect(DISTINCT co) AS prereqs
    WITH a, obligs, ce, temasE,
         [x IN obligs WHERE x.curso IN prereqs | x.w] AS wlist
    WITH a, obligs, ce, temasE,
         CASE WHEN size(wlist)=0 THEN 0.0
              ELSE reduce(s=0.0, v IN wlist | s+v) / toFloat(size(wlist))
         END AS prep

    //Cálculo de similitud temática entre cursos (Jaccard ponderado)
    //size([t IN ob.temas WHERE t IN temasE]) AS inter, [ES EL NUMERADOR]
    //size(ob.temas) + size(temasE) - size([t IN ob.temas WHERE t IN temasE]) AS uni [ES EL DENOMINADOR]
    UNWIND obligs AS ob
    WITH ce, prep, ob, temasE,
         size([t IN ob.temas WHERE t IN temasE]) AS inter,
         size(ob.temas) + size(temasE) - size([t IN ob.temas WHERE t IN temasE]) AS uni
    WITH ce, prep,
         CASE WHEN uni = 0 THEN 0.0 ELSE inter / toFloat(uni) END AS sim_jaccard,
         CASE WHEN uni = 0 THEN 0.0 ELSE ob.w * (inter / toFloat(uni)) END AS part
    WITH ce, prep, sum(part) AS numerator, sum(sim_jaccard) AS denominator
    WITH ce, prep,
         CASE WHEN denominator = 0 THEN 0.0 
              ELSE numerator / denominator 
         END AS affinity

    //Score final - con Order By se aplica Mergesort
    RETURN
      ce{.*} AS curso,
      round(prep*100)/100.0 AS prep,
      round(affinity*100)/100.0 AS affinity,
      round((0.6*prep + 0.4*affinity)*100)/100.0 AS score
    ORDER BY score DESC, curso.nombre
    LIMIT $limit
    """
    return jsonify(run_query(q, id=id_alumno, limit=limit))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)