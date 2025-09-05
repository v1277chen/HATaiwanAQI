from __future__ import annotations # 啟用未來版本的特性，例如在型別提示中使用 `list[str]` 而不是 `typing.List[str]`。

import logging # 導入 logging 模組，用於記錄程式運行時的資訊、警告或錯誤。

from homeassistant.components.sensor import RestoreSensor # 從 Home Assistant 的感測器組件導入 RestoreSensor，這允許感測器在 Home Assistant 重啟後恢復其上次的狀態。
from homeassistant.helpers.update_coordinator import CoordinatorEntity # 從 Home Assistant 的更新協調器助手導入 CoordinatorEntity，這是一個實體基礎類別，它使用協調器來管理數據更新。

from .const import ( # 從當前套件的 const.py 檔案中導入常數。
    DOMAIN, # 整合的領域名稱，通常是整合的唯一識別符。
    SITENAME_DICT, # 站點名稱字典，用於將站點 ID 對應到其名稱。
    SENSOR_INFO, # 感測器資訊字典，包含不同空氣品質類型（如 PM2.5, AQI）的配置。
    CONF_SITEID, # 配置中用於站點 ID 的鍵。
    COORDINATOR, # 配置中用於協調器實例的鍵。
)

_LOGGER = logging.getLogger(__name__) # 獲取一個 logger 實例，用於在此模組中記錄訊息。

async def async_setup_entry(hass, entry, async_add_entities): # 非同步函式，用於從配置條目設定台灣空氣品質監測感測器。
    """Set up Taiwan aqi sensors from a config entry.""" # 函式的說明字串。
    try: # 嘗試執行以下程式碼。
        siteid = entry.data.get(CONF_SITEID) # 從配置條目中獲取站點 ID。
        coordinator = hass.data[DOMAIN][entry.entry_id].get(COORDINATOR) # 從 Home Assistant 的數據中獲取此配置條目的協調器實例。

        entities = [ # 創建感測器實體列表。
            aqiSensor( # 為每個站點和每個感測器類型創建一個 aqiSensor 實例。
                coordinator=coordinator, # 傳遞數據更新協調器。
                siteid=s_id, # 傳遞站點 ID。
                sitename=SITENAME_DICT[s_id], # 傳遞站點名稱。
                aq_type=aq_type, # 傳遞空氣品質類型（如 "pm25"）。
                device_class=config["dc"], # 傳遞設備類別（device_class），用於 Home Assistant 的顯示和自動化。
                unit_of_measurement=config["unit"], # 傳遞測量單位。
                state_class=config["sc"], # 傳遞狀態類別（state_class），例如 "measurement" 或 "total"，用於歷史數據圖表。
                display_precision=config["dp"], # 傳遞顯示精度（小數點後位數）。
                icon=config["icon"] # 傳遞感測器圖標。
            ) for s_id in siteid # 遍歷所有配置的站點 ID。
            for aq_type, config in SENSOR_INFO.items() # 遍歷 SENSOR_INFO 中定義的每個空氣品質類型及其配置。
        ]
        async_add_entities(entities) # 將創建的感測器實體添加到 Home Assistant。
    except Exception as e: # 捕獲任何可能發生的異常。
        _LOGGER.error(f"setup sensor error: {e}") # 記錄錯誤訊息。

