import json
from server.database import engine, SessionLocal, Base
from server.models import Sign, Sample

Base.metadata.create_all(bind=engine)

def seed() -> None:
    """
    TODO: Enrich this comment session.
    Load initial dataset to our database.
    TODO: Add some robustness to this file (if a sign exists, it doesn't create it twice)
    """
    db = SessionLocal()
    
    # Clean previous data
    db.query(Sample).delete()
    db.query(Sign).delete()
    db.commit()
    
    with open("data/wlasl_subset.json") as f:
        signs_data = json.load(f)
    
    for entry in signs_data:
        sign = Sign(
            word = entry["word"],
            standard = entry.get("standard", "ASL"),
            hand = entry["hand"],
            description = entry.get("description"),
        )
        db.add(sign)
        db.commit()
        db.refresh(sign)
    
        for sample in entry.get("samples", []):
            s = Sample(
                sign_id = sign.id,
                emg_signal = sample.get("emg_signal"),
                image_url = sample.get("image_url"),
            )
            db.add(s)
    
    db.commit()
    db.close()
    print(f"Seeded {len(signs_data)} signs.")

if __name__ == "__main__":
    seed()