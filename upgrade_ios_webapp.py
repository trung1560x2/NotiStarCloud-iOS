import os

path = r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject new CSS for Photo Gallery Grid, Management Center, App Switches, and hide bulky Bento grid by default
extra_css = """
    /* Hide noisy Bento grid on main feed to keep UI ultra-clean */
    .bento-stats {
      display: none !important;
    }

    /* Photo Gallery Grid in Kho Ảnh Tab */
    .photo-gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(145px, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    .photo-grid-item {
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      background: #141724;
      border: 1px solid rgba(255, 255, 255, 0.1);
      aspect-ratio: 4 / 3;
      cursor: pointer;
    }
    .photo-grid-item img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .photo-grid-caption {
      position: absolute;
      inset: auto 0 0 0;
      padding: 6px 8px;
      background: linear-gradient(transparent, rgba(0, 0, 0, 0.88));
      font-size: 11px;
      color: #F8FAFC;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 600;
    }

    /* Management Screen (Màn Quản lý) */
    .mgmt-section {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 16px;
      margin-bottom: 12px;
    }
    .mgmt-section-title {
      font-size: 15px;
      font-weight: 800;
      color: var(--text-primary);
      margin: 0 0 6px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .mgmt-section-sub {
      font-size: 12px;
      color: var(--text-secondary);
      margin: 0 0 12px 0;
      line-height: 1.45;
    }
    .app-mgmt-row {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .app-mgmt-row:last-child {
      border-bottom: none;
    }
    .app-mgmt-info {
      flex: 1;
      min-width: 0;
    }
    .app-mgmt-name {
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-primary);
    }
    .app-mgmt-meta {
      font-size: 11.5px;
      color: var(--text-secondary);
    }
    .ota-banner {
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.22), rgba(124, 58, 237, 0.22));
      border: 1px solid rgba(96, 165, 250, 0.45);
      border-radius: 18px;
      padding: 14px;
      margin-bottom: 12px;
    }
"""

html = html.replace("  </style>", extra_css + "\n  </style>", 1)

# 2. Add "⚙️ Quản lý" tab to filterTabsBar & bottom-dock
old_tabs = """        <button class="tab-pill" data-tab="links" onclick="switchTab('links')">
          🔗 Link &amp; SĐT <span class="tab-count" id="countLinks">0</span>
        </button>
      </div>"""

new_tabs = """        <button class="tab-pill" data-tab="links" onclick="switchTab('links')">
          🔗 Link &amp; SĐT <span class="tab-count" id="countLinks">0</span>
        </button>
        <button class="tab-pill" data-tab="manage" onclick="switchTab('manage')">
          ⚙️ Quản lý
        </button>
      </div>"""
html = html.replace(old_tabs, new_tabs, 1)

old_dock = """  <!-- iOS Floating Bottom Dock -->
  <nav class="bottom-dock">
    <button class="dock-btn active" id="dockAll" onclick="switchTab('all')">
      <span class="dock-icon">📥</span>
      <span>Hộp thư</span>
    </button>
    <button class="dock-btn" id="dockRevoked" onclick="switchTab('revoked')">
      <span class="dock-icon">🚫</span>
      <span>Thu hồi</span>
    </button>
    <button class="dock-btn dock-btn-primary" onclick="openModal('captureModal')">
      <span class="dock-icon">➕</span>
      <span>Lưu nhanh</span>
    </button>
    <button class="dock-btn" id="dockBank" onclick="switchTab('bank')">
      <span class="dock-icon">🏦</span>
      <span>Ngân hàng</span>
    </button>
    <button class="dock-btn" id="dockCloud" onclick="openModal('cloudModal')">
      <span class="dock-icon">☁️</span>
      <span>Google Drive</span>
    </button>
  </nav>"""

new_dock = """  <!-- iOS Floating Bottom Dock -->
  <nav class="bottom-dock">
    <button class="dock-btn active" id="dockAll" onclick="switchTab('all')">
      <span class="dock-icon">📥</span>
      <span>Tất cả</span>
    </button>
    <button class="dock-btn" id="dockRevoked" onclick="switchTab('revoked')">
      <span class="dock-icon">🚫</span>
      <span>Thu hồi</span>
    </button>
    <button class="dock-btn" id="dockMedia" onclick="switchTab('media')">
      <span class="dock-icon">🖼️</span>
      <span>Kho Ảnh</span>
    </button>
    <button class="dock-btn" id="dockBank" onclick="switchTab('bank')">
      <span class="dock-icon">🏦</span>
      <span>Ngân hàng</span>
    </button>
    <button class="dock-btn" id="dockManage" onclick="switchTab('manage')">
      <span class="dock-icon">⚙️</span>
      <span>Quản lý</span>
    </button>
  </nav>"""
