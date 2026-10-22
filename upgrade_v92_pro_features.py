import os
import re

path = r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject CSS for Thread Group Badge, VIP Card Glow, 24h Analytics Bar Chart, and View Mode Toggle
pro_css = """
    /* Pro v9.2: Thread Grouping, VIP Glow, Analytics Chart & Quick Star */
    .view-mode-btn {
      height: 38px;
      padding: 0 12px;
      border-radius: 12px;
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      background: rgba(118, 118, 128, 0.24);
      color: #FFFFFF;
      font-size: 12.5px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      white-space: nowrap;
      flex-shrink: 0;
      transition: all 0.16s ease;
    }
    .view-mode-btn.active {
      background: rgba(10, 132, 255, 0.28);
      border-color: rgba(10, 132, 255, 0.65);
      color: #64D2FF;
    }
    .view-mode-btn svg {
      width: 15px;
      height: 15px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
    }

    .noti-card.vip-card {
      border-color: rgba(255, 159, 10, 0.45);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 0 0 0.5px rgba(255, 159, 10, 0.22);
    }

    .badge-vip {
      background: rgba(255, 159, 10, 0.2);
      color: #FFD60A;
      border: 0.5px solid rgba(255, 214, 10, 0.45);
    }

    .badge-thread-count {
      background: rgba(10, 132, 255, 0.22);
      color: #64D2FF;
      border: 0.5px solid rgba(10, 132, 255, 0.45);
      font-size: 11px;
      font-weight: 700;
      padding: 1.5px 8px;
      border-radius: 999px;
    }

    .quick-star-btn {
      background: none;
      border: none;
      color: rgba(235, 235, 245, 0.28);
      font-size: 15px;
      padding: 2px 4px;
      cursor: pointer;
      line-height: 1;
      transition: transform 0.15s ease, color 0.15s ease;
    }
    .quick-star-btn.starred {
      color: #FFD60A;
    }
    .quick-star-btn:active {
      transform: scale(1.25);
    }

    /* 24h Activity Bar Chart & Top Senders */
    .analytics-hours {
      display: flex;
      align-items: flex-end;
      gap: 3px;
      height: 68px;
      padding: 10px 4px 4px 4px;
      border-bottom: 0.5px solid rgba(255, 255, 255, 0.08);
      margin-bottom: 6px;
    }
    .hour-col {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      height: 100%;
      justify-content: flex-end;
      gap: 3px;
    }
    .hour-bar {
      width: 100%;
      border-radius: 3px 3px 1px 1px;
      background: linear-gradient(180deg, #64D2FF 0%, #0A84FF 100%);
      min-height: 3px;
      transition: height 0.3s ease;
    }
    .hour-label {
      font-size: 9px;
      color: var(--text-muted);
    }
    .stat-bar-row {
      margin-bottom: 9px;
    }
    .stat-bar-top {
      display: flex;
      justify-content: space-between;
      font-size: 12.5px;
      margin-bottom: 4px;
      font-weight: 600;
    }
    .stat-bar-track {
      height: 6px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
      overflow: hidden;
    }
    .stat-bar-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #0A84FF, #5E5CE6);
    }
"""

if "/* Pro v9.2: Thread Grouping" not in html:
    html = html.replace("  </style>", pro_css + "\n  </style>", 1)

# 2. Add Thread Grouping Toggle button to .search-row and VIP tab to #filterTabsBar
old_search_row = """      <!-- Search Row -->
      <div class="search-row">
        <div class="search-input-wrap">
          <span class="search-icon">
            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </span>
          <input
            type="search"
            id="searchInput"
            class="search-input"
            placeholder="Tìm tin nhắn, người gửi, số tiền, OTP..."
            oninput="onSearchChange()"
          />
          <button id="clearSearchBtn" class="clear-search-btn" onclick="clearSearch()">✕</button>
        </div>
      </div>"""

new_search_row = """      <!-- Search Row + Thread Grouping Toggle -->
      <div class="search-row">
        <div class="search-input-wrap">
          <span class="search-icon">
            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </span>
          <input
            type="search"
            id="searchInput"
            class="search-input"
            placeholder="Tìm tin nhắn, người gửi, số tiền, OTP..."
            oninput="onSearchChange()"
          />
          <button id="clearSearchBtn" class="clear-search-btn" onclick="clearSearch()">✕</button>
        </div>
        <button id="btnGroupMode" class="view-mode-btn" onclick="toggleGroupBySender()" title="Gom nhóm theo Người gửi / Hội thoại">
          <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span id="groupModeLabel">Hội thoại</span>
        </button>
      </div>"""

