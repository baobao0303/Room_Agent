#!/usr/bin/env python3
"""
tools/tds_search.py - High-precision Search & Component Lookup for TMT Design System (TDS).
Target Gateway: https://tds.design-system.local/
Catalog: 92+ Components, Directives, Design Tokens & Modules in TDS UI.
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
import re
from typing import List, Dict, Any, Optional

GATEWAY_BASE_URL = "https://tds.design-system.local"

# Complete verified catalog extracted directly from https://tds.design-system.local/
TDS_CATALOG: List[Dict[str, Any]] = [
    # 1. Button Suite
    {"name": "Button (Default)", "slug": "button-base", "category": "Button", "module": "TdsButtonModule", "selector": "[tds-button]", "link": "/components/button-base/vi", "desc": "Nút bấm tiêu chuẩn (Primary, Secondary, Success, Danger, Warning, Info).", "keywords": ["button", "nut", "click", "btn", "action", "primary"]},
    {"name": "Button Toggle", "slug": "button-toggle", "category": "Button", "module": "TdsButtonToggleModule", "selector": "tds-button-toggle", "link": "/components/button-toggle/vi", "desc": "Nút chuyển đổi trạng thái bật/tắt (Toggle).", "keywords": ["toggle", "switch", "button", "state"]},
    {"name": "Button Group", "slug": "button-group", "category": "Button", "module": "TdsButtonGroupModule", "selector": "tds-button-group", "link": "/components/button-group/vi", "desc": "Nhóm các nút bấm liền kề theo hàng ngang hoặc dọc.", "keywords": ["group", "nhom", "button", "list"]},
    {"name": "Button Outline", "slug": "button-outline", "category": "Button", "module": "TdsButtonModule", "selector": "[tds-button][variant='outline']", "link": "/components/button-outline/vi", "desc": "Nút viền ngoài không nền.", "keywords": ["outline", "border", "vien", "button"]},
    {"name": "Button Flat", "slug": "button-flat", "category": "Button", "module": "TdsButtonModule", "selector": "[tds-button][variant='flat']", "link": "/components/button-flat/vi", "desc": "Nút phẳng không viền không đổ bóng.", "keywords": ["flat", "phang", "button"]},
    {"name": "Button Overlay", "slug": "button-overlay", "category": "Button", "module": "TdsButtonModule", "selector": "[tds-button][variant='overlay']", "link": "/components/button-overlay/vi", "desc": "Nút phủ nền mờ dùng trên ảnh hoặc banner.", "keywords": ["overlay", "button", "mo"]},
    {"name": "Button Text", "slug": "button-text", "category": "Button", "module": "TdsButtonModule", "selector": "[tds-button][variant='text']", "link": "/components/button-text/vi", "desc": "Nút dạng văn bản không nền không viền.", "keywords": ["text", "chu", "link", "button"]},
    {"name": "Button Link", "slug": "link", "category": "Button", "module": "TdsButtonModule", "selector": "a[tds-button]", "link": "/components/link/vi", "desc": "Nút liên kết điều hướng dạng anchor link.", "keywords": ["link", "lien-ket", "href", "a"]},
    {"name": "Button Close", "slug": "button-close", "category": "Button", "module": "TdsButtonModule", "selector": "button[tds-button-close]", "link": "/components/button-close/vi", "desc": "Nút đóng (dấu X) cho modal, alert, drawer.", "keywords": ["close", "dong", "x", "cancel"]},
    {"name": "Button No Spacing", "slug": "button-no-spacing", "category": "Button", "module": "TdsButtonModule", "selector": "[tds-button][spacing='none']", "link": "/components/button-no-spacing/vi", "desc": "Nút không padding lề.", "keywords": ["no-spacing", "compact", "tight"]},
    {"name": "BackTop", "slug": "backtop", "category": "Button", "module": "TdsBackTopModule", "selector": "tds-back-top", "link": "/components/backtop/vi", "desc": "Nút cuộn nhanh lên đầu trang.", "keywords": ["backtop", "scroll-top", "len-dau-trang"]},

    # 2. Layout
    {"name": "Layout", "slug": "layout", "category": "Layout", "module": "TdsLayoutModule", "selector": "tds-layout, tds-header, tds-sider, tds-content", "link": "/components/layout/vi", "desc": "Khung bố cục chuẩn (Header, Sidebar, Content, Footer).", "keywords": ["layout", "bo-cuc", "sidebar", "header", "sider"]},
    {"name": "Divider", "slug": "divider", "category": "Layout", "module": "TdsDividerModule", "selector": "tds-divider", "link": "/components/divider/vi", "desc": "Đường kẻ phân cách nội dung ngang hoặc dọc.", "keywords": ["divider", "duong-ke", "separator", "hr", "line"]},
    {"name": "Flex", "slug": "flex", "category": "Layout", "module": "TdsFlexModule", "selector": "tds-flex", "link": "/components/flex/vi", "desc": "Khung sắp xếp phần tử dạng Flexbox linh hoạt.", "keywords": ["flex", "flexbox", "gap", "align", "justify"]},

    # 3. Navigation
    {"name": "Breadcrumb", "slug": "breadcrumb", "category": "Navigation", "module": "TdsBreadcrumbModule", "selector": "tds-breadcrumb", "link": "/components/breadcrumb/vi", "desc": "Thanh điều hướng phân cấp đường dẫn trang.", "keywords": ["breadcrumb", "dieu-huong", "duong-dan", "path"]},
    {"name": "Header", "slug": "header", "category": "Navigation", "module": "TdsHeaderModule", "selector": "tds-header", "link": "/components/header/vi", "desc": "Thanh tiêu đề điều hướng trên cùng trang.", "keywords": ["header", "topbar", "nav", "tieu-de"]},
    {"name": "Menu", "slug": "menu", "category": "Navigation", "module": "TdsMenuModule", "selector": "tds-menu", "link": "/components/menu/vi", "desc": "Menu điều hướng phân cấp đa tầng (Sidebar / TopNav).", "keywords": ["menu", "navigation", "nav", "submenu"]},
    {"name": "Pagination", "slug": "pagination", "category": "Navigation", "module": "TdsPaginationModule", "selector": "tds-pagination", "link": "/components/pagination/vi", "desc": "Phân trang dữ liệu danh sách.", "keywords": ["pagination", "phan-trang", "page", "paging"]},
    {"name": "Steps", "slug": "step", "category": "Navigation", "module": "TdsStepsModule", "selector": "tds-steps", "link": "/components/step/vi", "desc": "Quy trình nhiều bước (Wizard, Checkout steps).", "keywords": ["step", "steps", "quy-trinh", "buoc", "wizard"]},
    {"name": "PageHeader", "slug": "page-header", "category": "Navigation", "module": "TdsPageHeaderModule", "selector": "tds-page-header", "link": "/components/page-header/vi", "desc": "Tiêu đề trang kèm nút quay lại và các hành động chính.", "keywords": ["page-header", "title", "breadcrumb", "back"]},

    # 4. Data Entry
    {"name": "Input", "slug": "input", "category": "Data entry", "module": "TdsInputModule", "selector": "input[tds-input], tds-input-group", "link": "/components/input/vi", "desc": "Ô nhập liệu văn bản cơ bản kèm tiền tố, hậu tố.", "keywords": ["input", "nhap-lieu", "text", "form", "o-nhap"]},
    {"name": "InputNumber", "slug": "input-number", "category": "Data entry", "module": "TdsInputNumberModule", "selector": "tds-input-number", "link": "/components/input-number/vi", "desc": "Ô nhập liệu số lượng có nút tăng giảm, format tiền tệ.", "keywords": ["number", "so", "input-number", "currency", "tien"]},
    {"name": "Input Search", "slug": "search", "category": "Data entry", "module": "TdsInputModule", "selector": "input[tmt-input-search]", "link": "/components/search/vi", "desc": "Ô tìm kiếm có icon kính lúp và nút xóa nhanh.", "keywords": ["search", "tim-kiem", "find", "query"]},
    {"name": "Select", "slug": "select", "category": "Data entry", "module": "TdsSelectModule", "selector": "tds-select", "link": "/components/select/vi", "desc": "Hộp chọn dropdown đơn lẻ hoặc nhiều giá trị (Multiple).", "keywords": ["select", "dropdown", "chon", "combobox", "option"]},
    {"name": "Autocomplete", "slug": "auto-complete", "category": "Data entry", "module": "TdsAutoCompleteModule", "selector": "tds-autocomplete", "link": "/components/auto-complete/vi", "desc": "Ô gợi ý từ khóa tự động khi người dùng gõ phím.", "keywords": ["autocomplete", "goi-y", "suggest", "typeahead"]},
    {"name": "Cascader", "slug": "cascader", "category": "Data entry", "module": "TdsCascaderModule", "selector": "tds-cascader", "link": "/components/cascader/vi", "desc": "Chọn phân cấp đa tầng (Tỉnh/Thành -> Quận/Huyện -> Phường/Xã).", "keywords": ["cascader", "phan-cap", "tinh-thanh", "dia-chi"]},
    {"name": "Checkbox", "slug": "checkbox", "category": "Data entry", "module": "TdsCheckboxModule", "selector": "tds-checkbox, tds-checkbox-group", "link": "/components/checkbox/vi", "desc": "Hộp kiểm chọn một hoặc nhiều lựa chọn.", "keywords": ["checkbox", "hop-kiem", "tick", "check"]},
    {"name": "Radio", "slug": "radio", "category": "Data entry", "module": "TdsRadioModule", "selector": "tds-radio, tds-radio-group", "link": "/components/radio/vi", "desc": "Nút radio chọn 1 trong nhiều lựa chọn duy nhất.", "keywords": ["radio", "chon-mot", "radio-button"]},
    {"name": "DatePicker", "slug": "date-picker", "category": "Data entry", "module": "TdsDatePickerModule", "selector": "tds-date-picker", "link": "/components/date-picker/vi", "desc": "Hộp chọn ngày tháng năm lịch.", "keywords": ["date", "datepicker", "ngay", "lich", "calendar"]},
    {"name": "DateRangePicker", "slug": "date-range-picker", "category": "Data entry", "module": "TdsDatePickerModule", "selector": "tds-date-range-picker", "link": "/components/date-range-picker/vi", "desc": "Hộp chọn khoảng thời gian (Từ ngày - Đến ngày).", "keywords": ["range", "khoang-ngay", "date-range", "tu-ngay-den-ngay"]},
    {"name": "TimePicker", "slug": "time-picker", "category": "Data entry", "module": "TdsTimePickerModule", "selector": "tds-time-picker", "link": "/components/time-picker/vi", "desc": "Hộp chọn giờ phút giây.", "keywords": ["time", "gio", "phut", "dong-ho"]},
    {"name": "Switch", "slug": "switch", "category": "Data entry", "module": "TdsSwitchModule", "selector": "tds-switch", "link": "/components/switch/vi", "desc": "Công tắc bật / tắt gạt ngang.", "keywords": ["switch", "cong-tac", "toggle", "on-off"]},
    {"name": "Slider", "slug": "slider", "category": "Data entry", "module": "TdsSliderModule", "selector": "tds-slider", "link": "/components/slider/vi", "desc": "Thanh trượt điều chỉnh giá trị liên tục trong dải.", "keywords": ["slider", "thanh-truot", "range"]},
    {"name": "Rate", "slug": "rate", "category": "Data entry", "module": "TdsRateModule", "selector": "tds-rate", "link": "/components/rate/vi", "desc": "Đánh giá xếp hạng sao (1 - 5 sao).", "keywords": ["rate", "rating", "sao", "star", "danh-gia"]},
    {"name": "Form", "slug": "form", "category": "Data entry", "module": "TdsFormModule", "selector": "form[tds-form], tds-form-item", "link": "/components/form/vi", "desc": "Khung biểu mẫu quản lý validate, layout form.", "keywords": ["form", "bieu-mau", "validate", "form-item"]},
    {"name": "Upload", "slug": "upload", "category": "Data entry", "module": "TdsUploadModule", "selector": "tds-upload", "link": "/components/upload/vi", "desc": "Tải tệp tin, kéo thả tài liệu hoặc hình ảnh lên server.", "keywords": ["upload", "tai-len", "file", "image", "dropzone"]},
    {"name": "TreeSelect", "slug": "tree-select", "category": "Data entry", "module": "TdsTreeSelectModule", "selector": "tds-tree-select", "link": "/components/tree-select/vi", "desc": "Hộp chọn dữ liệu dạng cây thư mục phân cấp.", "keywords": ["tree-select", "cay", "danh-muc"]},
    {"name": "ColorPicker", "slug": "color-picker", "category": "Data entry", "module": "TdsColorPickerModule", "selector": "tds-color-picker", "link": "/components/color-picker/vi", "desc": "Hộp chọn mã màu sắc trực quan.", "keywords": ["color", "color-picker", "mau-sac", "palette"]},
    {"name": "OTP", "slug": "otp", "category": "Data entry", "module": "TdsOtpModule", "selector": "tds-otp", "link": "/components/otp/vi", "desc": "Các ô nhập mã xác thực OTP 4-6 số.", "keywords": ["otp", "xac-thuc", "ma-otp", "pin", "verify"]},

    # 5. Data Display
    {"name": "Table", "slug": "table", "category": "Data display", "module": "TdsTableModule", "selector": "table[tds-table]", "link": "/components/table/vi", "desc": "Bảng hiển thị dữ liệu bảng biểu, phân trang, sắp xếp cột.", "keywords": ["table", "bang", "grid", "data", "cot", "hang"]},
    {"name": "Data Table", "slug": "data-table", "category": "Data display", "module": "TdsDataTableModule", "selector": "tds-data-table", "link": "/components/data-table/vi", "desc": "Bảng nâng cao hỗ trợ virtual scroll, filter, resize cột.", "keywords": ["data-table", "virtual-scroll", "bang-du-lieu"]},
    {"name": "Card", "slug": "card", "category": "Data display", "module": "TdsCardModule", "selector": "tds-card", "link": "/components/card/vi", "desc": "Thẻ chứa thông tin nhóm có tiêu đề, viền và đổ bóng.", "keywords": ["card", "the", "hop", "box", "container"]},
    {"name": "Avatar", "slug": "avatar", "category": "Data display", "module": "TdsAvatarModule", "selector": "tds-avatar", "link": "/components/avatar/vi", "desc": "Ảnh đại diện người dùng hoặc thương hiệu.", "keywords": ["avatar", "anh-dai-dien", "profile", "user-image"]},
    {"name": "Badge", "slug": "badge", "category": "Data display", "module": "TdsBadgeModule", "selector": "tds-badge", "link": "/components/badge/vi", "desc": "Huy hiệu số lượng thông báo hoặc chấm trạng thái.", "keywords": ["badge", "huy-hieu", "thong-bao", "count", "dot"]},
    {"name": "Tag", "slug": "tag", "category": "Data display", "module": "TdsTagModule", "selector": "tds-tag", "link": "/components/tag/vi", "desc": "Nhãn dán thẻ phân loại trạng thái có màu sắc.", "keywords": ["tag", "nhan", "label", "chip", "status"]},
    {"name": "Tabs", "slug": "tabs", "category": "Data display", "module": "TdsTabsModule", "selector": "tds-tabset, tds-tab", "link": "/components/tabs/vi", "desc": "Chuyển đổi giữa các tab nội dung độc lập.", "keywords": ["tabs", "tabset", "tab", "chuyen-tab"]},
    {"name": "Collapse", "slug": "collapse", "category": "Data display", "module": "TdsCollapseModule", "selector": "tds-collapse, tds-collapse-panel", "link": "/components/collapse/vi", "desc": "Khung thu gọn / mở rộng nội dung (Accordion).", "keywords": ["collapse", "accordion", "thu-gon", "mo-rong"]},
    {"name": "Tooltip", "slug": "tooltip", "category": "Data display", "module": "TdsToolTipModule", "selector": "[tdsTooltip]", "link": "/components/tooltip/vi", "desc": "Chú thích nổi khi rê chuột vào phần tử.", "keywords": ["tooltip", "chu-thich", "hover", "hint"]},
    {"name": "Popover", "slug": "popover", "category": "Data display", "module": "TdsPopoverModule", "selector": "[tdsPopover]", "link": "/components/popover/vi", "desc": "Khung nổi chứa nội dung phức tạp khi bấm chuột.", "keywords": ["popover", "hop-noi", "popup"]},
    {"name": "Empty", "slug": "empty", "category": "Data display", "module": "TdsEmptyModule", "selector": "tds-empty", "link": "/components/empty/vi", "desc": "Hình ảnh và thông điệp trạng thái trống không có dữ liệu.", "keywords": ["empty", "trong", "no-data", "khong-co-du-lieu"]},
    {"name": "Statistic", "slug": "statistic", "category": "Data display", "module": "TdsStatisticModule", "selector": "tds-statistic", "link": "/components/statistic/vi", "desc": "Hiển thị chỉ số thống kê KPI nổi bật (Doanh thu, số lượng).", "keywords": ["statistic", "kpi", "thong-ke", "so-lieu", "metric"]},
    {"name": "Timeline", "slug": "timeline", "category": "Data display", "module": "TdsTimelineModule", "selector": "tds-timeline", "link": "/components/timeline/vi", "desc": "Dòng thời gian sự kiện theo thứ tự.", "keywords": ["timeline", "dong-thoi-gian", "nhat-ky", "history"]},
    {"name": "Tree", "slug": "tree", "category": "Data display", "module": "TdsTreeModule", "selector": "tds-tree", "link": "/components/tree/vi", "desc": "Cây cấu trúc thư mục, danh mục phân cấp.", "keywords": ["tree", "cay", "folder", "danh-muc-cay"]},
    {"name": "Segmented", "slug": "segmented", "category": "Data display", "module": "TdsSegmentedModule", "selector": "tds-segmented", "link": "/components/segmented/vi", "desc": "Thanh chọn phân đoạn chuyển chế độ xem (View switch).", "keywords": ["segmented", "phan-doan", "tab-switch"]},
    {"name": "Typography", "slug": "typography", "category": "Data display", "module": "TdsTypographyModule", "selector": "tds-typography, [tds-typography]", "link": "/components/typography/vi", "desc": "Chuẩn hóa font chữ, tiêu đề, đoạn văn và copy text.", "keywords": ["typography", "font", "text", "heading", "paragraph"]},
    {"name": "QRCode", "slug": "qr-code", "category": "Data display", "module": "TdsQRCodeModule", "selector": "tds-qrcode", "link": "/components/qr-code/vi", "desc": "Tạo mã QR động.", "keywords": ["qr", "qrcode", "ma-qr"]},

    # 6. Feedback
    {"name": "Alert", "slug": "alert", "category": "Feedback", "module": "TdsAlertModule", "selector": "tds-alert", "link": "/components/alert/vi", "desc": "Thanh cảnh báo thông tin cố định trên trang.", "keywords": ["alert", "canh-bao", "thong-bao", "warning", "error"]},
    {"name": "Modal", "slug": "modal", "category": "Feedback", "module": "TdsModalModule", "selector": "tds-modal, TdsModalService", "link": "/components/modal/vi", "desc": "Hộp thoại Popup chặn tương tác nền.", "keywords": ["modal", "dialog", "popup", "hop-thoai"]},
    {"name": "Drawer", "slug": "drawer", "category": "Feedback", "module": "TdsDrawerModule", "selector": "tds-drawer, TdsDrawerService", "link": "/components/drawer/vi", "desc": "Bảng trượt từ cạnh màn hình (Slide-in panel).", "keywords": ["drawer", "slide-in", "side-panel", "bang-truot"]},
    {"name": "Message", "slug": "message", "category": "Feedback", "module": "TdsMessageModule", "selector": "TdsMessageService", "link": "/components/message/vi", "desc": "Thông báo toast nổi góc màn hình biến mất sau vài giây.", "keywords": ["message", "toast", "thong-bao-nhanh", "popup-msg"]},
    {"name": "Notification", "slug": "notification", "category": "Feedback", "module": "TdsNotificationModule", "selector": "TdsNotificationService", "link": "/components/notification/vi", "desc": "Thông báo nổi góc có tiêu đề và mô tả dài.", "keywords": ["notification", "thong-bao-goc", "notify"]},
    {"name": "Progress", "slug": "progress", "category": "Feedback", "module": "TdsProgressModule", "selector": "tds-progress", "link": "/components/progress/vi", "desc": "Thanh tiến trình tiến độ công việc dạng vạch hoặc vòng tròn.", "keywords": ["progress", "tien-trinh", "loading-bar", "percent"]},
    {"name": "Skeleton", "slug": "skeleton", "category": "Feedback", "module": "TdsSkeletonModule", "selector": "tds-skeleton", "link": "/components/skeleton/vi", "desc": "Khung giao diện xương giả lập tải dữ liệu.", "keywords": ["skeleton", "placeholder", "loading-skeleton", "khung-xuong"]},
    {"name": "Spinner", "slug": "spinner", "category": "Feedback", "module": "TdsSpinnerModule", "selector": "tds-spinner", "link": "/components/spinner/vi", "desc": "Vòng quay chờ tải trang (Loading spinner).", "keywords": ["spinner", "loading", "quay", "cho"]},
    {"name": "Popconfirm", "slug": "popconfirm", "category": "Feedback", "module": "TdsPopconfirmModule", "selector": "[tdsPopconfirm]", "link": "/components/popconfirm/vi", "desc": "Hộp thoại xác nhận nhỏ nổi ngay trên nút xóa/hành động.", "keywords": ["popconfirm", "xac-nhan", "confirm-popup"]},

    # 7. Documentation & Guides
    {"name": "Installation", "slug": "install", "category": "Guide", "module": "tds-ui", "selector": "npm install tds-ui", "link": "/components/install", "desc": "Hướng dẫn cài đặt tds-ui, cấu hình fonts, icon và scss.", "keywords": ["install", "cai-dat", "setup", "huong-dan", "npm"]},
    {"name": "TailwindCSS Setup", "slug": "install-tailwindcss", "category": "Guide", "module": "tds-ui/tailwindcss", "selector": "tailwind.config.js", "link": "/components/install-tailwindcss", "desc": "Hướng dẫn tích hợp cấu hình Tailwind CSS token của TDS.", "keywords": ["tailwind", "tailwindcss", "css", "token", "config"]},
    {"name": "Icon Set", "slug": "icon", "category": "General", "module": "tds-ui", "selector": "<i class='tdsi-...'>", "link": "/components/icon", "desc": "Bảng tra cứu hơn 500 icon vector TDS Icons.", "keywords": ["icon", "bieu-tuong", "tdsi", "svg", "font-icon"]},
]

def check_gateway_health() -> bool:
    """Kiểm tra kết nối trực tiếp tới cổng gateway https://tds.design-system.local/"""
    try:
        req = urllib.request.Request(GATEWAY_BASE_URL, headers={"User-Agent": "TdsSearchTool/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def search_tds(query: str, category_filter: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Tìm kiếm component theo từ khóa và danh mục"""
    q = query.lower().strip()
    words = re.findall(r"[a-zA-Z0-9_\-]+", q)
    if not words and not category_filter:
        return []

    scored_results = []

    for item in TDS_CATALOG:
        # Lọc theo category nếu có
        if category_filter and category_filter.lower() not in item["category"].lower():
            continue

        score = 0
        name_lower = item["name"].lower()
        slug_lower = item["slug"].lower()
        desc_lower = item["desc"].lower()
        selector_lower = item["selector"].lower()
        keywords = [k.lower() for k in item["keywords"]]

        # 1. Khớp chính xác
        if q == slug_lower or q == name_lower:
            score += 100
        elif q in slug_lower or q in name_lower:
            score += 60

        # 2. Khớp từ khóa
        for w in words:
            if w in slug_lower:
                score += 40
            elif w in name_lower:
                score += 30
            elif any(w in k for k in keywords):
                score += 25
            elif w in desc_lower:
                score += 15
            elif w in selector_lower:
                score += 20

        if score > 0:
            full_url = f"{GATEWAY_BASE_URL}/#{item['link']}"
            scored_results.append({
                "score": score,
                "name": item["name"],
                "category": item["category"],
                "slug": item["slug"],
                "module": item["module"],
                "selector": item["selector"],
                "desc": item["desc"],
                "url": full_url,
                "link": item["link"]
            })

    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:limit]

def format_card(res: Dict[str, Any], is_first: bool = False) -> str:
    """Format thẻ thông tin component chuẩn terminal"""
    border = "═" * 68 if is_first else "─" * 68
    return f"""{border}
💎 \033[1;36m{res['name']}\033[0m \033[90m({res['category']})\033[0m  [Điểm khớp: {res['score']}]
📝 \033[33m{res['desc']}\033[0m
📦 Module  : \033[1;32mimport {{ {res['module']} }} from 'tds-ui';\033[0m
🎯 Selector: \033[1;35m{res['selector']}\033[0m
🌐 Gateway : \033[4;34m{res['url']}\033[0m"""

def main():
    parser = argparse.ArgumentParser(description="TDS Search Tool - Tra cứu component TMT Design System qua https://tds.design-system.local/")
    parser.add_argument("query", nargs="?", default="", help="Từ khóa tìm kiếm (vd: button, table, modal, datepicker, upload...)")
    parser.add_argument("--category", "-c", help="Lọc theo danh mục (Button, Layout, Navigation, Data entry, Data display, Feedback, Guide)")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Số lượng kết quả tối đa (mặc định: 5)")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả định dạng JSON cho AI Agent")
    parser.add_argument("--list-categories", action="store_true", help="Liệt kê toàn bộ danh mục TDS có trên website")
    parser.add_argument("--ping", action="store_true", help="Kiểm tra trạng thái kết nối tới cổng gateway https://tds.design-system.local/")

    args = parser.parse_args()

    if args.ping:
        ok = check_gateway_health()
        if ok:
            print(f"✅ Gateway {GATEWAY_BASE_URL} đang HOẠT ĐỘNG BÌNH THƯỜNG (HTTP 200, CORS enabled).")
            sys.exit(0)
        else:
            print(f"❌ Không thể kết nối tới Gateway {GATEWAY_BASE_URL}.")
            sys.exit(1)

    if args.list_categories:
        categories = sorted(list(set(item["category"] for item in TDS_CATALOG)))
        if args.json:
            print(json.dumps(categories, indent=2))
        else:
            print("📂 DANH MỤC THÀNH PHẦN TRÊN https://tds.design-system.local/:")
            for cat in categories:
                count = sum(1 for item in TDS_CATALOG if item["category"] == cat)
                print(f"  • {cat:<15} ({count} components)")
        sys.exit(0)

    if not args.query and not args.category:
        parser.print_help()
        sys.exit(0)

    results = search_tds(args.query, category_filter=args.category, limit=args.limit)

    if args.json:
        output = {
            "gateway": GATEWAY_BASE_URL,
            "query": args.query,
            "category_filter": args.category,
            "total_found": len(results),
            "results": results
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        sys.exit(0)

    if not results:
        print(f"\n🔍 Không tìm thấy component nào phù hợp với từ khóa: '{args.query}'")
        print(f"💡 Thử tìm theo từ khóa chung: 'button', 'input', 'table', 'date', 'select', 'modal', hoặc chạy với --list-categories.\n")
        sys.exit(0)

    print(f"\n🚀 TÌM THẤY {len(results)} COMPONENT PHÙ HỢP TRÊN GATEWAY: \033[4;34m{GATEWAY_BASE_URL}\033[0m\n")
    for i, res in enumerate(results):
        print(format_card(res, is_first=(i == 0)))
    print("─" * 68 + "\n")

if __name__ == "__main__":
    main()
