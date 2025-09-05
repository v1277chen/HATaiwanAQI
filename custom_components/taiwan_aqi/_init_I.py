import logging
import requests
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service import async_register_admin_service
from .const import DOMAIN, API_URL, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Taiwan AQI from a config entry."""
    # 建立空氣品質資料感測器實體
    coordinator = AQICoordinator(hass, config_entry)
    
    # 初始化 hass.data 中DOMAIN的預設值，確保DOMAIN鍵存在
    hass.data.setdefault(DOMAIN, {})
    
    # 將協調器實例儲存到 hass.data 中，以便後續感測器可以訪問
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # 初始化感測器平台
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    # 註冊全局服務 'update_aqi_data'，讓所有感測器可以手動更新
    hass.services.async_register(DOMAIN, "update_aqi_data", service_update_aqi_data)

    # 立即取得最新資料
    await coordinator.async_refresh()

    return True

async def service_update_aqi_data(service_call):
    """Handle the service call to update AQI data for all entities."""
    # 記錄手動觸發更新的訊息
    _LOGGER.info("Manually triggering AQI data update for all sensors.")

    # 更新所有已註冊的感測器的數據 (此部分程式碼可能需要與感測器實作方式協調)
    entities = [] # 初始化一個空列表來存儲實體
    for entity in service_call.context: # 遍歷服務呼叫的上下文中的所有實體
        if isinstance(entity, AQISensor): # 檢查實體是否為 AQISensor 類型
            entities.append(entity) # 如果是，則將其添加到列表中
            
    for entity in entities: # 遍歷所有收集到的 AQISensor 實體
        await entity.async_update_aqi_data() # 呼叫每個實體的異步更新方法


class AQICoordinator(DataUpdateCoordinator):
    """Class to manage fetching AQI data from the API."""

    def __init__(self, hass, config_entry):
        """Initialize the AQI coordinator."""
        self.hass = hass # 儲存 HomeAssistant 實例
        self.config_entry = config_entry # 儲存配置入口
        super().__init__(
            hass, # HomeAssistant 實例
            _LOGGER, # 日誌記錄器
            name=DOMAIN, # 協調器名稱
            update_interval=timedelta(seconds=UPDATE_INTERVAL), # 設定資料更新間隔
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # 從配置入口獲取站點名稱和 API 金鑰
            station = self.config_entry.data["station"]
            api_key = self.config_entry.data["api_key"] # 使用 config_entry 中的 API Key
            
            # 在執行器中異步執行資料獲取，避免阻塞主線程
            response = await self.hass.async_add_executor_job(self._fetch_data, station, api_key)
            return response # 返回獲取的資料
        except Exception as err:
            # 捕獲並記錄錯誤
            _LOGGER.error(f"Error fetching AQI data for {station}: {err}")
            # 拋出更新失敗異常
            raise UpdateFailed(f"Failed to fetch data: {err}")

    def _fetch_data(self, station, api_key):
        """Fetch the AQI data from the API."""
        try:
            # 設定 API 請求參數
            params = {
                "language": "zh", # 設定語言為中文
                "api_key": api_key # 使用提供的 API 金鑰
            }
            # 發送 GET 請求到 API_URL
            response = requests.get(API_URL, params=params)
            # 檢查請求是否成功，如果失敗則拋出異常
            response.raise_for_status()
            # 將響應解析為 JSON 格式
            data = response.json()

            # 過濾出選定的測站資料
            for record in data["records"]: # 遍歷所有記錄
                if record["sitename"] == station: # 如果測站名稱匹配
                    # 確保數值是以數字形式處理，如果是文字，將其轉換為浮點數或整數
                    return {
                        "aqi": int(record.get("aqi", 0)), # 將 AQI 轉換為整數，預設值為 0
                        "pm2.5": float(record.get("pm2.5", 0)), # 將 PM2.5 轉換為浮點數，預設值為 0
                        "pm10": float(record.get("pm10", 0)), # 將 PM10 轉換為浮點數，預設值為 0
                        "o3": float(record.get("o3", 0)), # 將 O3 轉換為浮點數，預設值為 0
                        "no2": float(record.get("no2", 0)), # 將 NO2 轉換為浮點數，預設值為 0
                        "so2": float(record.get("so2", 0)), # 將 SO2 轉換為浮點數，預設值為 0
                        "co": float(record.get("co", 0)), # 將 CO 轉換為浮點數，預設值為 0
                        "publishtime": record.get("publishtime", "N/A") # 保留時間作為文字，預設值為 "N/A"
                    }
            return None # 如果沒有找到匹配的測站，則返回 None
        except Exception as e:
            # 捕獲並記錄資料獲取過程中的錯誤
            _LOGGER.error(f"Error while fetching data from API for station {station}: {e}")
            # 重新拋出異常
            raise
