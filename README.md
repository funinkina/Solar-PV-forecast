# Solar PV forecast

The aim of the project is to build an open source PV forecast that is free and easy to use.
The forecast provides the expected generation in `kw` for 0 to 48 hours for a single PV site.

## Installation

First create a virtual environment and install the dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate # On Windows use .venv\Scripts\activate
pip install -e .
```
## Usage
### Backend
```bash
python api/main.py
```
### Frontend
```bash
cd dashboards
npm install
npm run dev
```

## Model

Two models are currently available to make predictions.

**Gradient Boosting Model** (default)

The model uses GFS or ICON NWPs to predict the solar generation at a site.
It is a gradient boosted tree model and uses 9 NWP variables.
It is trained on 25,000 PV sites with over 5 years of PV history, which is available [here](https://huggingface.co/datasets/openclimatefix/uk_pv).
The training of this model is handled in [pv-site-prediction](https://github.com/openclimatefix/pv-site-prediction)
TODO - we need to benchmark this forecast.

The 9 NWP variables, from Open-Meteo documentation, are mentioned above with their appropariate units.

1. **Visibility (km)**, or vis: Distance at which objects can be clearly seen. Can affect the amount of sunlight reaching solar panels.
2. **Wind Speed at 10 meters (km/h)**, or si10 : Wind speed measured at a height of 10 meters above ground level. Important for understanding weather conditions and potential impacts on solar panels.
3. **Temperature at 2 meters (°C)**, or t : Air temperature measure at 2 meters above the ground. Can affect the efficiency of PV systems.
4. **Precipitation (mm)**, or prate : Precipitation (rain, snow, sleet, etc.). Helps to predict cloud cover and potentiel reductions in solar irradiance.
5. **Shortwave Radiation (W/m²)**, or dswrf: Solar radiation in the shortwave spectrum reaching the Earth's surface. Measure of the potential solar energy available for PV systems.
6. **Direct Radiation (W/m²)** or dlwrf: Longwave (infrared) radiation emitted by the Earth back into the atmosphere. **confirm it is correct**
7. **Cloud Cover low (%)**, or lcc: Percentage of the sky covered by clouds at low altitudes. Impacts the amount of solar radiation reachign the ground, and similarly the PV system.
8. **Cloud Cover mid (%)**, or mcc : Percentage of the sky covered by clouds at mid altitudes.
9. **Cloud Cover high (%)**, or lcc : Percentage of the sky covered by clouds at high altitude
   We also use the following features

- poa_global: The plane of array irradiance, which is the amount of solar radiation that strikes a solar panel.
- poa_global_now_is_zero: A boolean variable that is true if the poa_global is zero at the current time. This is used to help the model learn that the PV generation is zero at night.
- capacity (kw): The capacity of the PV system in kw.
- The model also has a feature to check if these variables are NaNs or not.
  The model also uses the following variables, which are currently all set to nan
- recent_power: The mean power over the last 30 minutes
- h_mean: The mean of the recent pv data over the last 7 days
- h_median: The median of the recent pv data over the last 7 days
- h_max: The max of the recent pv data over the last 7 days

**XGBoost**

The second option is an XGBoost model and uses the following Numerical Weather Predictions (NWP) input features achieved from [open-meteo](https://open-meteo.com/) variables. Different types of data is provided by open-meteo. To train this model hourly forecast data of [the historical weather API](https://open-meteo.com/en/docs/historical-weather-api) was used. The time period is restricted by the availabilty of the target solar enegery data of the panels and covers the time between 2018 and 2021. Additional information about the time, location and specifics about the panel are used. The weather features used are listed below, with the description given by open-meteo.

- Temperature at 2m (ºC): Air temperature at 2 meters above ground
- Relative Humidity at 2m (%): Relative humidity at 2 meters above ground
- Dewpoint at 2m (ºC): Dew point temperature at 2 meters above ground
- Precipitation (rain + snow) (mm): Total precipitation (rain, showers, snow) sum of the preceding hour
- Surface Pressure (hPa): Atmospheric air pressure reduced to mean sea level (msl) or pressure at surface. Typically pressure on mean sea level is used in meteorology. Surface pressure gets lower with increasing elevation.
- Cloud Cover Total (%): Total cloud cover as an area fraction
- Cloud Cover Low (%): Low level clouds and fog up to 3 km altitude
- Cloud Cover Mid (%): Mid level clouds from 3 to 8 km altitude
- Cloud Cover High (%): High level clouds from 8 km altitude
- Wind Speed at 10m (km/h): Wind speed at 10, 80, 120 or 180 meters above ground. Wind speed on 10 meters is the standard level.
- Wind Direction (10m): Wind direction at 10 meters above ground
- Is day or Night: 1 if the current time step has daylight, 0 at night
- Direct Solar Radiation (W/m2): Direct solar radiation as average of the preceding hour on the horizontal plane and the normal plane (perpendicular to the sun)
- Diffusive Solar Radiation DHI (W/m2): Diffuse solar radiation as average of the preceding hour

To use this model specify `model="xgb"` in `run_forecast(site=site, model="xgb", ts=datetime.today())`.

## Evaluation

**Gradient Boosting Model** (default)

To evaluate the model we use the [UK PV](https://huggingface.co/datasets/openclimatefix/uk_pv) dataset and the [ICON NWP](https://huggingface.co/datasets/openclimatefix/dwd-icon-eu) dataset.
All the data is publicly available and the evaluation script can be run with the following command

```bash
python scripts/run_evaluation.py
```

The test dataset we used is defined in `quartz_solar_forecast/dataset/testset.csv`.
This contains 50 PV sites, which 50 unique timestamps. The data is from 2021.

The results of the evaluation are as follows The MAE is 0.1906 kw across all horizons.

| Horizons | MAE [kw]      | MAE [%] |
| -------- | ------------- | ------- |
| 0        | 0.202 +- 0.03 | 6.2     |
| 1        | 0.211 +- 0.03 | 6.4     |
| 2        | 0.216 +- 0.03 | 6.5     |
| 3 - 4    | 0.211 +- 0.02 | 6.3     |
| 5 - 8    | 0.191 +- 0.01 | 6       |
| 9 - 16   | 0.161 +- 0.01 | 5       |
| 17 - 24  | 0.173 +- 0.01 | 5.3     |
| 24 - 48  | 0.201 +- 0.01 | 6.1     |

If we exclude nighttime, then the average MAE [%] from 0 to 36 forecast hours is 13.0%.

Notes:

- The MAE in % is the MAE divided by the capacity of the PV site. We acknowledge there are a number of different ways to do this.
- It is slightly surprising that the 0-hour forecast horizon and the 24-48 hour horizon have a similar MAE.
  This may be because the model is trained expecting live PV data, but currently in this project we provide no live PV data.

**XGBoost**

The model was trained and evaluated on 1147 solar panels and tested on 37 independent locations. An intensive hyperparameter tuning was performed. The model provides a feature importance list. Different metrics were calculated and analyzed. Finally the model was evaluated using the Mean Absolute Error (MAE). The MAE over the entire test data is $0.12$ kW, when the night times are excluded the MAE is $0.21$ kW. A plot with the MAE for each panel in the test set is shown in the figure below.

![MAE](images/mae_test.png)
_Mean absolute error for the panels in the test set._

Notes:

- The evaluation per horizon is not available for this model, as it is not provided by the open-meteo data.

## Development Environment Setup

To set up the development environment for this project, follow these steps:

1. **Clone the repository:**
  ```bash
  git clone https://github.com/openclimatefix/open-source-quartz-solar-forecast.git
  cd open-source-quartz-solar-forecast
  ```

2. **Create a virtual environment:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  ```

