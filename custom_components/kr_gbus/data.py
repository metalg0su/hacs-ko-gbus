"""kr_gbus 런타임 데이터 타입."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .api import BusArrivalApiClient, BusRouteApiClient
from .coordinator import GBusDataUpdateCoordinator

type GBusConfigEntry = ConfigEntry[GBusData]


@dataclass
class GBusData:
    """설정 항목의 런타임 데이터."""

    arrival: BusArrivalApiClient
    route: BusRouteApiClient
    coordinator: GBusDataUpdateCoordinator