html = html.replace(old_dock, new_dock, 1)

# 3. Update STORAGE_KEYS and add APP_VERSION
old_keys = """      PIN_CODE: "notistar_ios_pin_code",
      FALLBACK_ITEMS: "notistar_ios_items_backup_v1"
    };"""

new_keys = """      PIN_CODE: "notistar_ios_pin_code",
      FALLBACK_ITEMS: "notistar_ios_items_backup_v2",
      BLOCKED_APPS: "notistar_ios_blocked_apps_v1",
      OTA_VERSION: "notistar_ios_ota_version_code",
      CLEANED_V3: "notistar_ios_cleaned_false_revoked_v3"
    };
    const CURRENT_OTA_VERSION_CODE = 3;
    const CURRENT_OTA_VERSION_NAME = "9.0.82-OTA";"""
html = html.replace(old_keys, new_keys, 1)

# 4. Fix hasMedia(item) so it only matches real photos (pictureB64 or "Ảnh" with largeIconB64)
old_has_media = """    function hasMedia(item) {
      return Boolean(
        (item.pictureB64 && item.pictureB64.length > 20) ||
        (item.largeIconB64 && item.largeIconB64.length > 200)
      );
    }"""

new_has_media = """    function getItemMediaB64(item) {
      if (item.pictureB64 && item.pictureB64.length > 50) {
        return item.pictureB64;
      }
      const txt = `${item.contentText || ""} ${item.bigText || ""}`.trim();
      if ((txt === "Ảnh" || txt === "Hình ảnh" || txt.includes("🖼") || txt.includes("📷")) && item.largeIconB64 && item.largeIconB64.length > 100) {
        return item.largeIconB64;
      }
      return "";
    }

    function formatB64Src(b64) {
      if (!b64) return "";
      if (b64.startsWith("data:")) return b64;
      const mime = b64.startsWith("iVBOR") ? "image/png" : "image/jpeg";
      return `data:${mime};base64,${b64}`;
    }

    function hasMedia(item) {
      return getItemMediaB64(item).length > 50;
    }

    function getBlockedAppsSet() {
      try {
        const raw = localStorage.getItem(STORAGE_KEYS.BLOCKED_APPS);
        if (raw) return new Set(JSON.parse(raw));
      } catch (e) {}
      return new Set();
    }

    function saveBlockedAppsSet(setObj) {
      try {
        localStorage.setItem(STORAGE_KEYS.BLOCKED_APPS, JSON.stringify(Array.from(setObj)));
      } catch (e) {}
    }"""
html = html.replace(old_has_media, new_has_media, 1)

# 5. Fix normalizeNotification(raw) & computeNotificationUid(item) & mergeIncomingNotifications
old_norm = """    function computeNotificationUid(item) {
      if (item.uid) return item.uid;
      const t = item.time || 0;
      const pkg = item.packageName || item.appName || "app";
      const title = (item.title || "").slice(0, 40);
      const body = getDisplayBody(item).slice(0, 60);
      return `${pkg}_${t}_${title}_${body}`.replace(/\\s+/g, "_");
    }

    function normalizeNotification(raw) {
      const time = Number(raw.time) || Date.now();
      const bodyText = raw.contentText || raw.body || "";
      const bigText = raw.bigText || bodyText;
      const isRevoked = Boolean(
        raw.isRevoked ||
        /thu hồi|đã xóa tin nhắn|unsent a message|removed a message/i.test(`${raw.title || ""} ${bigText}`)
      );"""

new_norm = """    function computeNotificationUid(item) {
      const pkg = (item.packageName || item.appName || "app").trim();
      const title = (item.title || "").trim().slice(0, 60);
      const body = getDisplayBody(item).trim().slice(0, 90);
      return `${pkg}|${title}|${body}`.replace(/\\s+/g, "_");
    }

    function normalizeNotification(raw) {
      const time = Number(raw.time) || Date.now();
      const bodyText = raw.contentText || raw.body || "";
      const bigText = raw.bigText || bodyText;
      // Chỉ giữ trạng thái thu hồi thật, không tự ý regex "thu hồi" trong nội dung chat thường
      const isRevoked = Boolean(raw.isRevoked);"""
