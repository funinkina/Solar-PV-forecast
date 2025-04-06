from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from quartz_solar_forecast.forecast import run_forecast
from quartz_solar_forecast.pydantic_models import PVSite, ForecastRequest

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://solar-pv-forecast.vercel.app/",
]

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/forecast/")
def forecast(forecast_request: ForecastRequest):
    site = forecast_request.site
    ts = forecast_request.timestamp if forecast_request.timestamp else datetime.now(timezone.utc).isoformat()
    print(forecast_request)
    print(f"Forecast request received for site: {site}, timestamp: {ts}")

    timestamp = pd.Timestamp(ts).tz_localize(None)
    formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    site_no_live = PVSite(latitude=site.latitude, longitude=site.longitude, capacity_kwp=site.capacity_kwp)
    predictions_no_live = run_forecast(site=site_no_live, ts=timestamp)

    if not site.inverter_type:
        predictions = predictions_no_live
    else:
        predictions_with_live = run_forecast(site=site, ts=timestamp)
        predictions_with_live['power_kw_no_live_pv'] = predictions_no_live['power_kw']
        predictions = predictions_with_live

    response = {
        "timestamp": formatted_timestamp,
        "predictions": predictions.to_dict(),
    }

    return response