html = html.replace(old_search_row, new_search_row, 1)

old_vip_pill_anchor = """        <button class="tab-pill tab-revoked" data-tab="revoked" onclick="switchTab('revoked')">
          Đã thu hồi <span class="tab-count" id="countRevoked">0</span>
        </button>"""

new_vip_pill_anchor = """        <button class="tab-pill tab-revoked" data-tab="revoked" onclick="switchTab('revoked')">
          Đã thu hồi <span class="tab-count" id="countRevoked">0</span>
        </button>
        <button class="tab-pill" data-tab="vip" onclick="switchTab('vip')">
          🔥 VIP <span class="tab-count" id="countVip">0</span>
        </button>"""

if 'data-tab="vip"' not in html:
    html = html.replace(old_vip_pill_anchor, new_vip_pill_anchor, 1)

# 3. Update version constants and state variables
html = html.replace('const CURRENT_OTA_VERSION_CODE = 5;', 'const CURRENT_OTA_VERSION_CODE = 6;')
html = html.replace('const CURRENT_OTA_VERSION_NAME = "9.1.0-iOS18";', 'const CURRENT_OTA_VERSION_NAME = "9.2.0-Pro";')

old_state = 'let searchQuery = "";'
new_state = """let searchQuery = "";
    let isGroupedBySender = localStorage.getItem("notistar_ios_group_sender") === "1";
    const DEFAULT_VIP_KEYWORDS = ["gấp", "khẩn", "chuyển khoản", "lương", "sếp", "mật khẩu", "hoàn tiền", "quan trọng"];"""

if "isGroupedBySender" not in html:
    html = html.replace(old_state, new_state, 1)

# 4. Add VIP Keywords, Voucher/Tracking Extractor, and Analytics helpers before computeBankingSummary()
pro_helpers_js = r"""
    function getVipKeywords() {
      try {
        const raw = localStorage.getItem("notistar_ios_vip_keywords");
        if (raw) {
          const arr = JSON.parse(raw);
          if (Array.isArray(arr) && arr.length > 0) return arr;
        }
      } catch (e) {}
      return DEFAULT_VIP_KEYWORDS;
    }

    function saveVipKeywords(str) {
      const list = String(str || "")
        .split(",")
        .map((s) => s.trim().toLowerCase())
        .filter(Boolean);
      localStorage.setItem("notistar_ios_vip_keywords", JSON.stringify(list));
      renderApp();
      showToast(`🔥 Đã lưu ${list.length} từ khóa Radar VIP!`);
    }

    function isVipNotification(item) {
      if (item.isStarred) return true;
      const hay = `${item.title || ""} ${getDisplayBody(item)}`.toLowerCase();
      const kws = getVipKeywords();
      return kws.some((kw) => kw && hay.includes(kw));
    }

    function extractTrackingAndPromo(item) {
      const text = `${item.title || ""} ${getDisplayBody(item)}`;
      const trackingMatch = /\b(SPXVN[0-9A-Z]{8,15}|VN[0-9]{9,14}[A-Z0-9]{0,4}|GHN[0-9A-Z]{6,14}|GHTK[0-9A-Z]{6,14}|VTP[0-9A-Z]{6,14})\b/i.exec(text)
        || /(?:mã\s*vận\s*đơn|mã\s*đơn\s*hàng|đơn\s*hàng)\s*[:#]?\s*([A-Z0-9]{8,18})\b/i.exec(text);
      const promoMatch = /(?:mã\s*giảm\s*giá|voucher|nhập\s*mã|code)\s*[:#]?\s*([A-Z0-9]{4,14})\b/i.exec(text);
      return {
        trackingCode: trackingMatch ? trackingMatch[1].toUpperCase() : null,
        promoCode: promoMatch ? promoMatch[1].toUpperCase() : null
      };
    }

    function toggleGroupBySender() {
      isGroupedBySender = !isGroupedBySender;
      localStorage.setItem("notistar_ios_group_sender", isGroupedBySender ? "1" : "0");
      const btn = document.getElementById("btnGroupMode");
      const lbl = document.getElementById("groupModeLabel");
      if (btn) btn.classList.toggle("active", isGroupedBySender);
      if (lbl) lbl.textContent = isGroupedBySender ? "Đang gom" : "Hội thoại";
      renderApp();
      showToast(isGroupedBySender ? "💬 Đã bật Gom nhóm theo Người gửi / Hội thoại" : "📋 Đã chuyển về chế độ Danh sách thời gian");
    }

    function groupNotificationsIntoThreads(list) {
      const map = new Map();
      for (const item of list) {
        const senderKey = `${item.packageName || item.appName}|${(item.title || item.appName || "").trim()}`;
        if (!map.has(senderKey)) {
          map.set(senderKey, {
            latest: item,
            count: 1,
            photosCount: hasMedia(item) ? 1 : 0,
            revokedCount: item.isRevoked ? 1 : 0,
            hasVip: isVipNotification(item)
          });
        } else {
          const entry = map.get(senderKey);
          entry.count++;
          if (hasMedia(item)) entry.photosCount++;
          if (item.isRevoked) entry.revokedCount++;
          if (isVipNotification(item)) entry.hasVip = true;
          if (item.time > entry.latest.time) {
            entry.latest = item;
          }
        }
      }
      return Array.from(map.values()).sort((a, b) => b.latest.time - a.latest.time);
    }

    async function shareConversationThread(uid) {
      const item = allNotifications.find((n) => n.uid === uid);
      if (!item) return;
      const related = allNotifications
        .filter((n) => (n.packageName || n.appName) === (item.packageName || item.appName) && n.title === item.title)
        .sort((a, b) => a.time - b.time);
      const lines = related.map((m) => `[${formatDateTime(m.time)}] ${m.title}${m.isRevoked ? " (ĐÃ THU HỒI)" : ""}: ${getDisplayBody(m)}`);
      const fullText = `=== Lịch sử Hội thoại: ${item.title} (${item.appName}) ===\n` + lines.join("\n");
      if (navigator.share) {
        try {
          await navigator.share({ title: `Hội thoại: ${item.title}`, text: fullText });
          return;
        } catch (e) {}
      }
      copyTextToClipboard(fullText, "📋 Đã sao chép toàn bộ cuộc hội thoại!");
    }
"""