html = html.replace(old_norm, new_norm, 1)

# 6. Update mergeIncomingNotifications to ignore self-spam and always keep pictureB64
old_merge = """      for (const raw of incomingList) {
        const norm = normalizeNotification(raw);
        const existing = map.get(norm.uid);
        if (!existing) {
          map.set(norm.uid, norm);
          addedCount++;
          newlyArrived.push(norm);
        } else {
          // Giữ trạng thái isRevoked hoặc isStarred nếu bản mới được cập nhật
          if (norm.isRevoked && !existing.isRevoked) {
            existing.isRevoked = true;
            newlyArrived.push(existing);
          }
          if (norm.pictureB64 && !existing.pictureB64) {
            existing.pictureB64 = norm.pictureB64;
          }
          if (norm.isStarred) {
            existing.isStarred = true;
          }
        }
      }"""

new_merge = """      for (const raw of incomingList) {
        if (raw.packageName === "com.notistar.cloud" && String(raw.title || "").startsWith("🚨")) {
          continue;
        }
        const norm = normalizeNotification(raw);
        const existing = map.get(norm.uid);
        if (!existing) {
          map.set(norm.uid, norm);
          addedCount++;
          newlyArrived.push(norm);
        } else {
          if (norm.time > existing.time) {
            existing.time = norm.time;
            existing.dateStr = norm.dateStr;
          }
          if (norm.pictureB64 && (!existing.pictureB64 || norm.pictureB64.length > existing.pictureB64.length)) {
            existing.pictureB64 = norm.pictureB64;
          }
          if (norm.largeIconB64 && !existing.largeIconB64) {
            existing.largeIconB64 = norm.largeIconB64;
          }
          if (norm.isStarred) {
            existing.isStarred = true;
          }
        }
      }"""
html = html.replace(old_merge, new_merge, 1)

# 7. Update switchTab, renderApp, and renderNotificationCardHtml to support Photo Gallery Grid, Management Center, and OTA
old_switch = """    function switchTab(tab) {
      currentTab = tab;
      document.querySelectorAll(".tab-pill").forEach((btn) => {
        btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
      });
      document.getElementById("dockAll")?.classList.toggle("active", tab === "all");
      document.getElementById("dockRevoked")?.classList.toggle("active", tab === "revoked");
      document.getElementById("dockBank")?.classList.toggle("active", tab === "bank");
      renderApp();
    }"""

new_switch = """    function switchTab(tab) {
      currentTab = tab;
      document.querySelectorAll(".tab-pill").forEach((btn) => {
        btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
      });
      document.getElementById("dockAll")?.classList.toggle("active", tab === "all");
      document.getElementById("dockRevoked")?.classList.toggle("active", tab === "revoked");
      document.getElementById("dockMedia")?.classList.toggle("active", tab === "media");
      document.getElementById("dockBank")?.classList.toggle("active", tab === "bank");
      document.getElementById("dockManage")?.classList.toggle("active", tab === "manage");
      renderApp();
    }"""
html = html.replace(old_switch, new_switch, 1)

old_render = """    function renderApp() {
      // 1. Tính toán số lượng cho 7 Tab & Bento Stats
      const chatList = allNotifications.filter(isChatNotification);
      const revokedList = allNotifications.filter((n) => n.isRevoked);
      const starredList = allNotifications.filter((n) => n.isStarred);
      const mediaList = allNotifications.filter(hasMedia);
      const bankSummary = computeBankingSummary();
      const linksList = allNotifications.filter((n) => extractLinksPhonesEmails(n).hasAny);"""

new_render = """    function renderApp() {
      const blockedSet = getBlockedAppsSet();
      const visibleNotifications = allNotifications.filter((n) => !blockedSet.has(n.packageName || n.appName));

      // 1. Tính toán số lượng cho 7 Tab & Bento Stats
      const chatList = visibleNotifications.filter(isChatNotification);
      const revokedList = visibleNotifications.filter((n) => n.isRevoked);
      const starredList = visibleNotifications.filter((n) => n.isStarred);
      const mediaList = visibleNotifications.filter(hasMedia);
      const bankSummary = computeBankingSummary();
      const linksList = visibleNotifications.filter((n) => extractLinksPhonesEmails(n).hasAny);"""
html = html.replace(old_render, new_render, 1)

