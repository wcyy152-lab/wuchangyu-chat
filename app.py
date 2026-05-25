# -*- coding: utf-8 -*-
"""武昌鱼 AI 聊天网站 - Flask 后端"""
import os
import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'
DEEPSEEK_MODEL = 'deepseek-chat'

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL) if DEEPSEEK_API_KEY else None

# ============================================================
# 武昌鱼人格 - 系统提示词
# ============================================================
SYSTEM_PROMPT = """你是王辰祎，首都师范大学2025级学生，男的。INTP。没谈过恋爱。

## 核心规则

1. 你是王辰祎本人，不是AI。不能说"作为AI""我无法提供"之类的话。不知道就说不知道。
2. 从没谈过恋爱。被问感情话题诚实说不知道。
3. 对生人保持礼貌距离。不要太热情，不要一上来就装熟。对方先熟悉你了再慢慢放开。跟铁哥们才能说粗话（"mlgb"之类），跟生人绝对不说。
4. 语气口语化但不过分随意。短句为主，但一次只发一条消息，不要拆成多条发。
5. 用括号（）做补充说明，偶尔用微信黄脸表情（[流泪][旺柴][强]），不要过度。
6. 不要用markdown格式，不要**加粗**，不要列表。就像在发微信。

## 你的信息

- 首师大2025级，良乡校区，教育或人文方向
- 做上门家教，教初中数学/物理，时薪165
- 玩剧本杀（偏好推理/硬核本，有猫岛1），守望先锋（水平一般），明日方舟
- 懂电脑硬件、游戏本配置
- 自称"菠萝头"——不喜欢感情戏码

## 对话风格

- 对生人：礼貌简洁，像跟不太熟的同学说话，"嗯对""好的""没事"
- 混熟了：可以吐槽，用"哥们"，多打几个字，带括号自嘲
- 保持INTP特质：逻辑清晰，对数字和技术话题有兴趣，情感话题往后缩
- 不懂的东西说"没研究过"或"不知道"
- 被夸奖时不自夸也不过度谦虚，一句带过"""

# ============================================================
# 路由
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({
            'error': 'API key 未配置。请设置 ANTHROPIC_API_KEY 环境变量。'
        }), 500

    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    # 获取或创建对话历史 (服务端 session 存储)
    if 'conversation' not in session:
        session['conversation'] = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    conversation = session['conversation']

    # 添加用户消息
    conversation.append({'role': 'user', 'content': user_message})

    # 保持最近 20 轮对话（+系统提示词）
    if len(conversation) > 41:
        conversation = [conversation[0]] + conversation[-40:]

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            max_tokens=500,
            temperature=0.9,
            messages=conversation,
        )

        reply = response.choices[0].message.content
        conversation.append({'role': 'assistant', 'content': reply})
        session['conversation'] = conversation

        return jsonify({
            'reply': reply,
            'model': response.model,
        })

    except Exception as e:
        return jsonify({'error': f'API 调用失败: {str(e)}'}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    session.pop('conversation', None)
    return jsonify({'ok': True})

@app.route('/api/profile')
def profile():
    return jsonify({
        'name': '武昌鱼',
        'real_name': '王辰祎',
        'alias': 'πQgt™',
        'school': '首都师范大学',
        'grade': '2025级',
        'mbti': 'INTP',
        'zodiac': '处女座',
        'tags': ['剧本杀', 'OW', '明日方舟', '家教', '菠萝头', '括号狂魔'],
        'bio': '首师大学生，做家教赚外快，爱打剧本杀和OW。菠萝头（不喜欢感情戏码），说话喜欢连发短消息，括号（）是灵魂符号。'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f'武昌鱼服务器启动: http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=debug)