if "function isVipNotification(item)" not in html:
    html = html.replace("    function computeBankingSummary() {", pro_helpers_js + "\n    function computeBankingSummary() {", 1)

# 5. Update renderApp() to support VIP tab and Thread Grouping
old_render_counts = """      // 1. Tính toán số lượng cho 7 Tab & Bento Stats
      const chatList = visibleNotifications.filter(isChatNotification);
      const revokedList = visibleNotifications.filter((n) => n.isRevoked);
      const starredList = visibleNotifications.filter((n) => n.isStarred);
      const mediaList = visibleNotifications.filter(hasMedia);
      const bankSummary = computeBankingSummary();
      const linksList = visibleNotifications.filter((n) => extractLinksPhonesEmails(n).hasAny);"""

new_render_counts = """      // 1. Tính toán số lượng cho các Tab
      const chatList = visibleNotifications.filter(isChatNotification);
      const revokedList = visibleNotifications.filter((n) => n.isRevoked);
      const vipList = visibleNotifications.filter(isVipNotification);
      const starredList = visibleNotifications.filter((n) => n.isStarred);
      const mediaList = visibleNotifications.filter(hasMedia);
      const bankSummary = computeBankingSummary();
      const linksList = visibleNotifications.filter((n) => extractLinksPhonesEmails(n).hasAny);
      setText("countVip", vipList.length);
      const grpBtn = document.getElementById("btnGroupMode");
      const grpLbl = document.getElementById("groupModeLabel");
      if (grpBtn) grpBtn.classList.toggle("active", isGroupedBySender);
      if (grpLbl) grpLbl.textContent = isGroupedBySender ? "Đang gom" : "Hội thoại";"""

html = html.replace(old_render_counts, new_render_counts, 1)

html = html.replace(
    'else if (currentTab === "revoked") filtered = revokedList;',
    'else if (currentTab === "revoked") filtered = revokedList;\n      else if (currentTab === "vip") filtered = vipList;',
    1
)