old_filter_block = """      // 2. Hiển thị Sổ phụ Ngân hàng khi ở tab Ngân hàng (hoặc khi có giao dịch và ở tab bank)
      const bankPanel = document.getElementById("bankingLedgerPanel");
      if (bankPanel) {
        const showBankPanel = currentTab === "bank" || (currentTab === "all" && bankSummary.bankItems.length > 0);
        bankPanel.classList.toggle("visible", showBankPanel);"""

new_filter_block = """      setText("countAll", visibleNotifications.length);

      // 2. Chỉ hiển thị Sổ phụ Ngân hàng khi ở tab Ngân hàng để giao diện gọn đẹp
      const bankPanel = document.getElementById("bankingLedgerPanel");
      if (bankPanel) {
        const showBankPanel = currentTab === "bank";
        bankPanel.classList.toggle("visible", showBankPanel);"""
html = html.replace(old_filter_block, new_filter_block, 1)

old_list_render = """      // 3. Lọc danh sách theo Tab + Tìm kiếm
      let filtered = allNotifications;
      if (currentTab === "chat") filtered = chatList;
      else if (currentTab === "revoked") filtered = revokedList;
      else if (currentTab === "starred") filtered = starredList;
      else if (currentTab === "media") filtered = mediaList;
      else if (currentTab === "bank") {
        filtered = bankSummary.bankItems
          .filter((entry) => currentBankFilter === "ALL" || entry.tx.bankName === currentBankFilter)
          .map((entry) => entry.item);
      } else if (currentTab === "links") {
        filtered = linksList;
      }

      if (searchQuery) {
        filtered = filtered.filter((item) => {
          const hay = `${item.appName} ${item.packageName} ${item.title} ${getDisplayBody(item)} ${item.dateStr}`.toLowerCase();
          return hay.includes(searchQuery);
        });
      }

      // 4. Render danh sách thẻ thông báo
      const container = document.getElementById("notiListContainer");
      if (!container) return;

      if (filtered.length === 0) {"""

new_list_render = """      const container = document.getElementById("notiListContainer");
      if (!container) return;

      // Nếu đang ở Tab Quản lý (⚙️ Quản lý)
      if (currentTab === "manage") {
        container.innerHTML = renderManagementViewHtml();
        return;
      }

      // 3. Lọc danh sách theo Tab + Tìm kiếm
      let filtered = visibleNotifications;
      if (currentTab === "chat") filtered = chatList;
      else if (currentTab === "revoked") filtered = revokedList;
      else if (currentTab === "starred") filtered = starredList;
      else if (currentTab === "media") filtered = mediaList;
      else if (currentTab === "bank") {
        filtered = bankSummary.bankItems
          .filter((entry) => currentBankFilter === "ALL" || entry.tx.bankName === currentBankFilter)
          .map((entry) => entry.item);
      } else if (currentTab === "links") {
        filtered = linksList;
      }

      if (searchQuery) {
        filtered = filtered.filter((item) => {
          const hay = `${item.appName} ${item.packageName} ${item.title} ${getDisplayBody(item)} ${item.dateStr}`.toLowerCase();
          return hay.includes(searchQuery);
        });
      }

      if (filtered.length === 0) {"""
html = html.replace(old_list_render, new_list_render, 1)

old_cards_loop = """      const htmlParts = [];
      for (const item of filtered.slice(0, 300)) {
        htmlParts.push(renderNotificationCardHtml(item));
      }
      container.innerHTML = htmlParts.join("");
    }"""

new_cards_loop = """      const htmlParts = [];
      if (currentTab === "media" && filtered.length > 0) {
        htmlParts.push(renderPhotoGalleryGridHtml(filtered));
      }
      for (const item of filtered.slice(0, 250)) {
        htmlParts.push(renderNotificationCardHtml(item));
      }
      container.innerHTML = htmlParts.join("");
    }

    function renderPhotoGalleryGridHtml(mediaItems) {
      const cells = [];
      for (const item of mediaItems.slice(0, 60)) {
        const b64 = getItemMediaB64(item);
        if (!b64) continue;
        const src = formatB64Src(b64);
        cells.push(`
          <div class="photo-grid-item" onclick="openLightbox('${escapeAttr(src)}')">
            <img src="${src}" alt="${escapeAttr(item.title)}" loading="lazy" />
            <div class="photo-grid-caption">${escapeHtml(item.appName)} • ${escapeHtml(item.title)}</div>
          </div>
        `);
      }
      if (cells.length === 0) return "";
      return `
        <div class="mgmt-section" style="padding:12px;">
          <div class="mgmt-section-title" style="font-size:13.5px;margin-bottom:8px;">
            <span>🖼️ Thư viện Hình ảnh đã bắt (${cells.length} ảnh)</span>
            <span style="font-size:11px;color:var(--text-secondary);">Chạm vào ảnh để phóng to</span>
          </div>
          <div class="photo-gallery-grid">${cells.join("")}</div>
        </div>
      `;
    }"""
