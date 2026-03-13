import codecs
import chromadb
from cyberhuatuo.config import config
from cyberhuatuo.searcher import search_cases
from cyberhuatuo.diagnosis import build_diagnosis_prompt

def test_prompt():
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
    results = search_cases(client, query="agent", top_k=2)
    
    with codecs.open('test_out_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(f"Found {len(results)} results.\n")
        for idx, r in enumerate(results):
            f.write(f"Result {idx+1}: contributor={r.contributor}\n")
    
        messages = build_diagnosis_prompt("My agent is failing with timeout", results)
        
        for m in messages:
            if m["role"] == "user":
                f.write("\n--- USER PROMPT ---\n")
                f.write(m["content"])
                f.write("\n")
                break

if __name__ == "__main__":
    test_prompt()
