from typing import Callable
import pandas as pd
from datetime import datetime, timedelta
from quartz_solar_forecast.inverters.inverter import AbstractInverter
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from ocf_vrmapi.vrm import VRM_API
except ImportError:
    VRM_API = None
    print("Warning: Failed to import ocf_vrmapi. Victron Inverter functions will not work.")

class VictronSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    username: str = Field(alias="VICTRON_USER")
    password: str = Field(alias="VICTRON_PASS")


class VictronInverter(AbstractInverter):

    def __init__(self, get_sites: Callable, get_kwh_stats: Callable):
        self.__get_sites = get_sites
        self.__get_kwh_stats = get_kwh_stats

    @classmethod
    def from_settings(cls, settings: VictronSettings):
        if VRM_API is None:
            raise ImportError("VRM_API is not available. Ensure ocf_vrmapi is installed.")

        try:
            api = VRM_API(username=settings.username, password=settings.password)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize VRM_API: {e}")

        get_sites = lambda: api.get_user_sites(api.user_id)
        end = datetime.now()
        start = end - timedelta(weeks=1)
        get_kwh_stats = lambda site_id: api.get_kwh_stats(site_id, start=start, end=end)

        return cls(get_sites, get_kwh_stats)

    def get_data(self, ts: pd.Timestamp) -> pd.DataFrame:
        try:
            sites = self.__get_sites()
            if not sites or "records" not in sites or not sites["records"]:
                raise ValueError("No sites found in the response from get_sites.")

            # Get the first site (assuming it's the primary site)
            first_site_id = sites["records"][0].get("idSite")
            if not first_site_id:
                raise ValueError("Site ID not found in the site records.")

            stats = self.__get_kwh_stats(first_site_id)
            if not stats or "records" not in stats or "kwh" not in stats["records"]:
                raise ValueError("No kWh stats found in the response from get_kwh_stats.")

            kwh = stats["records"]["kwh"]
            df = pd.DataFrame(kwh)

            # Ensure the DataFrame has the expected structure
            if df.shape[1] < 2:
                raise ValueError("Unexpected data format in kWh stats.")

            df[0] = pd.to_datetime(df[0], unit='ms')
            df.columns = ["timestamp", "power_kw"]
            return df

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve data: {e}")