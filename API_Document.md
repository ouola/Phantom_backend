# API 文件
## 1. PharmacyByOpeningHoursAPIView

### URL
- `GET` `pharmacies/opening-hours/`
### Example(Postman)
- `pharmacies/opening-hours/?weekday=Sun&time=23:59`

### 介紹
此API用於查詢在指定星期幾和時間內開放的藥局。

### Query Parameters

| 參數名稱 | 類型 | 必填 | 描述                 |
|----------|------|------|----------------------|
| `weekday` | `str`  | 是   | 要查詢的星期幾，例如 "Mon"、"Tue"。 |
| `time`    | `str`  | 是   | 要查詢的時間，格式為 "HH:MM"。     |

### Response

- **成功** (200 OK):
  ```json
  [
    {
      "name": "Pharmacy A"
    },
   {
      "name": "Pharmacy b"
    }
  ]
- **錯誤** (400 Bad Request):

  - 缺少 `weekday` 或 `time` :
    ```json
    {
      "error": "Weekday and time parameters are required."
    }
    ```

  - `time` 日期格式錯誤:
    ```json
    {
      "error": "Invalid time format. Use HH:MM format."
    }

## 2. MasksByPharmacyAPIView

### URL
- `GET` `pharmacies/masks/`
### Example(Postman)
- `pharmacies/masks/?pharmacy_name=DFW Wellness&sort_by=name`

### 介紹
此API用於查詢指定藥局的口罩資訊，並可以按名稱或價格排序。

### Query Parameters

| 參數名稱       | 類型   | 必填 | 描述                           |
| -------------- | ------ | ---- | -------------------------------- |
| `pharmacy_name` | `str`  | 是   | 藥局名稱                        |
| `sort_by`       | `str`  | 否   | 排序依據，值為 `"name"` 或 `"price"`，預設為 `"name"` |

### Response

- **成功** (200 OK):
```json
[
  {
    "name": "mask A",
    "price": "3.80"
  },
  {
    "name": "mask B",
    "price": "37.82"
  },
]
```
- **錯誤** (400 Bad Request):

	- **缺少 `pharmacy_name` :**
	  ```json
	  {
	    "error": "Pharmacy name is required."
	  }
   
	- **`sort_by` 參數錯誤:**
	  ```json
	  {
	    "error": "Invalid sort_by parameter. Use name or price."
	  }
   
## 3.PharmaciesByMaskCountAPIView

## URL 
- `GET` `pharmacies/mask-count/`
### Example(Postman)
- `pharmacies/mask-count/?comparison=more&count=5&min_price=0&max_price=20`

### 介紹 
此 API 用於查詢擁有指定數量以上或以下口罩的藥局。

### Query Parameters

| 參數名稱   | 類型  | 必填 | 描述                           |
|------------|-------|------|--------------------------------|
| `comparison` | `str`   | 是   | 比較方式，值為 "more" 或 "less" |
| `count`      | `int`   | 是   | 口罩數量                       |
| `min_price`  | `float` | 否   | 最低價格，預設為 0             |
| `max_price`  | `float` | 是   | 最高價格                       |

### Response

- **成功(200 OK):**

```json
[
  {
    "name": "Pharmacy A",
    "mask_count": 10
  },
	{
    "name": "Pharmacy b",
    "mask_count": 9
  }
]
```

