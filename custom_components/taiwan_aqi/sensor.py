from homeassistant.components.sensor import SensorEntity
# 從 Home Assistant 的感測器組件中導入 SensorEntity 類別，這是所有感測器實體的基類。

from .const import DOMAIN
# 從當前套件 (taiwan_aqi) 的 const 模塊中導入 DOMAIN 常量，通常用於標識集成領域。

import logging
# 導入 Python 標準庫中的 logging 模塊，用於記錄日誌信息。

_LOGGER = logging.getLogger(__name__)
# 獲取一個日誌記錄器實例。__name__ 會是 'custom_components.taiwan_aqi.sensor'，這有助於區分不同模塊的日誌。

# 定義不同的感測器類型
# 這是一個註釋，說明接下來的字典將定義不同的空氣品質感測器類型。

SENSOR_TYPES = {
# 定義一個名為 SENSOR_TYPES 的字典，用於映射感測器類型的短名稱和其顯示名稱。
 "aqi": "AQI",
 # 鍵 "aqi" 對應值 "AQI"，表示空氣品質指標。
 "pm2.5": "PM2.5",
 # 鍵 "pm2.5" 對應值 "PM2.5"，表示細懸浮微粒。
 "pm10": "PM10",
 # 鍵 "pm10" 對應值 "PM10"，表示懸浮微粒。
 "o3": "O3",
 # 鍵 "o3" 對應值 "O3"，表示臭氧。
 "no2": "NO2",
 # 鍵 "no2" 對應值 "NO2"，表示二氧化氮。
 "so2": "SO2",
 # 鍵 "so2" 對應值 "SO2"，表示二氧化硫。
 "co": "CO"
 # 鍵 "co" 對應值 "CO"，表示一氧化碳。
}

DEVICE_CLASSES = {
# 定義一個名為 DEVICE_CLASSES 的字典，用於將感測器類型映射到 Home Assistant 預定義的設備類別。
 "aqi": "aqi", # 如果存在 device_class for AQI，否則可以不設置
 # 鍵 "aqi" 對應值 "aqi"。如果 Home Assistant 有 "aqi" 的設備類別，則使用它。
 "pm2.5": "pm25", # PM2.5 濃度
 # 鍵 "pm2.5" 對應值 "pm25"，代表 PM2.5 濃度。
 "pm10": "pm10", # PM10 濃度
 # 鍵 "pm10" 對應值 "pm10"，代表 PM10 濃度。
 "o3": "ozone", # 臭氧濃度
 # 鍵 "o3" 對應值 "ozone"，代表臭氧濃度。
 "no2": "nitrogen_dioxide", # 二氧化氮濃度
 # 鍵 "no2" 對應值 "nitrogen_dioxide"，代表二氧化氮濃度。
 "so2": "sulphur_dioxide", # 二氧化硫濃度
 # 鍵 "so2" 對應值 "sulphur_dioxide"，代表二氧化硫濃度。
 "co": "carbon_monoxide" # 一氧化碳濃度
 # 鍵 "co" 對應值 "carbon_monoxide"，代表一氧化碳濃度。
}

async def async_setup_entry(hass, config_entry, async_add_entities):
# 定義一個異步函數，用於設置 Home Assistant 的配置條目。
# hass: Home Assistant 核心實例。
# config_entry: 當前集成的配置條目。
# async_add_entities: 用於將感測器實體添加到 Home Assistant 的回調函數。

 """Set up Taiwan AQI sensors from a config entry."""
 # 函數的文檔字符串，說明此函數的功能是從配置條目設置台灣空氣品質感測器。

 coordinator = hass.data[DOMAIN][config_entry.entry_id]
 # 從 Home Assistant 的 hass.data 中獲取數據協調器實例。
 # hass.data[DOMAIN] 應該包含了所有屬於此集成領域的數據，然後通過 config_entry.entry_id 獲取特定配置條目的協調器。

 # 為每個定義的感測器類型建立對應的感測器
 # 註釋說明接下來的代碼將為 SENSOR_TYPES 中定義的每種類型創建一個感測器實體。

 entities = [AQISensor(coordinator, sensor_type) for sensor_type in SENSOR_TYPES]
 # 使用列表推導式創建 AQISensor 實體的列表。
 # 對於 SENSOR_TYPES 中的每一種感測器類型 (sensor_type)，都會創建一個新的 AQISensor 實例，並將協調器和感測器類型傳遞給它。

 async_add_entities(entities)
 # 調用 async_add_entities 回調函數，將創建的感測器實體列表添加到 Home Assistant。

