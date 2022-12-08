'''Websocket Bridge extension for chatGPT'''
import asyncio
import json

import websocket_bridge_python
from playwright.async_api import async_playwright
from pycookiecheat import chrome_cookies

conversation_count = 0

async def connect_chat_gpt(playwright):
    """using playwright to connect chatGPT."""
    global PAGE, CONTEXT, BRIDGE
    browser_type = playwright.chromium
    debug_mode = await BRIDGE.get_emacs_var("ws-chat-gpt-debug")
    debug_mode = bool(debug_mode == 'true');
    browser = await browser_type.launch(headless=(not debug_mode))
    CONTEXT = await browser.new_context()
    cookie_array = []
    cookies = chrome_cookies("https://chat.openai.com")
    cookie_array = [
        {"name": x, "value": y, "path": "/", "domain": "chat.openai.com", "secure": True}
        for x, y in cookies.items()
    ]
    await CONTEXT.add_cookies(cookie_array)
    PAGE = await CONTEXT.new_page()
    await PAGE.goto("https://chat.openai.com/chat")
    f12 = await PAGE.context.new_cdp_session(PAGE)
    await f12.send("Network.enable")
    await f12.send("Page.enable")
    f12.on("Network.responseReceived", handle_websocket_frame_received)
    message = "ChatGPT is ready."
    print(message)
    await BRIDGE.message_to_emacs(message)

async def handle_websocket_frame_received(params:dict):
    """define a handler for chrome received websockets."""
    global conversation_count
    if params["response"]:
        if params["response"]["url"] == 'https://chat.openai.com/backend-api/conversation':
            await fetch_anwser(conversation_count)
            conversation_count = conversation_count + 1

async def fetch_anwser(number):
    '''fetch chatGPT anwser'''
    class_name = f'.request-\\:R2d6\\:-{number}'
    anwser = await PAGE.wait_for_selector(class_name)
    class_name = f'.request-\\\\:R2d6\\\\:-{number}'
    js = f'() => document.querySelector("{class_name}").parentNode.nextSibling'
    await PAGE.wait_for_function(js)
    html = (await anwser.inner_html()).replace('"', "'")
    await BRIDGE.eval_in_emacs(f'(ws-chat-gpt-render "{html}")')

async def input_text(text):
    '''input text in chatGPT textarea'''
    await PAGE.type("textarea", f"{text}\n")

async def refresh():
    '''refresh chatGPT page'''
    global conversation_count
    await PAGE.reload()
    conversation_count = 0

async def on_message(message):
    """dispatch message recived from Emacs."""
    info = json.loads(message)
    cmd = info[1][0].strip()
    sentence_str = info[1][1]
    if cmd == "input":
        await input_text(sentence_str)
    elif cmd == "refresh":
        await refresh()
    else:
        print("not fount dispatcher", flush=True)

async def main():
    """main"""
    global BRIDGE
    async with async_playwright() as playwright:
        try:
            BRIDGE = websocket_bridge_python.bridge_app_regist(on_message)
            await asyncio.gather(connect_chat_gpt(playwright), BRIDGE.start())
        except TimeoutError:
            print("Timeout!")

asyncio.run(main())
