from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
import re

app = FastAPI()

# Allow the React frontend to communicate with this Python API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading CAMeL Tools Morphological Database... (This may take a moment)")
# Load the default Morphological Database
db = MorphologyDB.builtin_db()
analyzer = Analyzer(db)
print("Database loaded. Server ready!")

class ParseRequest(BaseModel):
    words: list[str]
    stateType: str # 'raf', 'nasb', 'jarr'

@app.post("/api/detect")
def detect_nahw(request: ParseRequest):
    targets = []
    
    # Map React's state strings to CamelTools 'cas' (case) feature keys
    # n = Nominative (Raf'), a = Accusative (Nasb), g = Genitive (Jarr)
    target_cas = 'n' if request.stateType == 'raf' else 'a' if request.stateType == 'nasb' else 'g'
    
    for i, word in enumerate(request.words):
        # Clean punctuation from the word before analysis
        clean_word = re.sub(r'[.،؟!؛:]+', '', word)
        
        if not clean_word:
            continue
            
        # Get morphological analyses for the word
        analyses = analyzer.analyze(clean_word)
        
        if analyses:
            # CAMeL Tools returns a list of possible analyses sorted by probability.
            # We take the most likely one (index 0).
            best_analysis = analyses[0]
            
            # Check if the 'cas' (case) feature matches our target
            if best_analysis.get('cas') == target_cas:
                targets.append(i)
                
    return {"targets": targets}