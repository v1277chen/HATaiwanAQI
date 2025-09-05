# 導入 datetime 模組，用於處理日期和時間，特別是時間間隔。
from datetime import timedelta 
# 從 homeassistant.const 模組導入 Platform，表示 Home Assistant 中的平台類型。
from homeassistant.const import Platform
# 從 homeassistant.components.sensor 模組導入 SensorDeviceClass 和 SensorStateClass。
# SensorDeviceClass 用於定義感測器的設備類別 (例如：AQI, CO)。
# SensorStateClass 用於定義感測器狀態的類別 (例如：測量值)。
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

# 定義 Home Assistant 整合的領域名稱。
DOMAIN = "taiwan_aqi" 
# 配置項：API 金鑰的名稱。
CONF_API_KEY = "api_key" 
# 配置項：站點 ID 的名稱。
CONF_SITEID = "siteID" 
# 協調器名稱，用於資料更新的協調器。
COORDINATOR = "COORDINATOR" 
# 站點 ID 的變數名。
SITEID = "SITEID" 
# 定時任務的變數名。
TASK = "TIMER_TASK" 
# 台灣環境部空氣品質監測資料的 API URL。
API_URL = "https://data.moenv.gov.tw/api/v2/aqx_p_432" 
# Home Assistant 請求時使用的 User-Agent 字串，用於識別客戶端。
HA_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HomeAssistant/HA-Taiwanaqi" 
# 資料更新間隔設定為 11 分鐘。
UPDATE_INTERVAL = timedelta(minutes=11) 
# 此整合支援的平台列表，這裡指定為感測器 (Platform.SENSOR)。
PLATFORM = [Platform.SENSOR] 

# 台灣空氣品質監測站點 ID 的字典，鍵是站點名稱 (中文)，值是對應的站點 ID (字串)。
SITEID_DICT = { 
    "基隆市基隆": "1",
    "新北市汐止": "2",
    "新北市新店": "4",
    "新北市土城": "5",
    "新北市板橋": "6",
    "新北市新莊": "7",
    "新北市菜寮": "8",
    "新北市林口": "9",
    "新北市淡水": "10",
    "新北市三重": "67",
    "新北市永和": "70",
    "新北市富貴角": "84",
    "新北市樹林": "311",
    "臺北市士林": "11",
    "臺北市中山": "12",
    "臺北市萬華": "13",
    "臺北市古亭": "14",
    "臺北市松山": "15",
    "臺北市大同": "16",
    "臺北市陽明": "64",
    "桃園市桃園": "17",
    "桃園市大園": "18",
    "桃園市觀音": "19",
    "桃園市平鎮": "20",
    "桃園市龍潭": "21",
    "桃園市中壢": "68",
    "新竹市新竹": "24",
    "新竹縣湖口": "22",
    "新竹縣竹東": "23",
    "苗栗縣頭份": "25",
    "苗栗縣苗栗": "26",
    "苗栗縣三義": "27",
    "臺中市豐原": "28",
    "臺中市沙鹿": "29",
    "臺中市大里": "30",
    "臺中市忠明": "31",
    "臺中市西屯": "32",
    "臺中市和平區消防隊": "310",
    "彰化縣彰化": "33",
    "彰化縣線西": "34",
    "彰化縣二林": "35",
    "彰化縣大城": "85",
    "彰化縣員林": "139",
    "南投縣南投": "36",
    "南投縣竹山": "69",
    "南投縣埔里": "72",
    "南投縣鹿谷": "203",
    "雲林縣斗六": "37",
    "雲林縣崙背": "38",
    "雲林縣臺西": "41",
    "雲林縣麥寮": "83",
    "嘉義市嘉義": "42",
    "嘉義縣新港": "39",
    "嘉義縣朴子": "40",
    "臺南市新營": "43",
    "臺南市善化": "44",
    "臺南市安南": "45",
    "臺南市臺南": "46",
    "臺南市南化": "312",
    "高雄市美濃": "47",
    "高雄市橋頭": "48",
    "高雄市仁武": "49",
    "高雄市鳳山": "50",
    "高雄市大寮": "51",
    "高雄市林園": "52",
    "高雄市楠梓": "53",
    "高雄市左營": "54",
    "高雄市前金": "56",
    "高雄市前鎮": "57",
    "高雄市小港": "58",
    "高雄市復興": "71",
    "高雄市湖內": "202",
    "屏東縣屏東": "59",
    "屏東縣枋山": "313",
    "屏東縣潮州": "60",
    "屏東縣恆春": "61",
    "屏東縣琉球": "204",
    "宜蘭縣宜蘭": "65",
    "宜蘭縣冬山": "66",
    "宜蘭縣頭城": "201",
    "花蓮縣花蓮": "63",
    "臺東縣臺東": "62",
    "臺東縣關山": "80",
    "澎湖縣馬公": "78",
    "金門縣金門": "77",
    "連江縣馬祖": "75",
}