3. **Install the required dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

4. **Run the Jupyter Notebook server:**
  ```bash
  jupyter notebook
  ```

5. **Open your browser and navigate to:**
  ```bash
  http://localhost:8888
  ```

## Abbreviations

- NWP: Numerical Weather Predictions
- GFS: Global Forecast System
- PV: Photovoltaic
- MAE: Mean Absolute Error
- [ICON](https://www.dwd.de/EN/ourservices/nwp_forecast_data/nwp_forecast_data.html): ICOsahedral Nonhydrostatic
- KW: Kilowatt

## FOSDEM

FOSDEM is a free event for software developers to meet, share ideas and collaborate. Every year, thousands of developers of free and open source software from all over the world gather at the event in Brussels.
OCF presented Quartz Solar Forecast project at FOSDEM 2024. The link to the original FOSDEM video is availble at [Quartz Solar OS: Building an open source AI solar forecast for everyone](https://fosdem.org/2024/schedule/event/fosdem-2024-2960-quartz-solar-os-building-an-open-source-ai-solar-forecast-for-everyone/).
It is also available on [YouTube](https://www.youtube.com/watch?v=NAZ2VeiN1N8)

## Running the dashboard locally

Start the API first (port 8000):
`cd api`
`python main.py`

Start the frontend (port 5137):
`cd dashboards/dashboard_1`
`npm install`
`npm run dev`

## Global Model

Although this model is trained on UK data, this tool has been used in the following countries, (please let us know if you want your country to be added)

🇬🇧🇺🇸🇦🇺🇧🇦🇪🇸🇯🇵🇨🇳🇧🇪🇩🇪🇫🇷🇵🇹🇳🇱🇮🇳🇰🇷