old_loop_render = """      let lastDateHeader = "";
      for (const item of filtered.slice(0, 250)) {
        const dHeader = getFriendlyDateHeader(item.time);
        if (dHeader !== lastDateHeader) {
          lastDateHeader = dHeader;
          htmlParts.push(`
            <div class="date-group-header">
              <span>${escapeHtml(dHeader)}</span>
            </div>
          `);
        }
        htmlParts.push(renderNotificationCardHtml(item));
      }"""

new_loop_render = """      if (isGroupedBySender && currentTab !== "media") {
        const threads = groupNotificationsIntoThreads(filtered);
        htmlParts.push(`
          <div class="date-group-header">
            <span>Đang gom ${filtered.length} thông báo thành ${threads.length} cuộc hội thoại</span>
          </div>
        `);
        for (const th of threads.slice(0, 180)) {
          htmlParts.push(renderNotificationCardHtml(th.latest, th));
        }
      } else {
        let lastDateHeader = "";
        for (const item of filtered.slice(0, 250)) {
          const dHeader = getFriendlyDateHeader(item.time);
          if (dHeader !== lastDateHeader) {
            lastDateHeader = dHeader;
            htmlParts.push(`
              <div class="date-group-header">
                <span>${escapeHtml(dHeader)}</span>
              </div>
            `);
          }
          htmlParts.push(renderNotificationCardHtml(item, null));
        }
      }"""

html = html.replace(old_loop_render, new_loop_render, 1)

# 6. Upgrade renderNotificationCardHtml(item, threadMeta) to show Thread count, VIP badge, Tracking/Promo chips, and 1-tap Star
old_card_fn = re.search(
    r"function renderNotificationCardHtml\(item\).*?function openNotificationDetail\(uid\)",
    html,
    flags=re.S
)