class aqiSensor(CoordinatorEntity, RestoreSensor): # 定義 aqiSensor 類別，繼承自 CoordinatorEntity 和 RestoreSensor。
    """Representation of a Taiwan aqi sensor.""" # 類別的說明字串。

    def __init__( # aqiSensor 類的初始化方法。
        self, # 實例本身。
        coordinator, # 數據更新協調器。
        siteid, # 站點 ID。
        sitename, # 站點名稱。
        aq_type, # 空氣品質類型。
        device_class, # 設備類別。
        unit_of_measurement=None, # 測量單位，可選。
        state_class=None, # 狀態類別，可選。
        display_precision=None, # 顯示精度，可選。
        icon=None, # 圖標，可選。
    ):
        """Initialize the AQI sensor.""" # 初始化方法的說明字串。
        super().__init__(coordinator) # 調用父類 CoordinatorEntity 的初始化方法，傳遞協調器。
        self.siteid = siteid # 設置站點 ID。
        self._sitename = sitename # 設置站點名稱（內部使用）。
        self._type = aq_type # 設置空氣品質類型（內部使用）。
        self._device_class = device_class # 設置設備類別（內部使用）。
        self._unit_of_measurement = unit_of_measurement # 設置測量單位（內部使用）。
        self._state_class = state_class # 設置狀態類別（內部使用）。
        self._display_precision = display_precision # 設置顯示精度（內部使用）。
        self._icon = icon # 設置圖標（內部使用）。
        self._last_value = None # 初始化 _last_value 為 None，用於存儲上次的值。
        _LOGGER.debug(f"Initialized TaiwanaqiEntity for siteid: {self.siteid}, type: {self._type}") # 記錄調試訊息，表示實體已初始化。

    async def async_added_to_hass(self): # 當實體被添加到 Home Assistant 時調用的非同步方法。
        """Get the old value""" # 函式的說明字串，用於獲取舊值。
        await super().async_added_to_hass() # 調用父類的方法。

        if (last_sensor_data := await self.async_get_last_sensor_data()) \
            and last_sensor_data.native_value is not None \
            and self._device_class is not None:
            # 如果存在上次的感測器數據，且其原生值不為 None，且設備類別已定義。
            self._last_value = last_sensor_data.native_value # 將上次的感測器原生值存儲到 _last_value。

    @property # 裝飾器，將方法轉換為屬性，使其可以像訪問變數一樣訪問。
    def _data(self): # 獲取協調器數據的屬性。
        return self.coordinator.data # 返回協調器中存儲的數據。

    @property # 裝飾器，將方法轉換為屬性。
    def device_info(self): # 返回設備資訊的屬性，用於 Home Assistant 中顯示設備。
        return { # 返回一個字典，包含設備的識別資訊。
            "identifiers": {(DOMAIN, self.siteid)}, # 設備的唯一識別符，由領域和站點 ID 組成。
            "name": f"TWAQ Monitor - {self._sitename}({self.siteid})", # 設備的名稱。
            "manufacturer": "Taiwan Ministry of Environment Data Open Platform", # 製造商資訊。
            "model": "Taiwanaqi", # 型號資訊。
        }

    @property # 裝飾器，將方法轉換為屬性。
    def native_value(self): # 返回感測器當前原生值的屬性。
        if self._is_valid_data() and self.coordinator.last_update_success: # 如果數據有效且上次更新成功。
            self._last_value = self._data[self.siteid].get(self._type) # 從數據中獲取當前站點和類型的空氣品質值，並更新 _last_value。
            return self._last_value # 返回獲取到的值。
        else: # 如果數據無效或更新失敗。
            return "unknown" if self._device_class is None else 0 # 如果設備類別為 None 則返回 "unknown"，否則返回 0。

    @property # 裝飾器，將方法轉換為屬性。
    def device_class(self): # 返回設備類別的屬性。
        return self._device_class # 設備類型。

    @property # 裝飾器，將方法轉換為屬性。
    def native_unit_of_measurement(self): # 返回原生測量單位的屬性。
        return self._unit_of_measurement # 預設單位。

    @property # 裝飾器，將方法轉換為屬性。
    def state_class(self): # 返回狀態類別的屬性。
        return self._state_class # 圖表類型。

    @property # 裝飾器，將方法轉換為屬性。
    def suggested_display_precision(self): # 返回建議顯示精度的屬性。
        return self._display_precision

    @property # 裝飾器，將方法轉換為屬性。
    def extra_state_attributes(self): # 返回額外狀態屬性的屬性。
        if self._data and self.siteid in self._data: # 如果有數據且站點 ID 在數據中。
            lon = self._data[self.siteid].get("longitude", "unknown") # 獲取經度，如果沒有則為 "unknown"。
            lat = self._data[self.siteid].get("latitude", "unknown") # 獲取緯度，如果沒有則為 "unknown"。
        else: # 如果沒有數據或站點 ID 不在數據中。
            lon = "unknown" # 經度設為 "unknown"。
            lat = "unknown" # 緯度設為 "unknown"。

        return { # 返回包含額外屬性的字典。
            "sitename": self._sitename, # 站點名稱。
            "siteid": self.siteid, # 站點 ID。
            "longitude": lon, # 經度。
            "latitude": lat, # 緯度。
        }

    @property # 裝飾器，將方法轉換為屬性。
    def available(self): # 返回感測器是否可用的屬性。
        return self.siteid in self._data # 如果站點 ID 在數據中則返回 True，表示可用。

    @property # 裝飾器，將方法轉換為屬性。
    def name(self): # 返回感測器名稱的屬性。
        _type = self._type.replace("_", " ") if self._type else "unknown" # 將空氣品質類型中的下劃線替換為空格，如果沒有則為 "unknown"。
        return f"{self._sitename} {_type}" # 返回格式化的感測器名稱（站點名稱 + 空氣品質類型）。

    @property # 裝飾器，將方法轉換為屬性。
    def has_entity_name(self): # 返回是否使用實體名稱的屬性。
        return False # 返回 False，表示實體名稱由 `name` 屬性提供，而不是基於設備名稱自動生成。

    @property # 裝飾器，將方法轉換為屬性。
    def unique_id(self): # 返回感測器唯一 ID 的屬性。
        sanitized_name = self._type.replace(" ", "_") if self._type else "unknown" # 將空氣品質類型中的空格替換為下劃線，如果沒有則為 "unknown"。
        return f"{DOMAIN}_{self.siteid}_{sanitized_name}" # 返回格式化的唯一 ID。

    @property # 裝飾器，將方法轉換為屬性。
    def icon(self): # 返回感測器圖標的屬性。
        return self._icon # 返回在初始化時設置的圖標。

    def _is_valid_data(self) -> bool: # 內部方法，用於驗證數據的完整性。
        """Validate the integrity of the data.""" # 函式的說明字串。
        if not self._data: # 如果沒有數據。
            _LOGGER.error("No data available") # 記錄錯誤訊息。
            return False # 返回 False。

        if self.siteid not in self._data: # 如果站點 ID 不在數據中。
            _LOGGER.warning(f"The site ID '{self.siteid}' is not in the data: {self._data.keys()}") # 記錄警告訊息。
            return False # 返回 False。

        if (value := self._data[self.siteid].get(self._type)) in [None, ""]: # 如果特定站點和類型的數據值為 None 或空字符串。
            if value is None: # 如果值為 None。
                _LOGGER.debug(f"The value for '{self._type}' in siteID '{self.siteid}' is missing or None.") # 記錄調試訊息。
            elif value == "": # 如果值為空字符串。
                _LOGGER.debug(f"The value for '{self._type}' in siteID '{self.siteid}' is empy") # 記錄調試訊息。
            return False # 返回 False。

        _LOGGER.debug(f"Valid data found for site '{self.siteid}' and type '{self._type}': {value}") # 記錄調試訊息，表示找到有效數據。
        return True # 返回 True，表示數據有效。 [1]
