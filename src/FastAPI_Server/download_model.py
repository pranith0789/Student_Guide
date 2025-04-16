from sentence_transformers import SentenceTransformer

def download_model():
    print("Downloading all-MiniLM-L6-v2 model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model downloaded successfully!")

if __name__ == "__main__":
    download_model() 