new_card_fn = """function renderNotificationCardHtml(item, threadMeta = null) {
      const body = getDisplayBody(item);
      const otp = extractOtp(item);
      const tx = extractBankTransaction(item);
      const extracted = extractLinksPhonesEmails(item);
      const trackPromo = extractTrackingAndPromo(item);
      const isVip = isVipNotification(item);
      const avatarHtml = renderAppAvatarHtml(item, tx);

      const badges = [];
      if (threadMeta && threadMeta.count > 1) {
        badges.push(`<span class="badge-thread-count">${threadMeta.count} tin nhắn</span>`);
      }
      if (item.isRevoked || (threadMeta && threadMeta.revokedCount > 0)) {
        badges.push(`<span class="pill-badge badge-revoked">Đã thu hồi</span>`);
      }
      if (isVip) {
        badges.push(`<span class="pill-badge badge-vip">🔥 VIP</span>`);
      }
      if (tx) {
        badges.push(
          tx.isIncome
            ? `<span class="pill-badge badge-bank-in">${escapeHtml(tx.bankName)} ${formatVnd(tx.amountVnd, true)}</span>`
            : `<span class="pill-badge badge-bank-out">${escapeHtml(tx.bankName)} ${formatVnd(-tx.amountVnd, true)}</span>`
        );
      }

      // Media Picture
      let mediaHtml = "";
      const mediaB64 = getItemMediaB64(item);
      if (mediaB64) {
        const src = formatB64Src(mediaB64);
        mediaHtml = `
          <div class="card-media-wrap" onclick="event.stopPropagation(); openLightbox('${escapeAttr(src)}')">
            <img class="card-media-img" src="${src}" alt="Ảnh đính kèm" loading="lazy" />
            <span class="media-zoom-pill">Xem ảnh</span>
          </div>
        `;
      }

      // Contextual Smart Chips (OTP, Tracking Code, Promo Code, Phone, Link)
      const chips = [];
      if (otp) {
        chips.push(`
          <button class="otp-copy-btn" onclick="event.stopPropagation(); copyTextToClipboard('${escapeAttr(otp)}', 'Đã sao chép OTP: ${escapeAttr(otp)}')">
            Sao chép OTP: ${escapeHtml(otp)}
          </button>
        `);
      }
      if (trackPromo.trackingCode && trackPromo.trackingCode !== otp) {
        chips.push(`
          <button class="smart-chip" style="color:#64D2FF;border-color:rgba(100,210,255,0.4);" onclick="event.stopPropagation(); copyTextToClipboard('${escapeAttr(trackPromo.trackingCode)}', 'Đã chép mã vận đơn: ${escapeAttr(trackPromo.trackingCode)}')">
            📦 Mã đơn: ${escapeHtml(trackPromo.trackingCode)}
          </button>
        `);
      }
      if (trackPromo.promoCode && trackPromo.promoCode !== otp && trackPromo.promoCode !== trackPromo.trackingCode) {
        chips.push(`
          <button class="smart-chip" style="color:#FFD60A;border-color:rgba(255,214,10,0.4);" onclick="event.stopPropagation(); copyTextToClipboard('${escapeAttr(trackPromo.promoCode)}', 'Đã chép mã KM: ${escapeAttr(trackPromo.promoCode)}')">
            🎫 Mã: ${escapeHtml(trackPromo.promoCode)}
          </button>
        `);
      }
      for (const phone of extracted.phones.slice(0, 2)) {
        chips.push(`
          <a class="smart-chip" href="tel:${escapeAttr(phone)}" onclick="event.stopPropagation()">
            Gọi ${escapeHtml(phone)}
          </a>
        `);
      }
      for (const url of extracted.urls.slice(0, 1)) {
        let shortHost = url;
        try { shortHost = new URL(url).hostname.replace(/^www\\./, ""); } catch (e) {}
        chips.push(`
          <a class="smart-chip" href="${escapeAttr(url)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">
            Mở ${escapeHtml(shortHost)}
          </a>
        `);
      }

      const chipsBarHtml = chips.length > 0 ? `<div class="smart-actions-bar">${chips.join("")}</div>` : "";
      const cardCls = [
        "noti-card",
        item.isRevoked ? "revoked" : "",
        isVip && !item.isRevoked ? "vip-card" : ""
      ].filter(Boolean).join(" ");

      return `
        <article class="${cardCls}" onclick="openNotificationDetail('${escapeAttr(item.uid)}')">
          <div class="noti-row">
            ${avatarHtml}
            <div class="noti-main">
              <div class="noti-header-line">
                <div class="card-title selectable">${escapeHtml(item.title || item.appName)}</div>
                <div class="card-time-wrap">
                  <span class="card-time">${formatShortSmartTime(item.time)}</span>
                  <button class="quick-star-btn ${item.isStarred ? "starred" : ""}" onclick="event.stopPropagation(); toggleStarByUid('${escapeAttr(item.uid)}')" title="Ghim quan trọng">
                    ${item.isStarred ? "★" : "☆"}
                  </button>
                </div>
              </div>
              <div class="card-subline">
                <span class="app-name-label">${escapeHtml(item.appName)}</span>
                ${badges.join("")}
              </div>
              <div class="card-body selectable">${escapeHtml(body)}</div>
              ${mediaHtml}
              ${chipsBarHtml}
            </div>
          </div>
        </article>
      `;
    }

    function openNotificationDetail(uid)"""

if old_card_fn:
    html = html[:old_card_fn.start()] + new_card_fn + html[old_card_fn.end():]

# 7. Add Share Conversation button inside openNotificationDetail()
html = html.replace(
    """          <button class="sheet-action-btn" onclick="deleteNotificationByUid('${escapeAttr(item.uid)}'); closeModal('detailModal')">
            <span style="color:#FF6961;">Xóa tin</span>
          </button>
        </div>""",
    """          <button class="sheet-action-btn" onclick="shareConversationThread('${escapeAttr(item.uid)}')">
            <span style="color:#64D2FF;">Chia sẻ</span>
          </button>
        </div>
        <div style="display:flex;justify-content:flex-end;margin-top:-6px;margin-bottom:8px;">
          <button class="smart-chip" style="color:#FF6961;border-color:rgba(255,69,58,0.35);" onclick="deleteNotificationByUid('${escapeAttr(item.uid)}'); closeModal('detailModal')">
            🗑️ Xóa thông báo này
          </button>
        </div>""",
    1
)

