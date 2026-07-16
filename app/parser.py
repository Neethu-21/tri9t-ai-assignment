import fitz
import re
import hashlib

from app.database import SessionLocal, Base, engine
from app.models import Node

# Create table if it doesn't exist
Base.metadata.create_all(bind=engine)


def calculate_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_level(heading):
    number = re.match(r'^(\d+(?:\.\d+)*)', heading).group(1)
    return number.count(".") + 1


def import_pdf(pdf_path, version):

    db = SessionLocal()

    pdf = fitz.open(pdf_path)

    current_heading = ""
    current_body = ""
    current_level = 0

    parent_stack = {}

    for page in pdf:

        text = page.get_text()

        lines = text.split("\n")

        for line in lines:

            line = line.strip()

            if line == "":
                continue

            if re.match(r'^\d+(\.\d+)*\.', line):

                if current_heading != "":

                    parent_id = None

                    if current_level > 1:
                        parent_id = parent_stack.get(current_level - 1)

                    node = Node(
                        version=version,
                        heading=current_heading,
                        level=current_level,
                        body=current_body.strip(),
                        content_hash=calculate_hash(current_body),
                        parent_id=parent_id
                    )

                    db.add(node)
                    db.commit()
                    db.refresh(node)

                    parent_stack[current_level] = node.id

                current_heading = line
                current_body = ""
                current_level = get_level(line)

            else:

                current_body += line + " "

    if current_heading != "":

        parent_id = None

        if current_level > 1:
            parent_id = parent_stack.get(current_level - 1)

        node = Node(
            version=version,
            heading=current_heading,
            level=current_level,
            body=current_body.strip(),
            content_hash=calculate_hash(current_body),
            parent_id=parent_id
        )

        db.add(node)
        db.commit()

    pdf.close()
    db.close()

    print(f"Version {version} imported successfully.")


if __name__ == "__main__":

    import_pdf("data/ct200_manual.pdf", 1)

    import_pdf("data/ct200_manual_v2.pdf", 2)