html = html.replace(old_cards_loop, new_cards_loop, 1)

# 8. Update mediaHtml and action chips inside renderNotificationCardHtml
old_card_media = """      // Media Picture
      let mediaHtml = "";
      if (item.pictureB64 && item.pictureB64.length > 20) {
        const src = item.pictureB64.startsWith("data:")
          ? item.pictureB64
          : `data:image/jpeg;base64,${item.pictureB64}`;
        mediaHtml = `
          <div class="card-media-wrap">
            <img class="card-media-img" src="${src}" alt="Ảnh đính kèm" onclick="openLightbox('${escapeAttr(src)}')" />
          </div>
        `;
      }"""

new_card_media = """      // Media Picture (hỗ trợ cả pictureB64 và ảnh thu nhỏ largeIconB64 cho tin nhắn Ảnh)
      let mediaHtml = "";
      const mediaB64 = getItemMediaB64(item);
      if (mediaB64) {
        const src = formatB64Src(mediaB64);
        mediaHtml = `
          <div class="card-media-wrap">
            <img class="card-media-img" src="${src}" alt="Ảnh đính kèm" loading="lazy" onclick="openLightbox('${escapeAttr(src)}')" />
          </div>
        `;
      }"""
html = html.replace(old_card_media, new_card_media, 1)

old_card_chips = """      chips.push(`
        <button class="smart-chip" onclick="speakNotificationByUid('${escapeAttr(item.uid)}')">
          🔊 Đọc
        </button>
      `);"""

new_card_chips = """      chips.push(`
        <button class="smart-chip" onclick="speakNotificationByUid('${escapeAttr(item.uid)}')">
          🔊 Đọc
        </button>
      `);
      chips.push(`
        <button class="smart-chip" onclick="toggleRevokedByUid('${escapeAttr(item.uid)}')">
          ${item.isRevoked ? "✅ Bỏ báo thu hồi" : "🚫 Báo thu hồi"}
        </button>
      `);
      chips.push(`
        <button class="smart-chip" style="color:#FCA5A5;" onclick="deleteNotificationByUid('${escapeAttr(item.uid)}')">
          🗑️ Xóa
        </button>
      `);"""
html = html.replace(old_card_chips, new_card_chips, 1)

