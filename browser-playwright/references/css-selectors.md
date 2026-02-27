# CSS 选择器参考

## 基础选择器

| 选择器 | 示例 | 说明 |
|--------|------|------|
| `*` | `*` | 选中所有元素 |
| `#id` | `#submit-btn` | 通过 ID 选择 |
| `.class` | `.btn-primary` | 通过类名选择 |
| `tag` | `div`, `button`, `input` | 通过标签名选择 |

## 组合选择器

| 选择器 | 示例 | 说明 |
|--------|------|------|
| `selector1 selector2` | `.container .btn` | 后代选择器 |
| `selector1 > selector2` | `.form > .input` | 子元素选择器 |
| `selector1, selector2` | `.btn, .link` | 并集选择器 |
| `selector1 + selector2` | `h1 + p` | 相邻兄弟选择器 |

## 属性选择器

| 选择器 | 示例 | 说明 |
|--------|------|------|
| `[attr]` | `[disabled]` | 有该属性的元素 |
| `[attr=value]` | `[type="submit"]` | 属性等于指定值 |
| `[attr*=value]` | `[class*="active"]` | 属性包含指定值 |
| `[attr^=value]` | `[href^="https"]` | 属性以指定值开头 |
| `[attr$=value]` | `[src$=".png"]` | 属性以指定值结尾 |

## 伪类选择器

| 选择器 | 示例 | 说明 |
|--------|------|------|
| `:hover` | `a:hover` | 鼠标悬停状态 |
| `:active` | `button:active` | 激活状态 |
| `:focus` | `input:focus` | 聚焦状态 |
| `:first-child` | `li:first-child` | 第一个子元素 |
| `:last-child` | `li:last-child` | 最后一个子元素 |
| `:nth-child(n)` | `li:nth-child(2)` | 第 n 个子元素 |
| `:disabled` | `button:disabled` | 禁用状态 |
| `:checked` | `input:checked` | 选中状态 |

## 实战示例

### 表单元素
```css
# 用户名输入框
input[name="username"]
input[type="text"][placeholder*="用户名"]

# 密码输入框
input[type="password"]

# 提交按钮
button[type="submit"]
input[type="submit"]

# 选择框
select[name="country"]
option[value="China"]
```

### 链接和按钮
```css
# 所有链接
a

# 指定 href 的链接
a[href*="login"]
a[href^="https://"]

# 按钮文本包含"登录"
button:has-text("登录")
```

### 模态框
```css
# 模态框容器
.modal
.dialog
.popup

# 确认按钮
.modal .btn-confirm
button:has-text("确定")
```

### 二维码
```css
# 二维码图片
img[src*="qrcode"]
img[alt*="二维码"]
canvas.qrcode

# 扫码登录容器
.qrcode-container
.login-qrcode
```

## Playwright 专用选择器

Playwright 提供了一些增强选择器：

### 文本选择
```css
# 文本完全匹配
text="登录"

# 文本包含
text="确"

# CSS + 文本组合
button >> text="提交"
.submit-btn:has-text("同意")
```

### 角色/可访问性
```css
# 按角色选择
button[role="button"]
[role="dialog"]

# 按标签文本
button:has-text("取消")
```

## 最佳实践

1. **优先使用唯一属性**: ID、name、aria-label
2. **避免脆弱选择器**: 不要依赖动态生成的类名如 `.class-abc123`
3. **使用组合选择器**: 提高准确性
4. **考虑数据属性**: `[data-testid="submit-btn"]` 是最稳定的选择器
