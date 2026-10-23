import os

src_path = r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\index.html"
with open(src_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove duplicate detailModal if present
dup_modal = """  <!-- Modal Detail & Conversation Sheet (Opens when tapping any Notification Card) -->
  <div id="detailModal" class="modal-backdrop" onclick="closeModalOnBackdrop(event, 'detailModal')">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div id="detailModalContent"></div>
    </div>
  </div>

  <!-- Modal Detail & Conversation Sheet (Opens when tapping any Notification Card) -->"""

single_modal = """  <!-- Modal Detail & Conversation Sheet (Opens when tapping any Notification Card) -->"""
if dup_modal in html:
    html = html.replace(dup_modal, single_modal, 1)

# 2. Update version constants to v9.4.0-iOS18
html = html.replace('const CURRENT_OTA_VERSION_CODE = 6;', 'const CURRENT_OTA_VERSION_CODE = 9;')
html = html.replace('const CURRENT_OTA_VERSION_NAME = "9.2.0-Pro";', 'const CURRENT_OTA_VERSION_NAME = "9.4.0-iOS18";')
html = html.replace('<span class="ios-badge">OneUI 7</span>', '<span class="ios-badge" id="platformBadge">iOS 18 • Liquid</span>')

# 3. Add AndroidNativeBridge helper functions right after pinSetupMode
target_state = """    let enteredPin = "";
    let pinSetupMode = false;"""

android_helpers = """    let enteredPin = "";
    let pinSetupMode = false;
    const IS_ANDROID_NATIVE = typeof window.AndroidNative !== "undefined";

    async function syncFromAndroidNativeDb(showToastMsg = false) {
      if (!IS_ANDROID_NATIVE) return 0;
      try {
        const rawJson = window.AndroidNative.getLocalNotificationsJson(350);
        if (rawJson) {
          const parsed = JSON.parse(rawJson);
          if (Array.isArray(parsed)) {
            const normalized = parsed
              .filter((r) => !(r.packageName === "com.notistar.cloud" && String(r.title || "").startsWith("🚨")))
              .map(normalizeNotification);
            allNotifications = normalized.sort((a, b) => b.time - a.time);
            renderApp();
          }
        }
        updateAndroidPermissionBanner();
        const statsStr = window.AndroidNative.getSyncStatusSubtitle ? window.AndroidNative.getSyncStatusSubtitle() : "";
        if (statsStr) {
          setSyncStatus(statsStr, true);
        }
        if (showToastMsg) {
          showToast(`✅ Đã làm mới ${allNotifications.length} thông báo từ máy Android!`);
        }
        return allNotifications.length;
      } catch (e) {
        console.error("syncFromAndroidNativeDb error", e);
      }
      return 0;
    }

    function updateAndroidPermissionBanner() {
      if (!IS_ANDROID_NATIVE) return;
      const banner = document.getElementById("iosInstallBanner");
      if (!banner) return;
      const granted = window.AndroidNative.isNotificationPermissionGranted
        ? window.AndroidNative.isNotificationPermissionGranted()
        : true;
      if (!granted) {
        banner.style.display = "flex";
        banner.style.background = "rgba(255, 69, 58, 0.18)";
        banner.style.borderColor = "rgba(255, 69, 58, 0.5)";
        banner.innerHTML = `
          <div class="install-banner-text" style="color:#FFD3D0;">
            <strong>⚠️ Chưa cấp quyền Đọc thông báo ngầm:</strong> Bật ngay để tự động bắt tin nhắn thu hồi &amp; ảnh Zalo/Messenger
          </div>
          <button class="btn btn-primary" style="flex:0 0 auto;width:auto;padding:7px 12px;font-size:12px;" onclick="window.AndroidNative.openNotificationSettings()">
            Cấp quyền
          </button>
        `;
      } else {
        banner.style.display = "none";
      }
    }

    window.onAndroidNativeUpdated = function() {
      syncFromAndroidNativeDb(false);
    };"""

assert target_state in html, "target_state not found"
html = html.replace(target_state, android_helpers, 1)

# 4. Enhance openNotificationDetail with Android Native actions (Open App, Direct Reply, Snooze/Repost)
target_detail_actions = """        <div style="display:flex;justify-content:flex-end;margin-top:-6px;margin-bottom:8px;">
          <button class="smart-chip" style="color:#FF6961;border-color:rgba(255,69,58,0.35);" onclick="deleteNotificationByUid('${escapeAttr(item.uid)}'); closeModal('detailModal')">
            🗑️ Xóa thông báo này
          </button>
        </div>"""

replacement_detail_actions = """        ${IS_ANDROID_NATIVE ? `
        <div class="btn-row" style="margin-top:0;margin-bottom:10px;">
          <button class="btn btn-primary" onclick="window.AndroidNative.openApp(String('${item.id}'), '${escapeAttr(item.key || "")}', '${escapeAttr(item.packageName || "")}')">
            🚀 Mở ${escapeHtml(item.appName)}
          </button>
          ${item.hasRemoteInput ? `
          <button class="btn btn-success" onclick="window.AndroidNative.directReply(String('${item.id}'))">
            💬 Trả lời nhanh
          </button>
          ` : ""}
          <button class="btn" onclick="window.AndroidNative.repostOrSnooze(String('${item.id}'))">
            ⏰ Báo lại
          </button>
        </div>
        ` : ""}
        <div style="display:flex;justify-content:flex-end;margin-top:-6px;margin-bottom:8px;">
          <button class="smart-chip" style="color:#FF6961;border-color:rgba(255,69,58,0.35);" onclick="deleteNotificationByUid('${escapeAttr(item.uid)}'); closeModal('detailModal')">
            🗑️ Xóa thông báo này
          </button>
        </div>"""

assert target_detail_actions in html, "target_detail_actions not found"
html = html.replace(target_detail_actions, replacement_detail_actions, 1)

# 5. Wire toggleStarByUid, toggleRevokedByUid, deleteNotificationByUid, deleteNotificationsByApp, resetAllFalseRevokedItems, cleanSpamAppsNow to AndroidNative
html = html.replace(
    """    async function toggleRevokedByUid(uid) {
      const target = allNotifications.find((n) => n.uid === uid);
      if (!target) return;
      target.isRevoked = !target.isRevoked;
      await saveAllToLocalDb(allNotifications);""",
    """    async function toggleRevokedByUid(uid) {
      const target = allNotifications.find((n) => n.uid === uid);
      if (!target) return;
      target.isRevoked = !target.isRevoked;
      if (IS_ANDROID_NATIVE && target.id) {
        try { window.AndroidNative.toggleRevoked(String(target.id), Boolean(target.isRevoked)); } catch (e) {}
      }
      await saveAllToLocalDb(allNotifications);"""
)

html = html.replace(
    """    async function deleteNotificationByUid(uid) {
      allNotifications = allNotifications.filter((n) => n.uid !== uid);
      await saveAllToLocalDb(allNotifications);""",
    """    async function deleteNotificationByUid(uid) {
      const target = allNotifications.find((n) => n.uid === uid);
      if (IS_ANDROID_NATIVE && target && target.id) {
        try { window.AndroidNative.deleteNotification(String(target.id)); } catch (e) {}
      }
      allNotifications = allNotifications.filter((n) => n.uid !== uid);
      await saveAllToLocalDb(allNotifications);"""
)

html = html.replace(
    """    async function deleteNotificationsByApp(appKey, appLabel) {
      const before = allNotifications.length;""",
    """    async function deleteNotificationsByApp(appKey, appLabel) {
      if (IS_ANDROID_NATIVE) {
        try { window.AndroidNative.deleteNotificationsByPackage(String(appKey)); } catch (e) {}
      }
      const before = allNotifications.length;"""
)

html = html.replace(
    """    async function resetAllFalseRevokedItems() {
      let fixed = 0;""",
    """    async function resetAllFalseRevokedItems() {
      if (IS_ANDROID_NATIVE) {
        try {
          const cnt = window.AndroidNative.resetAllFalseRevoked();
          await syncFromAndroidNativeDb(false);
          showToast(`✅ Đã sửa ${cnt} tin báo thu hồi nhầm về trạng thái bình thường!`);
          return;
        } catch (e) {}
      }
      let fixed = 0;"""
)

html = html.replace(
    """    async function cleanSpamAppsNow() {
      const spamKeywords = ["youtube", "shopee", "lazada", "tiktok", "weather", "spotify"];""",
    """    async function cleanSpamAppsNow() {
      if (IS_ANDROID_NATIVE) {
        try {
          const cnt = window.AndroidNative.cleanPromotionalSpam();
          await syncFromAndroidNativeDb(false);
          showToast(`🧹 Đã dọn sạch ${cnt} thông báo giải trí/quảng cáo!`);
          return;
        } catch (e) {}
      }
      const spamKeywords = ["youtube", "shopee", "lazada", "tiktok", "weather", "spotify"];"""
)

html = html.replace(
    """    async function toggleStarByUid(uid) {
      const target = allNotifications.find((n) => n.uid === uid);
      if (!target) return;
      target.isStarred = !target.isStarred;
      await saveAllToLocalDb(allNotifications);""",
    """    async function toggleStarByUid(uid) {
      const target = allNotifications.find((n) => n.uid === uid);
      if (!target) return;
      target.isStarred = !target.isStarred;
      if (IS_ANDROID_NATIVE && target.id) {
        try { window.AndroidNative.toggleStar(String(target.id), Boolean(target.isStarred)); } catch (e) {}
      }
      await saveAllToLocalDb(allNotifications);"""
)

# 6. Wire speakVietnamese, syncNow, checkOtaUpdate, and Management View for AndroidNative
html = html.replace(
    """    function speakVietnamese(text) {
      if (!("speechSynthesis" in window)) {""",
    """    function speakVietnamese(text) {
      if (IS_ANDROID_NATIVE && window.AndroidNative.speakVietnamese) {
        try {
          window.AndroidNative.speakVietnamese(String(text || ""));
          return;
        } catch (e) {}
      }
      if (!("speechSynthesis" in window)) {"""
)

html = html.replace(
    """    async function checkOtaUpdate(manual = false) {
      try {""",
    """    async function checkOtaUpdate(manual = false) {
      if (IS_ANDROID_NATIVE && window.AndroidNative.checkOtaUpdate) {
        try {
          window.AndroidNative.checkOtaUpdate(Boolean(manual));
          return;
        } catch (e) {}
      }
      try {"""
)

html = html.replace(
    """    async function syncNow(showToastMsg = false) {
      if (isSyncing) return;""",
    """    async function syncNow(showToastMsg = false) {
      if (IS_ANDROID_NATIVE) {
        await syncFromAndroidNativeDb(false);
        if (showToastMsg && window.AndroidNative.triggerCloudSync) {
          try { window.AndroidNative.triggerCloudSync(); } catch (e) {}
        }
      }
      if (isSyncing) return;"""
)

# 7. Add Native Android Controls card in renderManagementViewHtml when IS_ANDROID_NATIVE is true
target_mgmt_ota = """          <div class="btn-row" style="margin-top:0;">
            <button class="btn btn-primary" onclick="checkOtaUpdate(true)">
              ⚡ Cập nhật OTA cho iOS ngay
            </button>
            <a class="btn btn-success" href="./NotiStarCloud_OneUI7_AutoDrive.apk" download="NotiStarCloud_OneUI7_AutoDrive.apk">
              🤖 Tải / Update APK Android (OTA)
            </a>
          </div>
        </div>"""

replacement_mgmt_ota = """          <div class="btn-row" style="margin-top:0;">
            <button class="btn btn-primary" onclick="checkOtaUpdate(true)">
              ⚡ ${IS_ANDROID_NATIVE ? "Kiểm tra & Cập nhật APK qua OTA" : "Cập nhật OTA cho iOS ngay"}
            </button>
            ${!IS_ANDROID_NATIVE ? `
            <a class="btn btn-success" href="./NotiStarCloud_OneUI7_AutoDrive.apk" download="NotiStarCloud_OneUI7_AutoDrive.apk">
              🤖 Tải / Update APK Android (OTA)
            </a>` : ""}
          </div>
        </div>

        ${IS_ANDROID_NATIVE ? `
        <div class="mgmt-section" style="border-color:rgba(10,132,255,0.4);background:linear-gradient(145deg, rgba(10,132,255,0.12), rgba(28,28,30,0.92));">
          <div class="mgmt-section-title">
            <span>🤖 Đặc quyền Hệ thống Android &amp; Đổi Giao diện</span>
            <span class="pill-badge badge-cloud">Native Bridge</span>
          </div>
          <p class="mgmt-section-sub">
            Bạn đang trải nghiệm <strong>Giao diện iOS 18 Liquid Glass</strong> chạy trực tiếp trên nhân hệ thống Android (bắt thông báo ngầm 0ms, chống thu hồi Zalo/Messenger, trả lời trực tiếp):
          </p>
          <div class="btn-row" style="margin-top:0;">
            <button class="btn btn-primary" onclick="window.AndroidNative.openNotificationSettings()">
              🔑 Quyền Đọc TB Ngầm
            </button>
            <button class="btn btn-success" onclick="window.AndroidNative.openCloudSyncActivity()">
              ☁️ Google Drive Native
            </button>
          </div>
          <div class="btn-row">
            <button class="btn" onclick="window.AndroidNative.openAutoReplyBot()">
              🤖 Bot Tự trả lời
            </button>
            <button class="btn" onclick="window.AndroidNative.toggleFloatingEdge()">
              📱 Thanh trượt cạnh
            </button>
            <button class="btn" onclick="window.AndroidNative.requestBatteryUnrestricted()">
              🔋 Pin Không giới hạn
            </button>
          </div>
          <div class="btn-row">
            <button class="btn" onclick="window.AndroidNative.postTestNotification()">
              🧪 Bắn thông báo mẫu
            </button>
            <button class="btn" style="border-color:rgba(167,139,250,0.5);color:#C4B5FD;" onclick="window.AndroidNative.switchToClassicAndroidUi()">
              🎨 Chuyển sang Giao diện Android Cổ điển
            </button>
          </div>
        </div>
        ` : ""}"""

assert target_mgmt_ota in html, "target_mgmt_ota not found"
html = html.replace(target_mgmt_ota, replacement_mgmt_ota, 1)

# 8. In initNotiStarIosApp, if IS_ANDROID_NATIVE, load immediately from Android SQLite DB!
target_init = """      // Hiển thị gợi ý Thêm vào Màn hình chính nếu mở trên Safari iPhone thường (chưa standalone)
      const isStandalone = window.navigator.standalone === true || window.matchMedia("(display-mode: standalone)").matches;
      if (!isStandalone) {
        const banner = document.getElementById("iosInstallBanner");
        if (banner) banner.style.display = "flex";
      }"""

replacement_init = """      if (IS_ANDROID_NATIVE) {
        const badge = document.getElementById("platformBadge");
        if (badge) badge.textContent = "iOS 18 • Liquid";
        updateAndroidPermissionBanner();
      } else {
        // Hiển thị gợi ý Thêm vào Màn hình chính nếu mở trên Safari iPhone thường (chưa standalone)
        const isStandalone = window.navigator.standalone === true || window.matchMedia("(display-mode: standalone)").matches;
        if (!isStandalone) {
          const banner = document.getElementById("iosInstallBanner");
          if (banner) banner.style.display = "flex";
        }
      }"""

assert target_init in html, "target_init not found"
html = html.replace(target_init, replacement_init, 1)

target_load_db = """      // Tải dữ liệu Offline từ IndexedDB trước để hiển thị tức thì (< 30ms)
      allNotifications = await loadAllFromLocalDb();"""

replacement_load_db = """      // Nếu chạy trên Android Native, nạp trực tiếp từ SQLite Database của máy (< 15ms)
      if (IS_ANDROID_NATIVE) {
        await syncFromAndroidNativeDb(false);
      } else {
        // Tải dữ liệu Offline từ IndexedDB trước để hiển thị tức thì (< 30ms)
        allNotifications = await loadAllFromLocalDb();
      }"""

assert target_load_db in html, "target_load_db not found"
html = html.replace(target_load_db, replacement_load_db, 1)

# Save to Android assets and update iOS WebApp_PWA
android_assets_dir = r"e:\MOD\NotiStarCloud\app\src\main\assets\ios_ui"
os.makedirs(android_assets_dir, exist_ok=True)
with open(os.path.join(android_assets_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

with open(src_path, "w", encoding="utf-8") as f:
    f.write(html)

with open(r"e:\MOD\NotiStarCloud_iOS\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully generated unified iOS 18 UI for Android assets and iOS PWA!")