# 8. Add 24h Activity Chart, Top Senders, and VIP Keyword Radar Editor to renderManagementViewHtml()
analytics_builder_js = """
      // Tính toán Biểu đồ 24h & Top Người gửi
      const hourBuckets = new Array(24).fill(0);
      const senderMap = new Map();
      for (const n of allNotifications) {
        const hr = new Date(Number(n.time) || Date.now()).getHours();
        if (hr >= 0 && hr < 24) hourBuckets[hr]++;
        const sTitle = (n.title || "").trim();
        if (sTitle && sTitle !== n.appName) {
          const sKey = `${sTitle} (${n.appName})`;
          senderMap.set(sKey, (senderMap.get(sKey) || 0) + 1);
        }
      }
      const maxHourCount = Math.max(...hourBuckets, 1);
      const hoursHtml = hourBuckets.map((cnt, hr) => {
        const pct = Math.max(Math.round((cnt / maxHourCount) * 100), 6);
        const showLbl = hr % 4 === 0 ? `${hr}h` : "";
        return `
          <div class="hour-col" title="${hr}:00 - ${cnt} thông báo">
            <div class="hour-bar" style="height:${pct}%;opacity:${cnt > 0 ? 1 : 0.22};"></div>
            <span class="hour-label">${showLbl}</span>
          </div>
        `;
      }).join("");

      const topSenders = Array.from(senderMap.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5);
      const maxSenderCnt = topSenders.length > 0 ? topSenders[0][1] : 1;
      const topSendersHtml = topSenders.map(([sName, sCnt]) => {
        const wPct = Math.round((sCnt / maxSenderCnt) * 100);
        return `
          <div class="stat-bar-row">
            <div class="stat-bar-top">
              <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:75%;">${escapeHtml(sName)}</span>
              <span style="color:#64D2FF;">${sCnt} tin</span>
            </div>
            <div class="stat-bar-track">
              <div class="stat-bar-fill" style="width:${wPct}%;"></div>
            </div>
          </div>
        `;
      }).join("");
      const currentVipStr = getVipKeywords().join(", ");
"""

if "const hourBuckets = new Array(24).fill(0);" not in html:
    html = html.replace(
        '      const apps = Array.from(appMap.values()).sort((a, b) => b.count - a.count);',
        '      const apps = Array.from(appMap.values()).sort((a, b) => b.count - a.count);\n' + analytics_builder_js,
        1
    )

analytics_cards_html = """        <div class="mgmt-section">
          <div class="mgmt-section-title">
            <span>📊 Phân tích Hoạt động 24 Giờ &amp; Top Liên hệ</span>
            <span style="font-size:11.5px;color:var(--text-secondary);">${allNotifications.length} thông báo</span>
          </div>
          <p class="mgmt-section-sub" style="margin-bottom:6px;">
            Biểu đồ mật độ thông báo theo khung giờ trong ngày và Top 5 người/nhóm nhắn nhiều nhất:
          </p>
          <div class="analytics-hours">${hoursHtml}</div>
          <div style="margin-top:12px;">
            ${topSendersHtml || '<div style="font-size:12px;color:var(--text-secondary);">Chưa có dữ liệu người gửi.</div>'}
          </div>
        </div>

        <div class="mgmt-section">
          <div class="mgmt-section-title">
            <span>🔥 Radar Từ khóa Khẩn cấp / VIP</span>
          </div>
          <p class="mgmt-section-sub">
            Tự động gắn nhãn <strong>🔥 VIP</strong> và đưa vào tab VIP khi tin nhắn chứa các từ khóa này (cách nhau bằng dấu phẩy):
          </p>
          <div style="display:flex;gap:8px;">
            <input type="text" id="vipKeywordsInput" class="form-input" value="${escapeAttr(currentVipStr)}" placeholder="gấp, khẩn, chuyển khoản, sếp..." />
            <button class="btn btn-primary" style="flex:0 0 auto;width:auto;" onclick="saveVipKeywords(document.getElementById('vipKeywordsInput').value)">
              Lưu
            </button>
          </div>
        </div>
"""

if "Phân tích Hoạt động 24 Giờ" not in html:
    html = html.replace(
        '<div class="mgmt-section">\n          <div class="mgmt-section-title">\n            <span>🛠️ Sửa lỗi Báo thu hồi nhầm &amp; Dọn dẹp</span>',
        analytics_cards_html + '\n        <div class="mgmt-section">\n          <div class="mgmt-section-title">\n            <span>🛠️ Sửa lỗi Báo thu hồi nhầm &amp; Dọn dẹp</span>',
        1
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully upgraded WebApp_PWA/index.html with v9.2.0-Pro features! Size:", os.path.getsize(path))