# 9. Add Management View, Per-App Controls, Reset False Revoked, Direct iOS Photo Upload, and OTA Auto-Update Functions
mgmt_and_ota_js = """
    async function toggleRevokedByUid(uid) {
      const target = allNotifications.find((n) => n.uid === uid);
      if (!target) return;
      target.isRevoked = !target.isRevoked;
      await saveAllToLocalDb(allNotifications);
      renderApp();
      showToast(target.isRevoked ? "🚫 Đã đánh dấu là Tin nhắn thu hồi" : "✅ Đã chuyển về tin nhắn thường");
    }

    async function deleteNotificationByUid(uid) {
      allNotifications = allNotifications.filter((n) => n.uid !== uid);
      await saveAllToLocalDb(allNotifications);
      renderApp();
      showToast("🗑️ Đã xóa thông báo");
    }

    async function toggleBlockApp(appKey) {
      const setObj = getBlockedAppsSet();
      if (setObj.has(appKey)) {
        setObj.delete(appKey);
        showToast(`✅ Đã hiển thị lại thông báo từ ${appKey}`);
      } else {
        setObj.add(appKey);
        showToast(`🚫 Đã ẩn/chặn thông báo từ ${appKey}`);
      }
      saveBlockedAppsSet(setObj);
      renderApp();
    }

    async function deleteNotificationsByApp(appKey, appLabel) {
      const before = allNotifications.length;
      allNotifications = allNotifications.filter((n) => (n.packageName || n.appName) !== appKey);
      const removed = before - allNotifications.length;
      await saveAllToLocalDb(allNotifications);
      renderApp();
      showToast(`🗑️ Đã xóa ${removed} thông báo của ${appLabel}`);
    }

    async function resetAllFalseRevokedItems() {
      let fixed = 0;
      for (const item of allNotifications) {
        if (item.isRevoked && item.key !== "demo_zalo_2") {
          item.isRevoked = false;
          fixed++;
        }
      }
      allNotifications = allNotifications.filter(
        (n) => !(n.packageName === "com.notistar.cloud" && String(n.title || "").startsWith("🚨"))
      );
      await saveAllToLocalDb(allNotifications);
      renderApp();
      showToast(`✅ Đã sửa ${fixed} tin báo thu hồi nhầm về trạng thái bình thường!`);
    }

    async function cleanSpamAppsNow() {
      const spamKeywords = ["youtube", "shopee", "lazada", "tiktok", "weather", "spotify"];
      const before = allNotifications.length;
      allNotifications = allNotifications.filter((n) => {
        const hay = `${n.packageName || ""} ${n.appName || ""}`.toLowerCase();
        return !spamKeywords.some((kw) => hay.includes(kw));
      });
      const removed = before - allNotifications.length;
      await saveAllToLocalDb(allNotifications);
      renderApp();
      showToast(`🧹 Đã dọn sạch ${removed} thông báo giải trí/quảng cáo (YouTube, Shopee...)!`);
    }

    async function handleQuickIosPhotoUpload(event) {
      const file = event.target?.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async (e) => {
        const img = new Image();
        img.onload = async () => {
          const canvas = document.createElement("canvas");
          const maxDim = 640;
          const scale = Math.min(maxDim / img.width, maxDim / img.height, 1);
          canvas.width = Math.round(img.width * scale);
          canvas.height = Math.round(img.height * scale);
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          const b64 = canvas.toDataURL("image/jpeg", 0.82).split(",")[1];
          const now = Date.now();
          const newItem = normalizeNotification({
            id: now,
            key: `ios_photo_${now}`,
            packageName: "com.apple.iphoto",
            appName: "Ảnh iPhone (iOS Capture)",
            title: file.name || "Ảnh chụp màn hình iPhone",
            contentText: "Ảnh chụp thông báo lưu trực tiếp từ iPhone",
            bigText: "Ảnh chụp thông báo lưu trực tiếp từ iPhone",
            time: now,
            dateStr: formatDateOnly(now),
            pictureB64: b64,
            isSynced: true
          });
          await mergeIncomingNotifications([newItem], false);
          pushItemsToCloud([newItem], true);
          switchTab("media");
          showToast("📸 Đã lưu ảnh từ iPhone vào Kho Ảnh & đồng bộ Google Drive!");
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }

    async function checkOtaUpdate(manual = false) {
      try {
        if (manual) showToast("🔄 Đang kiểm tra bản cập nhật OTA qua mạng...");
        const res = await fetch(`./version.json?_t=${Date.now()}`, { cache: "no-store" });
        if (!res.ok) throw new Error("Network error");
        const ver = await res.json();
        const savedVer = parseInt(localStorage.getItem(STORAGE_KEYS.OTA_VERSION) || "0", 10);

        if (ver.resetFalseRevokedVersion && ver.resetFalseRevokedVersion > savedVer) {
          await resetAllFalseRevokedItems();
        }

        if (ver.versionCode > savedVer) {
          localStorage.setItem(STORAGE_KEYS.OTA_VERSION, String(ver.versionCode));
          if ("caches" in window) {
            const keys = await caches.keys();
            await Promise.all(keys.map((k) => caches.delete(k)));
          }
          if (savedVer > 0) {
            showToast(`🚀 Đã cập nhật OTA lên v${ver.versionName}! Đang làm mới...`);
            setTimeout(() => window.location.reload(), 900);
            return;
          }
        }
        if (manual) {
          if ("caches" in window) {
            const keys = await caches.keys();
            await Promise.all(keys.map((k) => caches.delete(k)));
          }
          await loadCloudSnapshotIfAvailable(true);
          await syncNow(true);
          showToast(`✅ Đang ở bản mới nhất v${ver.versionName || CURRENT_OTA_VERSION_NAME} (Đã cập nhật qua mạng)!`);
        }
      } catch (e) {
        if (manual) showToast("⚠️ Đang dùng phiên bản hiện tại (Kiểm tra lại kết nối mạng)");
      }
    }

    function renderManagementViewHtml() {
      const blockedSet = getBlockedAppsSet();
      const appMap = new Map();
      for (const n of allNotifications) {
        const key = n.packageName || n.appName || "unknown";
        if (!appMap.has(key)) {
          appMap.set(key, { key, name: n.appName || key, count: 0, photos: 0, revoked: 0 });
        }
        const entry = appMap.get(key);
        entry.count++;
        if (hasMedia(n)) entry.photos++;
        if (n.isRevoked) entry.revoked++;
      }
      const apps = Array.from(appMap.values()).sort((a, b) => b.count - a.count);

      const appRowsHtml = apps.map((a) => {
        const isBlocked = blockedSet.has(a.key);
        return `
          <div class="app-mgmt-row">
            <div class="app-mgmt-info">
              <div class="app-mgmt-name">${escapeHtml(a.name)} ${isBlocked ? `<span style="color:#F87171;font-size:11px;">(Đã ẩn)</span>` : ""}</div>
              <div class="app-mgmt-meta">${a.count} thông báo • 🖼️ ${a.photos} ảnh • <span style="opacity:0.75;">${escapeHtml(a.key)}</span></div>
            </div>
            <button class="smart-chip" style="${isBlocked ? "border-color:#34D399;color:#6EE7B7;" : "border-color:#F59E0B;color:#FCD34D;"}" onclick="toggleBlockApp('${escapeAttr(a.key)}')">
              ${isBlocked ? "✅ Hiện lại" : "🙈 Ẩn App"}
            </button>
            <button class="smart-chip" style="border-color:rgba(239,68,68,0.4);color:#FCA5A5;" onclick="deleteNotificationsByApp('${escapeAttr(a.key)}', '${escapeAttr(a.name)}')">
              🗑️ Xóa
            </button>
          </div>
        `;
      }).join("");

      return `
        <div class="ota-banner">
          <div class="mgmt-section-title">
            <span>🚀 Cập nhật Tự động Qua Mạng (OTA Update)</span>
            <span class="pill-badge badge-cloud">v${CURRENT_OTA_VERSION_NAME}</span>
          </div>
          <p class="mgmt-section-sub" style="margin-bottom:10px;">
            Không cần cắm cáp hay tải lại thủ công! Cả bản <strong>iOS</strong> và <strong>Android</strong> đều tự động nhận bản vá &amp; tính năng mới trực tiếp qua mạng.
          </p>
          <div class="btn-row" style="margin-top:0;">
            <button class="btn btn-primary" onclick="checkOtaUpdate(true)">
              ⚡ Cập nhật OTA cho iOS ngay
            </button>
            <a class="btn btn-success" href="./NotiStarCloud_OneUI7_AutoDrive.apk" download="NotiStarCloud_OneUI7_AutoDrive.apk">
              🤖 Tải / Update APK Android (OTA)
            </a>
          </div>
        </div>

        <div class="mgmt-section">
          <div class="mgmt-section-title">
            <span>🛠️ Sửa lỗi Báo thu hồi nhầm &amp; Dọn dẹp</span>
          </div>
          <p class="mgmt-section-sub">
            Nếu trước đó máy Android đánh dấu nhầm tin nhắn thường thành "Đã thu hồi" hoặc lưu trùng thông báo YouTube/Shopee, bấm 1 chạm bên dưới để làm sạch ngay:
          </p>
          <div class="btn-row" style="margin-top:0;">
            <button class="btn btn-primary" onclick="resetAllFalseRevokedItems()">
              ✅ Reset báo thu hồi nhầm
            </button>
            <button class="btn btn-danger" onclick="cleanSpamAppsNow()">
              🧹 Dọn sạch rác YouTube / Shopee
            </button>
          </div>
        </div>

        <div class="mgmt-section">
          <div class="mgmt-section-title">
            <span>📲 Cơ chế Bắt thông báo trên iOS &amp; Tải ảnh trực tiếp</span>
          </div>
          <p class="mgmt-section-sub">
            • <strong>Đồng bộ từ Android (Tự động 100%):</strong> Máy Samsung S24 Ultra (<code>SM-S928B</code>) bắt ngầm mọi thông báo + ảnh Zalo, Telegram, Messenger và đồng bộ thẳng sang iPhone qua Google Drive.<br/>
            • <strong>Bắt trực tiếp trên iPhone:</strong> Do Apple khóa Sandbox giữa các app trên iOS chưa Jailbreak, bạn có thể lưu trực tiếp ảnh chụp màn hình / bộ nhớ tạm trên iPhone hoặc bật Phím tắt Tự động hóa iOS (SMS/OTP/Email/Gõ mặt lưng):
          </p>
          <div class="btn-row" style="margin-top:0;">
            <label class="btn btn-success" style="cursor:pointer;">
              📸 Tải Ảnh / Screenshot từ iPhone
              <input type="file" accept="image/*" style="display:none;" onchange="handleQuickIosPhotoUpload(event)" />
            </label>
            <button class="btn" onclick="openModal('captureModal')">
              📋 Lưu Clipboard iPhone
            </button>
            <button class="btn" onclick="openModal('iosGuideModal')">
              ⚡ Cài Phím tắt iOS
            </button>
          </div>
        </div>

        <div class="mgmt-section">
          <div class="mgmt-section-title">
            <span>📱 Quản lý Ứng dụng (${apps.length} ứng dụng)</span>
          </div>
          <p class="mgmt-section-sub">
            Ẩn bớt các ứng dụng không quan trọng hoặc xóa toàn bộ thông báo của từng ứng dụng:
          </p>
          <div>${appRowsHtml || `<div style="color:var(--text-secondary);font-size:13px;">Chưa có ứng dụng nào.</div>`}</div>
        </div>

        <div class="mgmt-section">
          <div class="mgmt-section-title">
            <span>☁️ Cấu hình Google Drive, Giọng nói &amp; Bảo mật</span>
          </div>
          <div class="btn-row" style="margin-top:8px;">
            <button class="btn btn-primary" onclick="openModal('cloudModal')">⚙️ Cấu hình Google Drive &amp; File</button>
            <button class="btn" onclick="toggleVoiceAnnouncer()">🔊 Bật/Tắt Loa Ting-Ting</button>
            <button class="btn" onclick="configurePinCode()">🔒 Khóa PIN 4 số</button>
          </div>
        </div>
      `;
    }

    async function loadCloudSnapshotIfAvailable(force = false) {
      try {
        const res = await fetch(`./cloud_snapshot.json?_t=${Date.now()}`, { cache: "no-cache" });
        if (!res.ok) return 0;
        const snap = await res.json();
        if (snap && Array.isArray(snap.notifications) && snap.notifications.length > 0) {
          return await mergeIncomingNotifications(snap.notifications, false);
        }
      } catch (e) {}
      return 0;
    }
"""

