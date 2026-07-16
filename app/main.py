from fastapi import FastAPI
from app.database import SessionLocal
from app.models import Node, Selection, Generation
from fastapi import Body
import json
from app.gemini_api import generate_test_cases

app = FastAPI(title="Tri9T AI Assignment")


# Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Home
@app.get("/")
def home():
    return {"message": "API Running Successfully"}


# Show all headings
@app.get("/headings")
def get_headings():

    db = SessionLocal()

    nodes = db.query(Node).all()

    result = []

    for node in nodes:
        result.append({
            "id": node.id,
            "heading": node.heading,
            "level": node.level,
            "version": node.version
        })

    db.close()

    return result


# Get one section by ID
@app.get("/section/{node_id}")
def get_section(node_id: int):

    db = SessionLocal()

    node = db.query(Node).filter(
        Node.id == node_id
    ).first()

    if node is None:
        db.close()
        return {"message": "Section not found"}

    children = db.query(Node).filter(
        Node.parent_id == node.id
    ).all()

    child_list = []

    for child in children:
        child_list.append({
            "id": child.id,
            "heading": child.heading,
            "level": child.level
        })

    db.close()

    return {
        "id": node.id,
        "heading": node.heading,
        "body": node.body,
        "version": node.version,
        "content_hash": node.content_hash,
        "children": child_list
    }

# Search headings
@app.get("/search")
def search(keyword: str):

    db = SessionLocal()

    nodes = db.query(
        Node
    ).filter(
        Node.heading.contains(keyword)
    ).all()

    db.close()

    result = []

    for node in nodes:
        result.append({
            "id": node.id,
            "heading": node.heading,
            "version": node.version
        })

    return result


# Compare Version 1 and Version 2
@app.get("/compare")
def compare():

    db = SessionLocal()

    version1 = db.query(Node).filter(Node.version == 1).all()
    version2 = db.query(Node).filter(Node.version == 2).all()

    db.close()

    if not version1:
        return {"message": "Version 1 not found."}

    if not version2:
        return {"message": "Version 2 not found."}

    old = {}
    new = {}

    for node in version1:
        old[node.heading] = node.content_hash

    for node in version2:
        new[node.heading] = node.content_hash

    added = []
    removed = []
    changed = []

    for heading in new:

        if heading not in old:
            added.append(heading)

        elif new[heading] != old[heading]:
            changed.append(heading)

    for heading in old:

        if heading not in new:
            removed.append(heading)

    return {
        "added": added,
        "removed": removed,
        "changed": changed
    }
    
@app.get("/node/{node_id}/changes")
def node_changes(node_id: int):

    db = SessionLocal()

    node = db.query(Node).filter(
        Node.id == node_id
    ).first()

    if node is None:
        db.close()
        return {"message": "Node not found"}

    other = db.query(Node).filter(
        Node.heading == node.heading,
        Node.version != node.version
    ).first()

    db.close()

    if other is None:
        return {
            "changed": False,
            "summary": "Node exists only in one version."
        }

    if node.content_hash == other.content_hash:
        return {
            "changed": False,
            "summary": "Content unchanged across versions."
        }

    return {
        "changed": True,
        "summary": "Content modified between document versions."
    }
    
@app.post("/selection")
def create_selection(data: dict = Body(...)):

    db = SessionLocal()

    selection = Selection(
        name=data["name"],
        version=data["version"],
        node_ids=json.dumps(data["nodes"])
    )

    db.add(selection)
    db.commit()
    db.refresh(selection)

    db.close()

    return {
        "selection_id": selection.id,
        "message": "Selection created successfully"
    }


@app.get("/generate/{selection_id}")
def generate(selection_id: int):

    db = SessionLocal()

    selection = db.query(Selection).filter(
        Selection.id == selection_id
    ).first()

    if selection is None:
        db.close()
        return {"message": "Selection not found"}

    import json

    node_ids = json.loads(selection.node_ids)

    text = ""

    for node_id in node_ids:

        node = db.query(Node).filter(
            Node.id == node_id
        ).first()

        if node:
            text += node.heading + "\n"
            text += node.body + "\n\n"

    db.close()

    result = generate_test_cases(text)

    generation = Generation(
    selection_id=selection.id,
    generated_text=result,
    version=selection.version
)

    db = SessionLocal()

    print("Saving generation...")

    db.add(generation)

    db.commit()

    db.refresh(generation)
    print("Saved Generation ID:", generation.id)

    db.close()

    return {
        "generation_id": generation.id,
        "selection": selection.name,
        "generated_test_cases": result
}
    
@app.get("/generation/{generation_id}")
def get_generation(generation_id: int):

    db = SessionLocal()

    generation = db.query(Generation).filter(
        Generation.id == generation_id
    ).first()

    if generation is None:
        db.close()
        return {"message": "Generation not found"}

    selection = db.query(Selection).filter(
        Selection.id == generation.selection_id
    ).first()

    latest_version = db.query(Node).order_by(
        Node.version.desc()
    ).first().version

    stale = generation.version != latest_version

    db.close()

    return {
        "generation_id": generation.id,
        "selection_id": generation.selection_id,
        "generated_from_version": generation.version,
        "latest_version": latest_version,
        "stale": stale,
        "generated_text": generation.generated_text
    }
    
@app.get("/selection/{selection_id}/generations")
def get_selection_generations(selection_id: int):

    db = SessionLocal()

    generations = db.query(Generation).filter(
        Generation.selection_id == selection_id
    ).all()

    db.close()

    if not generations:
        return {
            "message": "No generations found"
        }

    result = []

    for g in generations:
        result.append({
            "generation_id": g.id,
            "version": g.version,
            "generated_text": g.generated_text
        })

    return result