- **錯誤** (400 Bad Request):

	- **缺少必要參數:**
	  ```json
	  {
	    "error": "Comparison, count, and max_price parameters are required."
	  }
	- **`comparison ` 參數錯誤:**
	  ```json
	  {
 		"error": "Comparison must be either more or less."
	  }
	- **參數類型錯誤:**
	  ```json
	  {
  		"error": "Count must be an integer, and min_price and max_price must be floats."
	  }
   
## 4. TopUsersByTransactionAPIView

### URL

- `GET` `users/top-transactions/`
### Example(Postman)
- `users/top-transactions/?top_x=3&start_date=2021-01-20&end_date=2021-01-26`

### 介紹

此 API 用於查詢指定日期範圍內交易總金額最高的前 `top_x` 用戶。

### Query Parameters

| 參數名稱   | 類型     | 必填 | 描述                                     |
|------------|----------|------|------------------------------------------|
| `top_x`      | `int`      | 是   | 要查詢的用戶數量。必須是整數。           |
| `start_date`  | `str`      | 是   | 起始日期，格式為 YYYY-MM-DD。            |
| `end_date`    | `str`      | 是   | 結束日期，格式為 YYYY-MM-DD。            |

### Response

- **成功(200 OK):**
```json
[
  {
    "name": "User A",
    "total_amount": 44.11
  },
  {
    "name": "User B",
    "total_amount": 41.96
  }
]
```
- **錯誤** (400 Bad Request):
  
	- **缺少必要參數:**
	  ```json
		{
		  "error": "top_x, start_date, and end_date parameters are required."
		}
	- **`top_x ` 參數格式錯誤:**
	  ```json
		{
		  "error": "top_x must be an integer."
		}
	- **日期格式錯誤**
	  ```json
		{
  		"error": "start_date and end_date must be in YYYY-MM-DD format."
		}
	- **`end_date ` 不可早於 `start_date `:**
	  ```json
		{
 		 "error": "end_date cannot be before start_date."
		}
   
## 5. TotalMasksAndTransactionValueAPIView

### URL

- `GET` `transactions/total/`
### Example(Postman)
- `transactions/total/?start_date=2021-01-20&end_date=2021-01-26`
### 介紹

此 API 用於計算指定日期範圍內的總面罩數量和總交易金額。

### Query Parameters

| 參數名稱   | 類型     | 必填 | 描述                                     |
|------------|----------|------|------------------------------------------|
| `start_date`  | `str`      | 是   | 起始日期，格式為 YYYY-MM-DD。            |
| `end_date`   | `str`      | 是   | 結束日期，格式為 YYYY-MM-DD。            |

### Response

- **成功(200 OK):**
```json
{
  "total_masks": 150,
  "total_amount": 5000.00
}
```
- **錯誤** (400 Bad Request):
	- **缺少必要參數:**
	  ```json
		{
		  "error": "start_date and end_date parameters are required."
		}
	- **日期格式錯誤:**
	  ```json
		{
		  "error": "Invalid date format. Use YYYY-MM-DD."
		}
	- **`end_date ` 不可早於 `start_date `:**
	  ```json
		{
 		 "error": "Start date must be before or equal to end date."
		}
   
## 6. SearchAPIView

### URL

- `GET` `search/`
### Example
- `search/?search_term=Mask`
### 介紹

此 API 用於根據搜索關鍵詞查詢藥局和口罩。返回匹配的藥局和口罩列表。

### Query Parameters

| 參數名稱     | 類型     | 必填 | 描述                       |
|--------------|----------|------|----------------------------|
| `search_term`  | `str`      | 是   | 搜索關鍵詞                |

### Response

- **成功(200 OK):**
```json
{
  "pharmacies": [
    {
      "id": 1,
      "name": "Pharmacy A"
    }
  ],
  "masks": [
    {
      "id": 1,
      "name": "Mask A",
      "pharmacy": "Pharmacy A"
    }
  ]
}
```
- **錯誤** (400 Bad Request):
	- **缺少`search_term ` 參數:**
	  ```json
		{
 		 "error": "search_term parameter is required."
		}

## 7. PurchaseMaskAPIView

### URL

- `POST` `purchase-mask/`

### Example
- `purchase-mask/`
#### Request Body
```json
{
    "user_name": "Yvonne Guerrero",
    "pharmacy_name": "HealthMart",
    "mask_name": "Cotton Kiss (green) (3 per pack)",
    "quantity": 2
}
```
### 介紹

此 API 用於處理用戶購買口罩的請求。當用戶購買口罩時，會檢查用戶的餘額，更新用戶和藥局的現金餘額，並記錄購買歷史。

### Request Body

| 參數名稱      | 類型     | 必填 | 描述                             |
|---------------|----------|------|----------------------------------|
| `user_name`     | `str`      | 是   | 用戶名稱                        |
| `pharmacy_name`| `str`      | 是   | 藥局名稱                        |
| `mask_name`    | `str`      | 是   | 口罩名稱                        |
| `quantity`      | `int`      | 否   | 購買的口罩數量，默認為0         |

### Response

- **成功(200 OK):**
```json
{
  "message": "Purchase successful",
  "purchase_details": {
    "user": "User Name",
    "pharmacy": "Pharmacy Name",
    "mask": "Mask Name",
    "quantity": 5,
    "total_price": 100.00
  }
}
```
- **錯誤** (400 Bad Request):
	- **`Quantity  `不是整數:**
	  ```json
		{
 		 "error": "Quantity must be a positive integer"
		}
	- **用戶餘額不足:**
	  ```json
		{
  		"error": "Insufficient user balance"
		}
- **錯誤** (404 Not Found):
	- **用戶不存在:**
	  ```json
		{
 		 "error": "User does not exist"
		}
	- **藥局不存在**
	  ```json
		{
 		 "error": "Pharmacy does not exist"
		}
	- **口罩在指定藥局中不存在:**
	  ```json
		{
 		 "error": "Mask does not exist in the specified pharmacy"
		}
- **錯誤** (500 Internal Server Error):
	- **其他錯誤:**
	  ```json
		{
 		 "error": "Error description"
		}
