# NukeBot

---

⚠️ **法律免責聲明**
本專案僅供 **教學、教育與研究目的** 使用。
- 請勿將此工具用於任何未經許可的真實伺服器。
- 使用此工具攻擊他人伺服器可能違反 Discord 的 [服務條款](https://discord.com/terms) 並導致帳號被封鎖。
- 作者對因不當使用本工具而造成的任何損失或法律責任概不負責。

---

## 環境需求

- Python 3.11+
- Discord 帳號與開發者權限
- Git (用於下載程式)

---

## 開始使用

**1.先在你的主機執行**

```
git clone https://github.com/Wayne27304/NukeBot.git
python -m pip install -U discord.py aiohttp
```

**2. 填入token**

在app.py找到 `TOKEN =` 在後面填上機器人的token

**3. 執行程式**

```
python app.py
```

---

## 使用說明

1. 使用 /send 發送5則 custom_msg 函數
2. 使用 /nuke 來炸群 (刪除頻道更換頻道名稱等等)
3. 使用 /bye  刪除所有頻道
4. 使用 /stop 停止所有炸群動作 (beta)
5. 使用 /pro_send 自訂炸群訊息

---

## 參考

1. https://github.com/weiwei54321/discord_user_app_nuke
2. LY Nuke (在DiscordServer開源，但我已經退了)

---

## 授權
本專案採用 [MIT License](LICENSE) 授權