html = html.replace("    async function toggleStarByUid(uid) {", mgmt_and_ota_js + "\n    async function toggleStarByUid(uid) {", 1)

# 10. Update initNotiStarIosApp() to run cleanup, load ./cloud_snapshot.json immediately, and check OTA updates automatically
old_init_block = """      // Tải dữ liệu Offline từ IndexedDB trước để hiển thị tức thì (< 30ms)
      allNotifications = await loadAllFromLocalDb();

      // Nếu được mở trực tiếp từ Google Apps Script (?ui=ios) có dữ liệu nạp sẵn
      if (Array.isArray(window.__PRELOADED_NOTIFICATIONS__) && window.__PRELOADED_NOTIFICATIONS__.length > 0) {
        await mergeIncomingNotifications(window.__PRELOADED_NOTIFICATIONS__, false);
      }

      renderApp();
      await handleUrlQueryActions();

      // Đồng bộ thời gian thực với Google Drive
      await syncNow(false);"""

new_init_block = """      // Tải dữ liệu Offline từ IndexedDB trước để hiển thị tức thì (< 30ms)
      allNotifications = await loadAllFromLocalDb();

      // Tự động dọn sạch trạng thái báo thu hồi nhầm từ bản cũ (1 lần duy nhất)
      if (localStorage.getItem(STORAGE_KEYS.CLEANED_V3) !== "1") {
        localStorage.setItem(STORAGE_KEYS.CLEANED_V3, "1");
        allNotifications = allNotifications.filter(
          (n) => !(n.packageName === "com.notistar.cloud" && String(n.title || "").startsWith("🚨"))
        );
        for (const item of allNotifications) {
          if (item.isRevoked && item.key !== "demo_zalo_2") {
            item.isRevoked = false;
          }
        }
        await saveAllToLocalDb(allNotifications);
      }

      renderApp();

      // Nạp ngay Snapshot tốc độ cao (chứa đầy đủ 43+ ảnh thật & tin nhắn đã khử trùng lặp) trong < 150ms
      await loadCloudSnapshotIfAvailable(false);

      // Kiểm tra cập nhật OTA tự động qua mạng
      checkOtaUpdate(false);

      await handleUrlQueryActions();

      // Đồng bộ thời gian thực với Google Drive ở chế độ nền
      syncNow(false);"""

html = html.replace(old_init_block, new_init_block, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully upgraded WebApp_PWA/index.html! Size:", os.path.getsize(path))
