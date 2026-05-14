from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from server.database import engine, get_db, Base
from server.models import Sign, Sample
from server.schemas import SignCreate, SignResponse, SampleCreate, SampleResponse, StatsResponse
import ollama as ollama_client

Base.metadata.create_all(bind=engine)

# Our main app
app = FastAPI(title = "Sign Language API")


# --- Signs CRUD --- #

@app.get("/signs", response_model=list[SignResponse])
def list_signs(standard: str | None = None, hand: str | None = None, db: Session = Depends(get_db)) -> list[SignResponse]:
    """
    TODO: Enrich this description.
    Maps to the endpoint GET /signs 
    
    GET all the signs from our database
    """
    query = db.query(Sign)
    if standard:
        query = query.filter(Sign.standard == standard)
    if hand:
        query = query.filter(Sign.hand == hand)
        
    signs = query.all()
    return [
        SignResponse(
            id=s.id, word=s.word, standard=s.standard,
            description=s.description, hand=s.hand,
            sample_count=len(s.samples)
        ) for s in signs
    ]

@app.get("/signs/{sign_id}", response_model=SignResponse)
def get_sign(sign_id: int, db: Session = Depends(get_db)) -> SignResponse:
    """
    TODO: Enrich this description.
    Maps to the endpoint GET /signs/{id}
    
    GET a single sign from our database
    """
    sign = db.query(Sign).filter(Sign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")
    
    return SignResponse(
        id=sign.id, word=sign.word, standard=sign.standard,
        description=sign.description, hand=sign.hand,
        sample_count=len(sign.samples)
    )

@app.post("/signs", response_model=SignResponse, status_code=201) # HTTP 201: Created
def create_sign(data: SignCreate, db: Session = Depends(get_db)) -> SignResponse:
    """
    TODO: Enrich this description.
    Maps to the endpoint POST /signs
    
    POST a single sign into our database
    """
    # **d means "treat the key-value pairs in the dictionary as 
    # additional named arguments to this function call." (StackOverflow)
    sign = Sign(**data.model_dump())
    
    db.add(sign)
    db.commit()
    db.refresh(sign)
    return SignResponse(
        id=sign.id, word=sign.word, standard=sign.standard,
        description=sign.description, hand=sign.hand,
        sample_count=0
    )

@app.put("/signs/{sign_id}", response_model=SignResponse)
def update_sign(sign_id: int, data: SignCreate, db: Session = Depends(get_db)) -> SignResponse:
    """
    TODO: Enrich this description.
    Maps to the endpoint PUT /signs/{sign_id}
    
    PUT (update) a single already defined sign
    """
    sign = db.query(Sign).filter(Sign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")
    for key, value in data.model_dump().items():
        setattr(sign, key, value)   # This just sets the value attribute to the signs' {key}, example: Sign(wolf): word = "wolf" and so on.
    db.commit()
    db.refresh(sign)
    
    return SignResponse(
        id=sign.id, word=sign.word, standard=sign.standard,
        description=sign.description, hand=sign.hand,
        sample_count=len(sign.samples)
    )
    
@app.delete("/signs/{sign_id}", status_code=204) # HTTP 204: No Content (after delete something this should be the response)
def delete_sign(sign_id: int, db: Session = Depends(get_db)) -> None:
    """
    TODO: Enrich this description.
    Maps to the endpoint DELETE /signs/{sign_id}
    
    DELETE a single sign into our database
    """
    sign = db.query(Sign).filter(Sign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")
    db.delete(sign)
    db.commit()
    
    
# --- Samples --- #

@app.get("/signs/{sign_id}/samples", response_model=list[SampleResponse])
def list_samples(sign_id: int, db: Session = Depends(get_db)) -> list[SampleResponse]:
    """
    TODO: Enrich this description.
    Maps to the endpoint GET /signs/{sign_id}/samples
    
    GET every sample from a sign of our database
    """
    sign = db.query(Sign).filter(Sign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")
    return sign.samples

@app.post("/samples", response_model=SampleResponse, status_code=201)
def create_sample(data: SampleCreate, db: Session = Depends(get_db)) -> SampleResponse:
    """
    TODO: Enrich this description.
    Maps to the endpoint POST /samples
    
    POST a sample to a sign into our database
    """
    sign = db.query(Sign).filter(Sign.id == data.sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")
    sample = Sample(**data.model_dump())
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


# --- Stats Aggregation and LLM Integrartion --- #

@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """
    TODO: Enrich this description.
    Maps to the endpoint GET /stats
    
    GET aggregated stats from our database (very useful later)
    """
    total_signs: int = db.query(Sign).count()
    total_samples: int = db.query(Sample).count()
    
    hand_counts = db.query(Sign.hand, func.count()).group_by(Sign.hand).all()
    signs_per_hand: dict = {hand: count for hand, count in hand_counts}
    
    sample_counts: tuple = (
        db.query(Sign.word, func.count(Sample.id))
        .join(Sample, isouter=True)
        .group_by(Sign.id)
        .all()
    )
    samples_per_sign: dict = {word: count for word, count in sample_counts}
    
    return StatsResponse(
        totla_signs=total_signs,
        total_samples=total_samples,
        signs_per_hand=signs_per_hand,
        samples_per_sign=samples_per_sign,
    )
    
@app.get("/signs/{sign_id}/describe")
def describe_sign(sign_id: int, db: Session = Depends(get_db)):
    sign = db.query(Sign).filter(Sign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")

    sample_count = len(sign.samples)
    prompt = (
        f"You are an ASL instructor. Describe how to perform the sign for '{sign.word}' "
        f"using the {sign.hand} hand(s). "
        f"Additional context: {sign.description or 'none'}. "
        f"We have {sample_count} recorded samples of this sign. "
        f"Keep it concise (2-3 sentences)."
    )

    response = ollama_client.chat(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"sign": sign.word, "description": response["message"]["content"]}