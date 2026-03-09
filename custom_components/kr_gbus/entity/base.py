"""kr_gbus 베이스 엔티티."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..coordinator import GBusDataUpdateCoordinator


class GBusEntity(CoordinatorEntity[GBusDataUpdateCoordinator]):
    """kr_gbus 엔티티 기본 클래스.

    CoordinatorEntity를 상속하면 coordinator가 데이터를 갱신할 때
    연결된 모든 엔티티에 자동으로 상태 갱신 알림이 전달된다.
    엔티티는 API를 직접 호출하지 않고 coordinator.data를 참조한다.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GBusDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=coordinator.config_entry.title,
        )
