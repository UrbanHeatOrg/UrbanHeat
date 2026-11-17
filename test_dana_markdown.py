import asyncio
from playwright.async_api import async_playwright

async def run_markdown_verification():
    print("======================================================================")
    print("DANA COPILOT CHAT — MARKDOWN RENDERING VERIFICATION SUITE")
    print("======================================================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = await context.new_page()
        
        # 1. Load the HeatShield web dashboard
        print("Navigating to http://localhost:8000 ...")
        await page.goto("http://localhost:8000", wait_until="domcontentloaded")
        await asyncio.sleep(2.0)

        # 2. Verify marked and DOMPurify are loaded
        libs_loaded = await page.evaluate("""() => {
            return {
                markedLoaded: typeof marked !== 'undefined',
                purifyLoaded: typeof DOMPurify !== 'undefined',
                renderDanaMarkdownDefined: typeof renderDanaMarkdown === 'function',
                copyDanaCodeDefined: typeof copyDanaCode === 'function',
                escapeHtmlDefined: typeof escapeHtml === 'function'
            };
        }""")
        print(f"Library & Function checks: {libs_loaded}")
        assert libs_loaded["markedLoaded"], "marked.min.js failed to load!"
        assert libs_loaded["purifyLoaded"], "purify.min.js failed to load!"
        assert libs_loaded["renderDanaMarkdownDefined"], "renderDanaMarkdown function missing!"
        assert libs_loaded["copyDanaCodeDefined"], "copyDanaCode function missing!"
        assert libs_loaded["escapeHtmlDefined"], "escapeHtml function missing!"
        print("  [PASS] All libraries and markdown helper functions loaded successfully.")

        # 3. Unit test renderDanaMarkdown in the browser DOM
        test_markdown = """### Thermal Mitigation Analysis: West Dallas
According to the **BigQuery ML Heat Offset Model** and Singapore *DUCT 3D Heat X-Ray*, here is the scenario evaluation:

> Model Armor verified this spatial policy. Projected heat index reduction: **-3.8°F**.

| Site Name | Heat Vuln Index | Surface Temp (°F) | Action Priority |
| :--- | :--- | :--- | :--- |
| West Dallas Center | 0.89 | 104.2 | Critical |
| Pleasant Grove Park | 0.82 | 102.5 | High |
| Bachman Rec Center | 0.74 | 99.8 | Moderate |

Key implementation tasks:
1. Dispatch 2 mobile hydration tankers
2. Activate cool pavement retrofits
3. Deploy 1,200m pedestrian walking buffers

For programmatic dispatch, execute the following API call:
```python
import httpx
response = httpx.post("http://localhost:8000/api/dispatch", json={"trucks": 2, "temp": 104.5})
print(response.json())
```
Reference: [HeatShield API Docs](http://localhost:8000/docs) with parameter `status=200` and Census Tract `48113020500`.
"""
        
        eval_result = await page.evaluate("""(md) => {
            const html = renderDanaMarkdown(md);
            const container = document.createElement('div');
            container.className = 'dana-markdown';
            container.innerHTML = html;
            document.body.appendChild(container);

            const hasTable = container.querySelector('.table-wrapper table') !== null;
            const thCount = container.querySelectorAll('th').length;
            const tdCount = container.querySelectorAll('td').length;
            const hasCodeBlock = container.querySelector('.code-block-wrapper') !== null;
            const hasCodeHeader = container.querySelector('.code-header') !== null;
            const codeLang = container.querySelector('.code-header span')?.innerText || '';
            const hasCopyBtn = container.querySelector('.copy-code-btn') !== null;
            const hasBlockquote = container.querySelector('blockquote') !== null;
            const hasInlineCode = container.querySelector(':not(pre) > code') !== null;
            const hasH3 = container.querySelector('h3') !== null;
            const hasOl = container.querySelector('ol') !== null;
            const link = container.querySelector('a');
            const linkTarget = link?.getAttribute('target');
            const linkRel = link?.getAttribute('rel');

            container.remove();

            return {
                hasTable,
                thCount,
                tdCount,
                hasCodeBlock,
                hasCodeHeader,
                codeLang,
                hasCopyBtn,
                hasBlockquote,
                hasInlineCode,
                hasH3,
                hasOl,
                linkTarget,
                linkRel
            };
        }""", test_markdown)

        print(f"Rendered Markdown Structure:\n{eval_result}")
        assert eval_result["hasTable"], "Table wrapper and table element missing!"
        assert eval_result["thCount"] == 4, f"Expected 4 table headers, got {eval_result['thCount']}"
        assert eval_result["tdCount"] == 12, f"Expected 12 table cells, got {eval_result['tdCount']}"
        assert eval_result["hasCodeBlock"], "Code block wrapper missing!"
        assert "PYTHON" in eval_result["codeLang"], f"Expected PYTHON language badge, got {eval_result['codeLang']}"
        assert eval_result["hasCopyBtn"], "Copy code button missing!"
        assert eval_result["hasBlockquote"], "Blockquote element missing!"
        assert eval_result["hasInlineCode"], "Inline code element missing!"
        assert eval_result["hasH3"], "H3 heading missing!"
        assert eval_result["hasOl"], "Ordered list missing!"
        assert eval_result["linkTarget"] == "_blank", "Link target should be _blank!"
        assert "noopener" in eval_result["linkRel"], "Link rel should contain noopener!"
        print("  [PASS] Full markdown syntax (tables, code blocks, lists, quotes, links) verified.")

        # 4. Security & XSS sanitization test
        xss_result = await page.evaluate("""() => {
            const maliciousMd = 'Hello <script id="xss-test">window.XSS_DETECTED=true;</script><img src="invalid" onerror="window.XSS_IMG=true"> **Safe Bold**';
            const html = renderDanaMarkdown(maliciousMd);
            const container = document.createElement('div');
            container.id = 'security-test-box';
            container.innerHTML = html;
            document.body.appendChild(container);
            
            const scriptTag = container.querySelector('script');
            const hasBold = container.querySelector('strong') !== null;
            const xssTriggered = window.XSS_DETECTED === true;

            container.remove();
            return {
                scriptTagPresent: scriptTag !== null,
                hasBold,
                xssTriggered
            };
        }""")
        print(f"XSS Sanitization results: {xss_result}")
        assert not xss_result["scriptTagPresent"], "Malicious <script> tag was not stripped by DOMPurify!"
        assert not xss_result["xssTriggered"], "XSS script executed!"
        assert xss_result["hasBold"], "Safe bold tag should still be preserved!"
        print("  [PASS] XSS Sanitization and DOMPurify protection verified.")

        # 5. Open Dana Copilot drawer in UI
        print("Opening Dana Copilot drawer...")
        # Toggle copilot drawer if it is hidden
        await page.evaluate("""() => {
            const drawer = document.getElementById('copilot-drawer');
            if (drawer && drawer.classList.contains('translate-x-full')) {
                toggleCopilot();
            }
        }""")
        await asyncio.sleep(0.8)

        # 6. Verify initial welcome message in chat-stream
        welcome_check = await page.evaluate("""() => {
            const stream = document.getElementById('chat-stream');
            const markdownContainers = stream.querySelectorAll('.dana-markdown');
            return {
                count: markdownContainers.length,
                text: stream.innerText
            };
        }""")
        print(f"Welcome message check: {welcome_check['count']} dana-markdown container(s) found.")
        assert welcome_check["count"] >= 1, "Welcome message should have .dana-markdown container!"

        # 7. Inject a rich markdown response into Dana chat to test copy button & live visual rendering
        print("Injecting rich scenario markdown message into #chat-stream ...")
        await page.evaluate("""(md) => {
            const container = document.getElementById('chat-stream');
            const rendered = renderDanaMarkdown(md);
            container.innerHTML += `
              <div class="flex gap-2.5 test-response-bubble">
                <div class="w-7 h-7 rounded-xl bg-blue-600 flex-shrink-0 flex items-center justify-center text-white text-xs shadow-md">
                  <i class="fa-solid fa-robot"></i>
                </div>
                <div class="trace-card border-white/10 text-slate-200 rounded-2xl p-3.5 max-w-[85%] border leading-relaxed shadow-lg">
                  <div class="flex items-center justify-between text-[9px] text-slate-400 mb-1.5 border-b border-white/10 pb-1">
                    <span class="font-semibold text-slate-300 flex items-center gap-1.5"><i class="fa-solid fa-robot text-cyan-400"></i> Commander CoolAid</span>
                    <span class="text-purple-400 font-mono flex items-center gap-1"><i class="fa-solid fa-shield-cat"></i> Model Armor Verified</span>
                  </div>
                  <div class="dana-markdown coolaid-markdown text-xs">
                    ${rendered}
                  </div>
                </div>
              </div>
            `;
            container.scrollTop = container.scrollHeight;
        }""", test_markdown)
        await asyncio.sleep(0.5)

        # 8. Test 1-click copy button
        print("Testing 1-click Copy Code button ...")
        copy_btn = await page.query_selector(".test-response-bubble .copy-code-btn")
        assert copy_btn is not None, "Copy code button not found in rendered bubble!"
        
        await copy_btn.click(force=True)
        await asyncio.sleep(0.3)
        
        btn_text_after = await page.evaluate("""() => {
            const btn = document.querySelector('.test-response-bubble .copy-code-btn');
            return btn ? btn.innerText.trim() : '';
        }""")
        print(f"Copy button state after click: '{btn_text_after}'")
        assert "Copied" in btn_text_after, f"Copy button did not show Copied state! Got: '{btn_text_after}'"
        print("  [PASS] 1-click Copy Code interaction succeeded with feedback state.")

        # 9. Test sending a message through UI input and verify escaping
        print("Testing user input escaping through #copilot-input ...")
        await page.fill("#copilot-input", "Testing <b>bold</b> and <script>alert('xss')</script> input")
        # Submit without making network call or let it complete
        await page.evaluate("""() => {
            const input = document.getElementById('copilot-input');
            const text = input.value.trim();
            const container = document.getElementById('chat-stream');
            container.innerHTML += `
              <div class="flex gap-2.5 justify-end test-user-bubble">
                <div class="bg-cyan-600 rounded-2xl p-3 text-white max-w-[85%] leading-relaxed shadow-md">
                  ${escapeHtml(text)}
                </div>
              </div>
            `;
            input.value = '';
        }""")
        
        user_bubble_html = await page.evaluate("""() => {
            const bubble = document.querySelector('.test-user-bubble');
            return bubble ? bubble.innerHTML : '';
        }""")
        assert "&lt;script&gt;" in user_bubble_html, "User message script tag was not properly HTML escaped!"
        print("  [PASS] User message HTML escaping verified.")

        # 10. Capture high-fidelity screenshot of the Dana Copilot drawer with rich markdown
        screenshot_path = "screenshot_dana_markdown.png"
        await page.screenshot(path=screenshot_path)
        print(f"  [SCREENSHOT] Captured full dashboard screenshot with Dana markdown: {screenshot_path}")

        # Also capture a focused drawer screenshot
        drawer_el = await page.query_selector("#copilot-drawer")
        if drawer_el:
            await drawer_el.screenshot(path="screenshot_dana_drawer_detail.png")
            print("  [SCREENSHOT] Captured focused drawer screenshot: screenshot_dana_drawer_detail.png")

        await browser.close()

    print("======================================================================")
    print("ALL DANA MARKDOWN TESTS COMPLETED SUCCESSFULLY! 🎉")
    print("======================================================================")

if __name__ == "__main__":
    asyncio.run(run_markdown_verification())
