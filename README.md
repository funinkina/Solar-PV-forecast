# Quartz Solar Forecast

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-34-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

![image](https://github.com/user-attachments/assets/6563849b-b355-4842-93e4-61c15a9a9ebf)
[![tags badge](https://img.shields.io/github/v/tag/openclimatefix/open-source-quartz-solar-forecast?include_prereleases&sort=semver&color=FFAC5F)](https://github.com/openclimatefix/open-source-quartz-solar-forecast/tags)
[![pypi badge](https://img.shields.io/pypi/v/quartz-solar-forecast?&color=07BCDF)](https://pypi.org/project/quartz-solar-forecast/)
[![ease of contribution: easy](https://img.shields.io/badge/ease%20of%20contribution:%20easy-32bd50)](https://github.com/openclimatefix/ocf-meta-repo?tab=readme-ov-file#overview-of-ocfs-nowcasting-repositories) 
[![Python package tests](https://github.com/openclimatefix/open-source-quartz-solar-forecast/actions/workflows/pytest.yaml/badge.svg)](https://github.com/openclimatefix/open-source-quartz-solar-forecast/actions/workflows/pytest.yaml)


The aim of the project is to build an open source PV forecast that is free and easy to use.
The forecast provides the expected generation in `kw` for 0 to 48 hours for a single PV site.

Open Climate Fix also provides a commercial PV forecast, please get in touch at quartz.support@openclimatefix.org

Want to learn more about the project? We've presented Quartz Solar Forecast at two open source conferences:

- **FOSDEM 2024** (Free and Open source Software Developers' European Meeting): How we built Open Quartz, our motivation behind it and its impact on aiding organizations in resource optimization [Watch the talk](https://www.youtube.com/watch?v=NAZ2VeiN1N8)

- **LF Energy 2024**: Exploring Open Quartz's developments - new models, inverter APIs, and our Open Source journey at Open Climate Fix [Watch the talk](https://www.youtube.com/watch?v=YTaq41ztEDg)


The current model uses GFS or ICON NWPs to predict the solar generation at a site

```python
from quartz_solar_forecast.forecast import run_forecast
from quartz_solar_forecast.pydantic_models import PVSite
from datetime import datetime

# make a pv site object
site = PVSite(latitude=51.75, longitude=-1.25, capacity_kwp=1.25)

# run model for today, using ICON NWP data
predictions_df = run_forecast(site=site, ts=datetime.today(), nwp_source="icon")
```

which should result in a time series similar to this one:

![https://github.com/openclimatefix/Open-Source-Quartz-Solar-Forecast/blob/main/predictions.png?raw=true](https://github.com/openclimatefix/Open-Source-Quartz-Solar-Forecast/blob/main/predictions.png?raw=true)

A colab notebook providing some examples can be found [here](https://colab.research.google.com/drive/1qKDFRpq4Hk-LHgWuDsz_Najc3Zq-GVNY?usp=sharing).

## Generating Forecasts

To generate solar forecasts and save them into a CSV file, follow these steps:

- Run the forecast_csv.py script with desired inputs

```bash
python scripts/forecast_csv.py
```

Replace the --init_time_freq, --start_datetime, --end_datetime, and --site_name with your desired forecast initialization frequency (in hours), start datetime, end datetime, and the name of the forecast or site, respectively.

Output

The script will generate solar forecasts at the specified intervals between the start and end datetimes. The results will be combined into a CSV file named using the site name, start and end datetimes, and the frequency of forecasts. This file will be saved in the scripts/csv_forecasts directory.

## Installation

The source code is currently hosted on GitHub at: https://github.com/openclimatefix/Open-Source-Quartz-Solar-Forecast

Binary installers for the latest released version are available at the Python Package Index (PyPI)

```bash
pip install quartz-solar-forecast
```

You might need to install the following packages first

```bash
conda install -c conda-forge pyresample
```

This can solve the [bug: \_\_\_kmpc_for_static_fini](https://github.com/openclimatefix/Open-Source-Quartz-Solar-Forecast/issues/32).

### Logging

The package logs when `run_forecast` is used. This is useful for OCF to determine how the package is being used 
and how we can make improvements in the future.
Note that any latitudes and longitudes are rounded to 2 decimals places in order to anonymize the data.
If you would like to disable this logging, you can do so by setting the environment variable `QUARTZ_SOLAR_FORECAST_LOGGING` to `False`.


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

## Model Comparisons

The following plot shows example predictions of both models for the same time period. Additionally for the Gradient Boosting model (default) the results from the two different data sources are shown.

![model comparison](images/model_data_comparison_hr.png)
_Predictions using the two different models and different data sources._

## Known restrictions

- The model is trained on [UK MetOffice](https://www.metoffice.gov.uk/services/data/met-office-weather-datahub) NWPs, but when running inference we use [GFS](https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast) data from [Open-meteo](https://open-meteo.com/). The differences between GFS and UK MetOffice could led to some odd behaviours.
- Depending, whether the timestamp for the prediction lays more than 90 days in the past or not, different data sources for the NWP are used. If we predict within the last 90 days, we can use ICON or GFS from the open-meteo Weather Forecast API. Since ICON doesn't provide visibility, this parameter is queried from GFS in any case. If the date for the prediction is further back in time, a reanalysis model of historical data is used (open-meteo | Historical Weather API). The historical weather API doesn't provide visibility at all, that's why it's set to a maximum of 24000 meter in this case. This can lead to some loss of precision.
- The model was trained and tested only over the UK, applying it to other geographical regions should be done with caution.
- When using the XGBoost model, only hourly predictions within the last 90 days are available for data consistency.

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
