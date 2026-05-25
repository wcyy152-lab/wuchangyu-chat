# 武昌鱼 AI Chat

和武昌鱼（王辰祎）聊天——首师大 INTP 学生，剧本杀/OW/明日方舟玩家。

## 本地运行

```bash
pip install -r requirements.txt
DEEPSEEK_API_KEY=sk-xxx python app.py
```

浏览器打开 `http://localhost:5000`

## 部署

一键部署到 Render：点击下方按钮

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

或手动：
1. Fork 此仓库
2. 在 Render 创建 Web Service
3. 设置环境变量 `DEEPSEEK_API_KEY`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
