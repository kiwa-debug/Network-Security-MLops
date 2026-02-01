import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")

import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.utils.ml_utils.model.estimator import NetworkModel


# Initialize MongoDB client as None
client = None
database = None
collection = None

# Try to connect to MongoDB if URL is provided
if mongo_db_url:
    try:
        print(f"Attempting MongoDB connection...")
        client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB connection successful!")
        
        from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
        from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME
        
        database = client[DATA_INGESTION_DATABASE_NAME]
        collection = database[DATA_INGESTION_COLLECTION_NAME]
    except Exception as e:
        print(f"⚠ MongoDB connection failed: {e}")
        print("⚠ Continuing without MongoDB - training features will be disabled")
        client = None
        database = None
        collection = None
else:
    print("⚠ MONGODB_URL_KEY not set - running without MongoDB")
    print("⚠ Training features will be disabled")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        if not client:
            return Response("Training disabled: MongoDB connection not available. Please configure MONGODB_URL_KEY.", status_code=503)
        
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        #print(df)
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8080)