class AQISensor(SensorEntity):
# 定義一個名為 AQISensor 的類，它繼承自 SensorEntity。這意味著它將作為 Home Assistant 中的一個感測器。

 """Representation of a Taiwan AQI sensor."""
 # 類的文檔字符串，說明此類代表一個台灣空氣品質感測器。

 def __init__(self, coordinator, sensor_type):
 # 類的初始化方法。
 # self: 實例本身。
 # coordinator: 數據協調器實例，用於獲取數據和處理更新。
 # sensor_type: 此感測器實體代表的具體空氣品質類型（例如 "pm2.5", "aqi"）。

 """Initialize the AQI sensor."""
 # 方法的文檔字符串，說明此方法用於初始化空氣品質感測器。

 self.coordinator = coordinator
 # 將傳入的協調器實例賦值給實例變量 self.coordinator。

 self.sensor_type = sensor_type
 # 將傳入的感測器類型賦值給實例變量 self.sensor_type。

 self._attr_name = f"{SENSOR_TYPES[sensor_type]} Sensor ({coordinator.config_entry.data['station']})"
 # 設置感測器的名稱。
 # 使用 f-string 格式化字符串，結合 SENSOR_TYPES 字典中的顯示名稱和協調器配置數據中的站點名稱。

 self._attr_unique_id = f"taiwan_aqi_{sensor_type}_{coordinator.config_entry.data['station']}"
 # 設置感測器的唯一 ID。
 # 唯一 ID 確保在 Home Assistant 中每個感測器都有一個獨特的標識符，通常由集成名稱、感測器類型和站點名稱組成。

 self._attr_device_class = DEVICE_CLASSES.get(sensor_type) # 設定 device_class
 # 設置感測器的設備類別。
 # 使用 DEVICE_CLASSES 字典的 .get() 方法來獲取對應 sensor_type 的設備類別。如果不存在，則返回 None。

 self._attr_state_class = "measurement" # 設定 state_class 為 measurement 以支持統計
 # 設置感測器的狀態類別為 "measurement"。
 # 這表明感測器的值是可測量的，並且 Home Assistant 可以為其提供歷史統計功能。

 @property
 # 裝飾器，將 state 方法轉換為一個屬性，可以像訪問變量一樣訪問它。
 def state(self):
 # 定義一個 state 屬性，用於返回感測器的當前狀態。

 """Return the state of the sensor."""
 # 屬性的文檔字符串，說明它返回感測器的狀態。

 if self.coordinator.data:
 # 檢查協調器是否有數據。如果為 True，表示數據已成功獲取。

 return self.coordinator.data.get(self.sensor_type)
 # 從協調器的數據中獲取當前感測器類型對應的值作為狀態。
 # 使用 .get() 方法可以避免在鍵不存在時引發 KeyError。

 return None
 # 如果協調器沒有數據，則返回 None。

 @property
 # 裝飾器，將 extra_state_attributes 方法轉換為一個屬性。
 def extra_state_attributes(self):
 # 定義一個 extra_state_attributes 屬性，用於返回感測器的額外狀態屬性。

 """Return extra state attributes."""
 # 屬性的文檔字符串，說明它返回額外的狀態屬性。

 if not self.coordinator.data:
 # 檢查協調器是否有數據。如果為 False，表示沒有數據。

 return {}
 # 如果沒有數據，則返回一個空字典作為額外屬性。

 return {
 # 如果有數據，則返回一個包含額外屬性的字典。
 "station": self.coordinator.config_entry.data["station"],
 # 包含站點名稱，從協調器的配置條目數據中獲取。
 "last_update": self.coordinator.data.get("publishtime")
 # 包含最後更新時間，從協調器的數據中獲取 "publishtime" 字段。
 }

 async def async_update(self):
 # 定義一個異步方法，用於請求從協調器更新數據。

 """Request an update from the coordinator."""
 # 方法的文檔字符串，說明它請求從協調器更新。

 await self.coordinator.async_request_refresh()
 # 調用協調器的 async_request_refresh 方法，觸發數據刷新。這是 Home Assistant 建議的從集成內部更新數據的方式。

 async def async_update_aqi_data(self):
 # 定義一個異步方法，作為一個服務處理器，用於手動更新 AQI 數據。

 """Service handler to update AQI data."""
 # 方法的文檔字符串，說明它是一個用於更新 AQI 數據的服務處理器。

 await self.async_update()
 # 調用自身的 async_update 方法來觸發數據更新。

 _LOGGER.info(f"AQI data manually updated for {self.coordinator.config_entry.data['station']}")
 # 使用日誌記錄器記錄一條信息，表示哪個站點的 AQI 數據已手動更新。
