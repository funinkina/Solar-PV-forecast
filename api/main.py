import uvicorn
import os

port = int(os.environ.get("PORT", 8000))                                                                                            

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