# 根據 SITEID_DICT 建立一個反向字典，鍵是站點 ID，值是站點名稱。
SITENAME_DICT = {v: k for k, v in SITEID_DICT.items()} 

# 定義感測器資訊的字典，包含各種空氣品質指標的屬性。
SENSOR_INFO = { 
    "aqi": { # 空氣品質指標 (AQI)
        "dc": SensorDeviceClass.AQI, # 設備類別：AQI
        "unit": None, # 單位：無 (AQI 值本身就是一個指數)
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無 (使用預設或 Home Assistant 自動生成)
    },
    "pollutant": { # 主要污染物
        "dc": None, # 設備類別：無
        "unit": None, # 單位：無
        "sc": None, # 狀態類別：無
        "dp": None, # 小數位數：無
        "icon": "mdi:smog", # 圖標：煙霧
    },
    "status": { # 空氣品質狀態描述
        "dc": None, # 設備類別：無
        "unit": None, # 單位：無
        "sc": None, # 狀態類別：無
        "dp": None, # 小數位數：無
        "icon": "mdi:nature-people-outline", # 圖標：戶外人物
    },
    "publishtime": { # 資料發布時間
        "dc": None, # 設備類別：無
        "unit": None, # 單位：無
        "sc": None, # 狀態類別：無
        "dp": None, # 小數位數：無
        "icon": "mdi:update", # 圖標：更新
    },
    "so2": { # 二氧化硫濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb (十億分之一)
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "so2_avg": { # 二氧化硫平均濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "co": { # 一氧化碳濃度
        "dc": SensorDeviceClass.CO, # 設備類別：一氧化碳 (ppm)
        "unit": "ppm", # 單位：ppm (百萬分之一)
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無
    },
    "co_8hr": { # 一氧化碳八小時平均濃度
        "dc": SensorDeviceClass.CO, # 設備類別：一氧化碳 (ppm)
        "unit": "ppm", # 單位：ppm
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無
    },
    "o3": { # 臭氧濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "o3_8hr": { # 臭氧八小時平均濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "no2": { # 二氧化氮濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "nox": { # 氮氧化物濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "no": { # 一氧化氮濃度
        "dc": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, # 設備類別：揮發性有機化合物 (ppb)
        "unit": "ppb", # 單位：ppb
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": "mdi:molecule", # 圖標：分子
    },
    "pm10": { # 懸浮微粒 (PM10) 濃度
        "dc": SensorDeviceClass.PM10, # 設備類別：PM10 (µg/m³)
        "unit": "µg/m³", # 單位：微克/立方公尺
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無
    },
    "pm10_avg": { # 懸浮微粒 (PM10) 平均濃度
        "dc": SensorDeviceClass.PM10, # 設備類別：PM10 (µg/m³)
        "unit": "µg/m³", # 單位：微克/立方公尺
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無
    },
    "pm2.5": { # 細懸浮微粒 (PM2.5) 濃度
        "dc": SensorDeviceClass.PM25, # 設備類別：PM2.5 (µg/m³)
        "unit": "µg/m³", # 單位：微克/立方公尺
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無
    },
    "pm2.5_avg": { # 細懸浮微粒 (PM2.5) 平均濃度
        "dc": SensorDeviceClass.PM25, # 設備類別：PM2.5 (µg/m³)
        "unit": "µg/m³", # 單位：微克/立方公尺
        "sc": SensorStateClass.MEASUREMENT, # 狀態類別：測量值
        "dp": 2, # 小數位數：2
        "icon": None, # 圖標：無
    },
}
