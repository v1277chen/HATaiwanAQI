import logging
# 導入 logging 模組，用於記錄日誌信息。

import voluptuous as vol
# 導入 voluptuous 模組並將其別名為 vol，這是一個用於數據驗證的庫。

from homeassistant import config_entries
# 從 homeassistant 導入 config_entries 模組，用於處理 Home Assistant 的配置流程。

from homeassistant.core import callback
# 從 homeassistant.core 導入 callback 裝飾器，用於標記異步回調函數。

from homeassistant.helpers.selector import (
# 從 homeassistant.helpers.selector 導入各種選擇器，用於在配置界面中顯示輸入字段。
    TextSelector,
    # 文本選擇器，用於普通文本輸入。
    TextSelectorConfig,
    # 文本選擇器的配置類。
    TextSelectorType,
    # 文本選擇器的類型（例如，TEXT）。
    SelectSelector,
    # 選擇選擇器，用於下拉菜單或多選框。
    SelectSelectorConfig,
    # 選擇選擇器的配置類。
    SelectSelectorMode,
    # 選擇選擇器的模式（例如，DROPDOWN, LIST, RADIOS）。
    SelectOptionDict,
    # 選擇選項的字典格式。
)

from .const import (
# 從當前包的 const 模組導入常量。
    DOMAIN,
    # 該集成（integration）的域名。
    CONF_API_KEY,
    # API 密鑰的配置鍵。
    CONF_SITEID,
    # 站點 ID 的配置鍵。
    SITEID_DICT,
    # 包含站點 ID 及其對應名稱的字典。
)

_LOGGER = logging.getLogger(__name__)
# 獲取當前模組的日誌記錄器實例，用於記錄程序運行時的信息。

TEXT_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))
# 創建一個文本選擇器實例，配置為普通的文本輸入類型。

SITE_SELECTOR = SelectSelector(
# 創建一個選擇選擇器實例。
    SelectSelectorConfig(
    # 配置選擇選擇器。
        options=[SelectOptionDict(value=str(v), label=k) for k, v in SITEID_DICT.items()],
        # 設置選項列表，每個選項是一個字典，包含 value（站點 ID）和 label（站點名稱）。
        # 將 value 轉換為字符串，因為 SelectOptionDict 可能需要字符串類型。
        mode=SelectSelectorMode.DROPDOWN,
        # 設置選擇模式為下拉菜單。
        custom_value=False,
        # 不允許用戶輸入自定義值。
        multiple=True
        # 允許用戶選擇多個選項。
    )
)


class TaiwanAQMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
# 定義 TaiwanAQMConfigFlow 類，繼承自 config_entries.ConfigFlow，負責 Home Assistant 的配置流程。
# domain=DOMAIN 將此配置流程與特定的集成域名關聯。
    """Handle a config flow for Taiwan AQM."""
    # 類文檔字符串，說明此類用於處理台灣空氣品質監測（Taiwan AQM）的配置流程。

    VERSION = 1
    # 定義配置流程的版本號。當配置流程的數據結構發生變化時，需要更新此版本號。

    @staticmethod
    # 靜態方法裝飾器，表示該方法不依賴於類的實例。
    @callback
    # 回調裝飾器，標記這是一個可以異步調用的回調函數。
    def async_get_options_flow(config_entry):
    # 靜態方法，用於返回選項流程的處理器。
        """Return the options flow handler."""
        # 方法文檔字符串，說明此方法返回選項流程的處理器。
        return TaiwanAQMOptionsFlow()
        # 返回 TaiwanAQMOptionsFlow 類的實例，該類將處理配置條目的選項。

    async def async_step_user(self, user_input=None):
    # 異步方法，處理用戶首次配置集成時的步驟。
    # user_input 參數包含用戶提交的表單數據。
        """Handle the initial configuration step."""
        # 方法文檔字符串，說明此方法處理初始配置步驟。
        errors = {}
        # 初始化一個空字典，用於存儲驗證錯誤信息。

        if self._async_current_entries():
        # 檢查是否已經存在當前集成的配置條目。
            return self.async_abort(reason="single_instance_allowed")
            # 如果已經存在，則中止配置流程，因為只允許單個實例。
        if self.hass.data.get(DOMAIN):
        # 檢查 Home Assistant 的數據中是否已存在此 DOMAIN 的數據（表示集成已加載）。
            return self.async_abort(reason="single_instance_allowed")
            # 如果已存在，則中止配置流程，因為只允許單個實例。

        if user_input is not None:
        # 如果用戶提交了表單數據。
            if not user_input[CONF_API_KEY]:
            # 如果 API 密鑰為空。
                errors["base"] = "no_api"
                # 在 errors 字典中添加一個錯誤，鍵為 "base"，值為 "no_api"。
            elif not user_input[CONF_SITEID]:
            # 如果站點 ID 為空。
                errors["base"] = "no_id"
                # 在 errors 字典中添加一個錯誤，鍵為 "base"，值為 "no_id"。
            else:
            # 如果 API 密鑰和站點 ID 都已提供。
                return self.async_create_entry(
                # 創建一個新的配置條目。
                    title="TWAQ Monitor",
                    # 配置條目的標題。
                    data=user_input,
                    # 配置條目中存儲的數據，即用戶輸入。
                )

        schema = vol.Schema(
        # 創建一個 voluptuous 模式 (schema) 來定義表單的結構和驗證規則。
            {
                vol.Required(CONF_API_KEY): TEXT_SELECTOR,
                # 必填字段 CONF_API_KEY，使用 TEXT_SELECTOR 顯示為文本輸入框。
                vol.Required(CONF_SITEID): SITE_SELECTOR
                # 必填字段 CONF_SITEID，使用 SITE_SELECTOR 顯示為下拉選擇框（多選）。
            }
        )

        return self.async_show_form(
        # 顯示配置表單給用戶。
            step_id="user",
            # 當前步驟的 ID。
            data_schema=schema,
            # 表單的數據模式。
            errors=errors,
            # 要顯示的錯誤信息。
        )


