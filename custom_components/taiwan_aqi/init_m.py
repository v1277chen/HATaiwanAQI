import logging # 導入 logging 模組，用於記錄日誌資訊

from copy import deepcopy # 從 copy 模組導入 deepcopy 函數，用於深度複製物件

from homeassistant.config_entries import ConfigEntry # 從 Home Assistant 導入 ConfigEntry 類，表示一個配置條目
from homeassistant.core import HomeAssistant, ServiceCall # 從 Home Assistant 導入 HomeAssistant 核心物件和 ServiceCall 類，用於服務呼叫
from homeassistant.helpers.typing import ConfigType # 從 Home Assistant 導入 ConfigType 類型提示
from homeassistant.helpers import config_validation as cv # 從 Home Assistant 導入 config_validation 模組，通常用於配置驗證，並將其別名為 cv
from homeassistant.helpers import entity_registry as er # 從 Home Assistant 導入 entity_registry 模組，用於管理實體註冊
from homeassistant.helpers import device_registry as dr # 從 Home Assistant 導入 device_registry 模組，用於管理設備註冊
from homeassistant.helpers.event import async_track_time_change # 從 Home Assistant 導入 async_track_time_change 函數，用於跟蹤時間變化事件

from .coordinator import AQMCoordinator # 從當前包導入 AQMCoordinator 類，負責資料協調
from .const import ( # 從當前包導入 const 模組中的常量
    DOMAIN, # 領域名稱，通常是整合的唯一識別碼
    CONF_SITEID, # 配置中用於站點ID的鍵
    COORDINATOR, # 協調器物件的鍵
    SITEID, # 站點ID的鍵
    TASK, # 定時任務的鍵
    PLATFORM, # 平台名稱，例如 'sensor'
    UPDATE_INTERVAL, # 更新間隔時間
)

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=True) # 定義配置 schema，這裡表示舊的配置方式已被移除，如果存在則會拋出錯誤
_LOGGER = logging.getLogger(__name__) # 獲取一個日誌記錄器實例，用於記錄此模組的日誌

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up global services for Taiwan AQM .""" # 設定台灣空氣品質監測的全局服務
    return True # 返回 True 表示設定成功

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Taiwan AQM from a config entry.""" # 從配置條目設定台灣空氣品質監測
    try:
        hass.data.setdefault(DOMAIN, {}) # 如果 hass.data 中沒有 DOMAIN 鍵，則設定為一個空字典
        # 創建 AQMCoordinator 實例，負責獲取和協調空氣品質資料
        coordinator = AQMCoordinator(hass, entry, UPDATE_INTERVAL)

        async def refresh_task(*args):
            """定義一個非同步刷新任務"""
            await coordinator.async_refresh() # 呼叫協調器進行資料刷新
            _LOGGER.debug(
                f"Refresh Success at: {args[0].strftime('%Y-%m-%d %H:%M:%S %Z')}" # 記錄刷新成功的日誌，包含時間
            )

        # 設定一個每10分鐘執行的定時任務，呼叫 refresh_task
        task = async_track_time_change(hass, refresh_task, minute=10, second=0)
        # 將協調器、站點ID和定時任務儲存到 hass.data 中，以便後續存取
        hass.data[DOMAIN][entry.entry_id] = {
            COORDINATOR: coordinator,
            SITEID: entry.data.get(CONF_SITEID),
            TASK: task,
        }
        # 執行協調器的首次資料刷新
        await coordinator.async_config_entry_first_refresh()
        # 初始化感測器平台
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORM)

        # 當配置條目更新時，註冊 update_listener 函數
        entry.async_on_unload(entry.add_update_listener(update_listener))

        return True # 返回 True 表示設定成功
    except Exception as e:
        _LOGGER.error(f"async_setup_entry error: {e}") # 記錄錯誤日誌
        return False # 返回 False 表示設定失敗

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener.""" # 更新監聽器
    try:
        # 當配置條目更新時，重新載入該配置條目
        await hass.config_entries.async_reload(entry.entry_id)
    except Exception as e:
        _LOGGER.error(f"update_listener error: {e}") # 記錄錯誤日誌

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.""" # 卸載一個配置條目
    try:
        # 獲取並取消定時任務
        task = hass.data[DOMAIN][entry.entry_id].get(TASK)
        task()
        # 卸載平台（例如，感測器平台）
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry, PLATFORM
        )

        if unload_ok:
            # 獲取舊的站點ID和新的站點ID
            old_siteid = hass.data[DOMAIN][entry.entry_id].get(SITEID, [])
            new_siteid = entry.data.get(CONF_SITEID, [])
            # 計算需要移除的設備識別符
            del_dev_identifiers = {
                (DOMAIN, id)
                for id in old_siteid if id not in new_siteid
            }
            _LOGGER.debug(f"remove dev_identifiers: {del_dev_identifiers}") # 記錄要移除的設備識別符
            if del_dev_identifiers:
                # 獲取設備註冊表
                dev_reg = dr.async_get(hass)
                # 篩選出需要移除的設備
                devices = [
                    device for device in
                    dr.async_entries_for_config_entry(dev_reg, entry.entry_id)
                    if device.identifiers & del_dev_identifiers
                ]
                # 移除設備
                for dev in devices:
                    dev_reg.async_remove_device(dev.id)
                    _LOGGER.debug(f"removed device: {dev.id}") # 記錄已移除的設備

            # 從 hass.data 中移除當前配置條目的資料
            hass.data[DOMAIN].pop(entry.entry_id)
            # 如果 DOMAIN 下沒有其他配置條目了，則移除 DOMAIN 鍵
            if DOMAIN in hass.data and not hass.data[DOMAIN]:
                hass.data.pop(DOMAIN)

            return True # 返回 True 表示卸載成功
        else:
            return False # 返回 False 表示卸載失敗
    except Exception as e:
        _LOGGER.error(f"async_unload_entry error: {e}") # 記錄錯誤日誌
        return False # 返回 False 表示卸載失敗

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry.""" # 重新載入配置條目
    # 呼叫 Home Assistant 的配置條目重新載入功能
    await hass.config_entries.async_reload(entry.entry_id)

# async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
# """Migrate config entry.""" # 遷移配置條目
# if entry.version > 2:
# # 未來版本無法處理
# return False
#
# if entry.version < 2:
# # 舊版本更新資料
# data = deepcopy(dict(entry.data))
#
# hass.config_entries.async_update_entry(entry, version=2, data=data)
# return True
