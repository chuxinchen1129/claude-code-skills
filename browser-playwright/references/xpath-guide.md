# XPath 选择器指南

## 基础语法

| 语法 | 示例 | 说明 |
|------|------|------|
| `/` | `/html/body/div` | 从根节点开始 |
| `//` | `//div` | 从任意位置开始 |
| `.` | `.` | 当前节点 |
| `..` | `..` | 父节点 |
| `@` | `@id` | 属性选择 |
| `*` | `//*` | 任意元素 |

## 节点选择

| XPath | 说明 |
|-------|------|
| `//div` | 所有 div 元素 |
| `//div[@class='container']` | class 为 container 的 div |
| `//input[@type='text']` | type 为 text 的 input |
| `//button[@id='submit']` | id 为 submit 的按钮 |
| `//a[@href]` | 所有有 href 属性的链接 |

## 文本匹配

| XPath | 说明 |
|-------|------|
| `//button[text()='登录']` | 文本完全匹配"登录"的按钮 |
| `//button[contains(text(), '登')]` | 文本包含"登"的按钮 |
| `//a[starts-with(text(), '点击')]` | 文本以"点击"开头的链接 |
| `//*[text()='确定']` | 任意文本为"确定"的元素 |

## 位置选择

| XPath | 说明 |
|-------|------|
| `//div[1]` | 第一个 div |
| `//div[last()]` | 最后一个 div |
| `//div[position()<3]` | 前两个 div |
| `//li[position()>2 and position()<5]` | 第3、4个 li |
| `(//button)[2]` | 第二个按钮 |

## 属性操作

| XPath | 说明 |
|-------|------|
| `//*[@id]` | 所有有 id 属性的元素 |
| `//*[starts-with(@class, 'btn')]` | class 以"btn"开头的元素 |
| `//*[contains(@class, 'active')]` | class 包含"active"的元素 |
| `//*[ends-with(@src, '.png')]` | src 以".png"结尾的元素 |
| `//*[@disabled]` | 所有禁用的元素 |
| `//*[@checked]` | 所有选中的复选框 |

## 组合条件

| XPath | 说明 |
|-------|------|
| `//div[@class='container' and @id='main']` | 同时满足两个条件 |
| `//button[not(@disabled)]` | 未禁用的按钮 |
| `//input[@type='text' or @type='email']` | type 为 text 或 email |
| `//a[@href!='#']` | href 不等于"#"的链接 |

## 轴选择器

| 轴 | 示例 | 说明 |
|----|------|------|
| `ancestor` | `//button/ancestor::form` | 所有祖先元素 |
| `parent` | `//input/parent::div` | 父元素 |
| `child` | `//form/child::input` | 直接子元素 |
| `following` | `//h1/following::p` | 之后的所有元素 |
| `preceding` | `//button/preceding::label` | 之前的所有元素 |
| `following-sibling` | `//h1/following-sibling::p` | 之后的所有兄弟元素 |
| `preceding-sibling` | `//button/preceding-sibling::label` | 之前的所有兄弟元素 |

## 实战示例

### 表单操作
```xpath
# 用户名输入框
//input[@name='username']
//input[@placeholder*='用户名']

# 密码输入框
//input[@type='password']

# 提交按钮
//button[@type='submit']
//input[@type='submit']
//button[text()='提交']

# 选择框
//select[@name='country']
//option[@value='China']
```

### 授权流程
```xpath
# 授权按钮
//button[text()='授权']
//button[contains(text(), '同意')]
//input[@value='同意授权']

# 确认按钮
//button[@class='confirm']
//button[.='确定']
```

### 登录/注册
```xpath
# 登录按钮
//a[text()='登录']
//button[text()='登录']

# 注册按钮
//a[text()='注册']
//button[contains(text(), '立即注册')]
```

### 二维码
```xpath
# 二维码图片
//img[contains(@src, 'qrcode')]
//img[contains(@alt, '二维码')]
//canvas[contains(@class, 'qrcode')]

# 扫码登录相关
//div[contains(@class, 'qrcode-container')]
//div[@id='login-qrcode']
```

### 模态框
```xpath
# 模态框
//div[contains(@class, 'modal')]
//div[@role='dialog']

# 确认按钮
//div[contains(@class, 'modal')]//button[text()='确定']
//button[@class='btn-confirm']
```

### 下拉菜单
```xpath
# 下拉触发器
//button[@aria-expanded]
//div[contains(@class, 'dropdown')]//button

# 选项
//li[contains(@class, 'dropdown-item')]
//a[contains(@class, 'dropdown-option')]
```

## CSS vs XPath 对比

| 功能 | CSS | XPath |
|------|-----|-------|
| 按 ID | `#id` | `//*[@id='id']` |
| 按类名 | `.class` | `//*[@class='class']` |
| 按属性 | `[attr='val']` | `//*[@attr='val']` |
| 按文本 | ❌ | `//*[text()='text']` |
| 父元素选择 | ❌ | `//child/..` |
| 文本包含 | ❌ | `//*[contains(text(),'x')]` |

## 选择建议

1. **优先使用 CSS**: 更简洁、性能更好
2. **XPath 用于**:
   - 文本匹配
   - 向上查找父元素
   - 复杂条件组合
3. **避免复杂 XPath**: 越复杂越脆弱
4. **优先使用稳定属性**: id、name、data-* 属性

## Playwright 中的使用

```python
# 使用 XPath
await page.click('//button[text()="登录"]')
await page.fill('//input[@name="username"]', "user123")
await page.screenshot('//div[@class="modal"]', "modal.png")

# 获取文本
text = await page.inner_text('//*[text()="欢迎"]')

# 等待元素
await page.wait_for_selector('//img[contains(@src, "qrcode")]')
```