class TaiwanAQMOptionsFlow(config_entries.OptionsFlow):
# 定義 TaiwanAQMOptionsFlow 類，繼承自 config_entries.OptionsFlow，用於處理已配置集成的選項。
    """Handle Taiwan AQM options."""
    # 類文檔字符串，說明此類用於處理台灣空氣品質監測（Taiwan AQM）的選項。

    async def async_step_init(self, user_input=None):
    # 異步方法，處理選項流程的初始步驟。
    # user_input 參數包含用戶提交的表單數據。
        """Manage the options."""
        # 方法文檔字符串，說明此方法管理選項。
        errors = {}
        # 初始化一個空字典，用於存儲驗證錯誤信息。

        if user_input is not None:
        # 如果用戶提交了表單數據。
            if not user_input[CONF_API_KEY]:
            # 如果 API 密鑰為空。
                errors["base"] = "no_api"
                # 在 errors 字典中添加一個錯誤，鍵為 "base"，值為 "no_api"。
            elif not user_input[CONF_SITEID]:
            # 如果站點 ID 為空。
                errors["base"] = "no_id"
                # 在 errors 字典中添加一個錯誤，鍵為 "base"，值為 "no_id"。
            else:
            # 如果 API 密鑰和站點 ID 都已提供。
                # 更新選項
                self.hass.config_entries.async_update_entry(
                # 調用 Home Assistant 的配置條目管理器來更新現有的配置條目。
                    self.config_entry, data=user_input
                    # 指定要更新的 config_entry 和新的數據 user_input。
                )
                return self.async_create_entry(title=None, data=None)
                # 創建一個不帶標題和數據的空條目，表示選項已成功更新並關閉選項流程。

        old_apikey = self.config_entry.data.get(CONF_API_KEY)
        # 從現有的配置條目中獲取舊的 API 密鑰。
        old_siteid = self.config_entry.data.get(CONF_SITEID, [])
        # 從現有的配置條目中獲取舊的站點 ID，如果不存在則默認為空列表。

        schema = vol.Schema(
        # 創建一個 voluptuous 模式 (schema) 來定義選項表單的結構和驗證規則。
            {
                vol.Required(CONF_API_KEY, default=old_apikey): TEXT_SELECTOR,
                # 必填字段 CONF_API_KEY，默認為舊的 API 密鑰，使用 TEXT_SELECTOR 顯示。
                vol.Required(CONF_SITEID, default=old_siteid): SITE_SELECTOR
                # 必填字段 CONF_SITEID，默認為舊的站點 ID 列表，使用 SITE_SELECTOR 顯示。
            }
        )

        return self.async_show_form(
        # 顯示選項表單給用戶。
            step_id="init",
            # 當前步驟的 ID。
            data_schema=schema,
            # 表單的數據模式。
            errors=errors,
            # 要顯示的錯誤信息。
        )
