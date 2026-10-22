/**
 * ============================================================================
 * NOTISTAR CLOUD (ANDROID + iOS 18 PWA) — GOOGLE APPS SCRIPT & DRIVE BACKEND
 * ============================================================================
 * Tệp: GoogleAppsScript_iOS_And_Drive.gs
 *
 * Cấu hình Cloud mặc định của người dùng:
 * - Thư mục Google Drive ID : 1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU
 * - Link Thư mục Google Drive: https://drive.google.com/drive/folders/1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU
 * - Web App URL              : https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec
 *
 * Tính năng nổi bật:
 * 1. Đồng bộ 2 chiều thời gian thực (Real-time Sync) giữa Android & iPhone (iOS PWA):
 *    - doPost(e) với action = "sync": Lưu thông báo + ảnh Base64 (pictureB64) + trạng thái
 *      Chống thu hồi (isRevoked) vào tệp `notistar_cloud_backup.json` nằm trực tiếp trong
 *      thư mục Google Drive `1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU`, đồng thời ghi lịch sử vào
 *      Google Sheets (`NotiStar_History`).
 *    - doPost(e) / doGet(e) với action = "pull" hoặc format = "json": Trả về toàn bộ JSON
 *      (`{ status: "ok", count: ..., notifications: [...] }`) cho cả Android & iPhone.
 * 2. Tích hợp sẵn giao diện iOS 18 / OneUI 7 PWA ngay trên Cloud (`?ui=ios`):
 *    - Mở `https://script.google.com/macros/s/.../exec?ui=ios` bằng Safari trên iPhone để
 *      sử dụng trực tiếp hoặc chọn "Thêm vào Màn hình chính" (Add to Home Screen) với dữ liệu
 *      Google Drive được nạp sẵn tức thì!
 * 3. Hỗ trợ iOS Shortcuts (Phím tắt iPhone) tự động đẩy tin nhắn/biến động số dư lên Drive
 *    qua cả GET (`?capture=1&app=...&title=...&body=...`) hoặc POST JSON.
 * ============================================================================
 */

const DEFAULT_DRIVE_FOLDER_ID = '1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU';
const DEFAULT_WEBAPP_URL = 'https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec';
const BACKUP_FILE_NAME = 'notistar_cloud_backup.json';
const SHEET_NAME = 'NotiStar_History';
const MAX_BACKUP_ITEMS = 2000;

/**
 * Xử lý HTTP POST từ Android NotiStarCloud, iOS PWA, hoặc iOS Shortcuts Automation.
 */
function doPost(e) {
  try {
    var rawContents = (e && e.postData && e.postData.contents) ? e.postData.contents : '{}';
    var payload = JSON.parse(rawContents);
    var action = String(payload.action || 'sync').toLowerCase();
    var folderId = String(payload.folderId || DEFAULT_DRIVE_FOLDER_ID).trim() || DEFAULT_DRIVE_FOLDER_ID;

    if (action === 'pull' || action === 'get') {
      return handlePullRequest(folderId);
    }

    var device = payload.device || 'NotiStar_Device';
    var items = Array.isArray(payload.notifications) ? payload.notifications : [];

    // Hỗ trợ trường hợp iOS Shortcuts gửi 1 object thông báo đơn lẻ trong body POST
    if (items.length === 0 && (payload.title || payload.body || payload.contentText)) {
      var nowTs = Date.now();
      items.push({
        id: nowTs,
        key: 'ios_post_' + nowTs,
        packageName: payload.packageName || 'com.apple.shortcuts',
        appName: payload.appName || payload.app || 'iPhone Shortcut',
        title: payload.title || 'Thông báo iPhone',
        contentText: payload.contentText || payload.body || '',
        bigText: payload.bigText || payload.body || payload.contentText || '',
        time: nowTs,
        dateStr: formatIsoDate(nowTs),
        isRevoked: Boolean(payload.isRevoked),
        isStarred: Boolean(payload.isStarred),
        pictureB64: payload.pictureB64 || ''
      });
    }

    // 1. Ghi vào Google Sheets (NotiStar_History)
    try {
      appendItemsToSheet(device, items, folderId);
    } catch (sheetErr) {
      // Vẫn tiếp tục lưu file JSON trên Google Drive ngay cả khi Sheet gặp lỗi quyền
    }

    // 2. Hợp nhất & khử trùng lặp vào tệp notistar_cloud_backup.json trong Drive Folder
    var mergedResult = mergeIntoDriveBackup(device, items, folderId);

    return jsonResponse({
      status: 'ok',
      syncedCount: items.length,
      totalBackupCount: mergedResult.count,
      fileId: mergedResult.fileId,
      folderId: folderId
    });
  } catch (err) {
    return jsonResponse({
      status: 'error',
      message: err.toString()
    });
  }
}

/**
 * Xử lý HTTP GET:
 * - Nếu `?ui=ios` -> Trả về giao diện Web App iOS 18 / OneUI 7 PWA kèm dữ liệu nạp sẵn từ Drive.
 * - Nếu `?capture=1&app=...&title=...&body=...` -> Lưu nhanh thông báo từ iOS Shortcuts URL.
 * - Mặc định hoặc `?action=pull` / `?format=json` -> Trả về JSON backup cho Android & iOS.
 */
function doGet(e) {
  var params = (e && e.parameter) ? e.parameter : {};
  var folderId = String(params.folderId || DEFAULT_DRIVE_FOLDER_ID).trim() || DEFAULT_DRIVE_FOLDER_ID;

  // 1. Hỗ trợ iOS Shortcuts đẩy nhanh qua GET (?capture=1&app=Zalo&title=...&body=...)
  if (params.capture === '1' && (params.title || params.body || params.text)) {
    var now = Date.now();
    var bodyText = params.body || params.text || '';
    var singleItem = {
      id: now,
      key: 'ios_get_' + now,
      packageName: params.pkg || 'com.apple.shortcuts',
      appName: params.app || 'iPhone Shortcut',
      title: params.title || params.app || 'iPhone',
      contentText: bodyText,
      bigText: bodyText,
      time: now,
      dateStr: formatIsoDate(now),
      isRevoked: params.revoked === '1' || params.revoked === 'true',
      isStarred: params.starred === '1' || params.starred === 'true',
      isSynced: true
    };
    try { appendItemsToSheet('iPhone Shortcut', [singleItem], folderId); } catch (ignore) {}
    mergeIntoDriveBackup('iPhone Shortcut', [singleItem], folderId);

    if (params.ui !== 'ios') {
      return jsonResponse({
        status: 'ok',
        captured: true,
        item: singleItem
      });
    }
  }

  // 2. Nếu mở giao diện trực tiếp trên Safari iPhone (?ui=ios)
  if (String(params.ui || '').toLowerCase() === 'ios') {
    return renderIosPwaWebApp(folderId);
  }

  // 3. Mặc định (bao gồm ?action=pull hoặc ?format=json): trả về JSON chuẩn cho Android & iOS
  return handlePullRequest(folderId);
}

/**
 * Đọc tệp `notistar_cloud_backup.json` từ thư mục Google Drive `1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU`
 * và trả về JSON `{ status: "ok", count: ..., notifications: [...] }`.
 */
function handlePullRequest(folderId) {
  try {
    var targetFolderId = folderId || DEFAULT_DRIVE_FOLDER_ID;
    var file = findBackupFileInDrive(targetFolderId);

    if (file) {
      var rawContent = file.getBlob().getDataAsString('UTF-8');
      var parsed = {};
      try {
        parsed = JSON.parse(rawContent);
      } catch (parseErr) {
        parsed = { notifications: [] };
      }
      var list = Array.isArray(parsed.notifications) ? parsed.notifications : [];
      return jsonResponse({
        status: 'ok',
        app: 'NotiStarCloud',
        version: 1,
        folderId: targetFolderId,
        fileId: file.getId(),
        exportTime: parsed.exportTime || Date.now(),
        count: list.length,
        notifications: list
      });
    }

    return jsonResponse({
      status: 'ok',
      app: 'NotiStarCloud',
      version: 1,
      folderId: targetFolderId,
      count: 0,
      notifications: []
    });
  } catch (err) {
    return jsonResponse({
      status: 'error',
      message: err.toString(),
      notifications: []
    });
  }
}

/**
 * Tìm tệp `notistar_cloud_backup.json` ưu tiên trong thư mục `1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU`.
 * Nếu chưa có trong thư mục, tìm trên toàn Drive để tương thích ngược.
 */
function findBackupFileInDrive(folderId) {
  try {
    if (folderId) {
      var folder = DriveApp.getFolderById(folderId);
      var folderFiles = folder.getFilesByName(BACKUP_FILE_NAME);
      if (folderFiles.hasNext()) {
        return folderFiles.next();
      }
    }
  } catch (folderErr) {
    // Fallback tìm toàn Drive nếu Folder ID không truy cập được
  }

  var rootFiles = DriveApp.getFilesByName(BACKUP_FILE_NAME);
  if (rootFiles.hasNext()) {
    return rootFiles.next();
  }
  return null;
}

/**
 * Hợp nhất danh sách thông báo mới (bao gồm ảnh Base64 `pictureB64` và cờ `isRevoked`)
 * vào tệp `notistar_cloud_backup.json` trong thư mục Google Drive `1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU`.
 */
function mergeIntoDriveBackup(device, newItems, folderId) {
  var targetFolderId = folderId || DEFAULT_DRIVE_FOLDER_ID;
  var existingItems = [];
  var file = findBackupFileInDrive(targetFolderId);

  if (file) {
    try {
      var parsed = JSON.parse(file.getBlob().getDataAsString('UTF-8'));
      if (Array.isArray(parsed.notifications)) {
        existingItems = parsed.notifications;
      }
    } catch (ignore) {}
  }

  // Khử trùng lặp thông minh theo khóa kết hợp (packageName + time + title + body)
  // đồng thời bảo toàn cờ `isRevoked`, `isStarred` và ảnh `pictureB64`
  var map = {};
  var orderKeys = [];

  function makeUid(n) {
    var t = n.time || 0;
    var pkg = n.packageName || n.appName || 'app';
    var title = String(n.title || '').substring(0, 40);
    var body = String(n.bigText || n.contentText || '').substring(0, 60);
    return pkg + '_' + t + '_' + title + '_' + body;
  }

  var allInput = existingItems.concat(newItems || []);
  for (var i = 0; i < allInput.length; i++) {
    var item = allInput[i];
    if (!item) continue;
    var uid = makeUid(item);
    if (!map[uid]) {
      map[uid] = item;
      orderKeys.push(uid);
    } else {
      // Cập nhật nếu thông báo sau đó bị thu hồi hoặc bổ sung ảnh/đánh dấu sao
      if (item.isRevoked) map[uid].isRevoked = true;
      if (item.isStarred) map[uid].isStarred = true;
      if (item.pictureB64 && !map[uid].pictureB64) map[uid].pictureB64 = item.pictureB64;
      if (item.largeIconB64 && !map[uid].largeIconB64) map[uid].largeIconB64 = item.largeIconB64;
    }
  }

  var combined = [];
  for (var k = 0; k < orderKeys.length; k++) {
    combined.push(map[orderKeys[k]]);
  }

  // Sắp xếp mới nhất lên đầu
  combined.sort(function(a, b) {
    return (Number(b.time) || 0) - (Number(a.time) || 0);
  });

  if (combined.length > MAX_BACKUP_ITEMS) {
    combined = combined.slice(0, MAX_BACKUP_ITEMS);
  }

  var backupObj = {
    status: 'ok',
    app: 'NotiStarCloud',
    version: 1,
    device: device,
    folderId: targetFolderId,
    exportTime: Date.now(),
    exportDate: new Date().toISOString(),
    count: combined.length,
    notifications: combined
  };

  var jsonStr = JSON.stringify(backupObj, null, 2);

  if (file) {
    file.setContent(jsonStr);
  } else {
    try {
      var targetFolder = DriveApp.getFolderById(targetFolderId);
      file = targetFolder.createFile(BACKUP_FILE_NAME, jsonStr, MimeType.PLAIN_TEXT);
    } catch (e) {
      file = DriveApp.createFile(BACKUP_FILE_NAME, jsonStr, MimeType.PLAIN_TEXT);
    }
  }

  return {
    fileId: file ? file.getId() : '',
    count: combined.length
  };
}

/**
 * Ghi lịch sử thông báo vào Google Sheets (`NotiStar_History`).
 * Nếu Script không gắn sẵn vào Sheet, tự động tạo/mở `NotiStar_Cloud_Spreadsheet` trong thư mục Drive.
 */
function appendItemsToSheet(device, items, folderId) {
  if (!items || items.length === 0) return;
  var sheet = getOrCreateSheet(folderId);
  for (var i = 0; i < items.length; i++) {
    var n = items[i];
    var timeStr = new Date(n.time || Date.now()).toLocaleString('vi-VN');
    var body = (n.bigText && n.bigText.length > 0) ? n.bigText : (n.contentText || '');
    var revokedTag = n.isRevoked ? '🚫 ĐÃ THU HỒI' : '';
    var hasPhotoTag = (n.pictureB64 && n.pictureB64.length > 20) ? '🖼️ Có Ảnh' : '';
    sheet.appendRow([
      n.id || '',
      timeStr,
      n.dateStr || '',
      device,
      n.appName || '',
      n.packageName || '',
      n.title || '',
      body,
      revokedTag,
      n.isStarred ? '★' : '',
      hasPhotoTag,
      n.key || ''
    ]);
  }
}

function getOrCreateSheet(folderId) {
  var ss = null;
  try {
    ss = SpreadsheetApp.getActiveSpreadsheet();
  } catch (ignore) {}

  if (!ss) {
    var files = DriveApp.getFilesByName('NotiStar_Cloud_Spreadsheet');
    if (files.hasNext()) {
      ss = SpreadsheetApp.open(files.next());
    } else {
      ss = SpreadsheetApp.create('NotiStar_Cloud_Spreadsheet');
      try {
        if (folderId) {
          var folder = DriveApp.getFolderById(folderId);
          var ssFile = DriveApp.getFileById(ss.getId());
          ssFile.moveTo(folder);
        }
      } catch (moveErr) {}
    }
  }

  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow([
      'ID', 'Thời gian', 'Ngày', 'Thiết bị', 'Ứng dụng',
      'Package', 'Tiêu đề', 'Nội dung chi tiết', 'Trạng thái Thu hồi',
      'Đã ghim', 'Đính kèm Ảnh', 'Key'
    ]);
    sheet.getRange(1, 1, 1, 12).setFontWeight('bold');
  }
  return sheet;
}

/**
 * Phục vụ trực tiếp ứng dụng iOS 18 / OneUI 7 PWA khi mở `?ui=ios` trên Safari iPhone,
 * nạp sẵn toàn bộ thông báo từ Google Drive (`window.__PRELOADED_NOTIFICATIONS__`).
 */
function renderIosPwaWebApp(folderId) {
  var preloadedNotifications = [];
  try {
    var file = findBackupFileInDrive(folderId || DEFAULT_DRIVE_FOLDER_ID);
    if (file) {
      var parsed = JSON.parse(file.getBlob().getDataAsString('UTF-8'));
      if (Array.isArray(parsed.notifications)) {
        preloadedNotifications = parsed.notifications.slice(0, 500);
      }
    }
  } catch (ignore) {}

  var html = [
    '<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"/>',
    '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover"/>',
    '<meta name="apple-mobile-web-app-capable" content="yes"/>',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>',
    '<meta name="apple-mobile-web-app-title" content="NotiStar Cloud"/>',
    '<title>NotiStar Cloud — iOS 18 & OneUI 7</title>',
    '<style>',
    'body{margin:0;background:#090A0F;color:#F4F6FB;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",sans-serif;padding:env(safe-area-inset-top,20px) 14px env(safe-area-inset-bottom,30px) 14px;}',
    '.shell{max-width:760px;margin:0 auto;}',
    '.hdr{position:sticky;top:0;background:rgba(18,20,30,0.86);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.08);z-index:20;}',
    '.row{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;}',
    '.title{font-size:20px;font-weight:800;margin:0;display:flex;align-items:center;gap:8px;}',
    '.badge-ios{font-size:11px;padding:2px 8px;border-radius:99px;background:linear-gradient(90deg,#2563EB,#7C3AED);color:#fff;}',
    '.tabs{display:flex;gap:6px;overflow-x:auto;padding:10px 0 4px 0;scrollbar-width:none;}',
    '.tab{padding:7px 13px;border-radius:99px;background:#191C2A;border:1px solid rgba(255,255,255,0.08);color:#949BB0;font-size:12.5px;font-weight:700;cursor:pointer;white-space:nowrap;}',
    '.tab.active{background:#2563EB;color:#fff;}',
    '.search{width:100%;padding:10px 14px;border-radius:99px;border:1px solid rgba(255,255,255,0.1);background:#191C2A;color:#fff;font-size:14px;margin-top:8px;box-sizing:border-box;outline:none;}',
    '.card{background:#191C2A;border:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:14px;margin-top:10px;}',
    '.card.revoked{background:linear-gradient(145deg,#28151D,#1B141C);border:1.5px solid #EF4444;}',
    '.rev-tag{display:inline-block;background:rgba(239,68,68,0.22);color:#FCA5A5;font-size:11px;font-weight:800;padding:3px 9px;border-radius:99px;margin-bottom:6px;}',
    '.meta{display:flex;align-items:center;gap:8px;font-size:12px;color:#949BB0;margin-bottom:4px;}',
    '.app{color:#4F8BFF;font-weight:700;}',
    '.ctitle{font-size:15px;font-weight:700;margin-bottom:4px;}',
    '.cbody{font-size:13.5px;color:#D5D9E6;white-space:pre-wrap;line-height:1.45;}',
    '.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;}',
    '.chip{padding:5px 11px;border-radius:99px;background:rgba(255,255,255,0.07);color:#CBD5E1;font-size:11.5px;font-weight:600;border:none;cursor:pointer;text-decoration:none;}',
    '.chip-otp{background:#059669;color:#fff;font-weight:800;}',
    '.bank-box{background:#131B2E;border:1px solid rgba(52,211,153,0.3);border-radius:18px;padding:12px;margin-top:10px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center;}',
    '</style></head><body><div class="shell">',
    '<div class="hdr"><div class="row"><h1 class="title">🔔 NotiStar Cloud <span class="badge-ios">iOS Cloud</span></h1>',
    '<div style="display:flex;gap:6px;"><button class="tab active" onclick="pullFromCloud()">🔄 Làm mới</button>',
    '<a class="tab" href="https://drive.google.com/drive/folders/' + (folderId || DEFAULT_DRIVE_FOLDER_ID) + '" target="_blank">📂 Mở Drive</a></div></div>',
    '<input id="q" class="search" placeholder="Tìm tin nhắn, Zalo thu hồi, số tiền, OTP, SĐT..." oninput="render()"/>',
    '<div class="tabs">',
    '<button class="tab active" id="t_all" onclick="setTab(\'all\')">Tất cả</button>',
    '<button class="tab" id="t_chat" onclick="setTab(\'chat\')">💬 Tin nhắn</button>',
    '<button class="tab" id="t_revoked" onclick="setTab(\'revoked\')">🚫 Đã thu hồi</button>',
    '<button class="tab" id="t_starred" onclick="setTab(\'starred\')">⭐ Đánh dấu</button>',
    '<button class="tab" id="t_media" onclick="setTab(\'media\')">🖼️ Kho Ảnh</button>',
    '<button class="tab" id="t_bank" onclick="setTab(\'bank\')">🏦 Ngân hàng</button>',
    '<button class="tab" id="t_links" onclick="setTab(\'links\')">🔗 Link & SĐT</button>',
    '</div></div>',
    '<div id="bankSummary" class="bank-box" style="display:none;"></div>',
    '<div id="list"></div></div>',
    '<script>',
    'window.__PRELOADED_NOTIFICATIONS__ = ' + JSON.stringify(preloadedNotifications) + ';',
    'const WEBAPP_URL = ' + JSON.stringify(DEFAULT_WEBAPP_URL) + ';',
    'let items = window.__PRELOADED_NOTIFICATIONS__ || [];',
    'let curTab = "all";',
    'const OTP_RE = /(?:otp|mã\\s*xác\\s*thực|ma\\s*xac\\s*thuc|verification\\s*code|mã\\s*otp)[^0-9]{0,25}([0-9]{4,8})\\b/i;',
    'const TX_RE = /([+-])\\s*([0-9]{1,3}(?:[.,][0-9]{3})+|[0-9]{4,12})\\s*(?:vnd|đ|vnđ|d\\b)/i;',
    'const PHONE_RE = /(?:\\+84|0)(?:3[2-9]|5[25689]|7[06-9]|8[1-9]|9[0-9])[0-9]{7}\\b/g;',
    'const URL_RE = /https?:\\/\\/[^\\s<>"\')]+/gi;',
    'function bodyOf(n){return (n.bigText&&n.bigText.length>0)?n.bigText:(n.contentText||"");}',
    'function setTab(t){curTab=t;document.querySelectorAll(".tabs .tab").forEach(b=>b.classList.remove("active"));const el=document.getElementById("t_"+t);if(el)el.classList.add("active");render();}',
    'async function pullFromCloud(){try{const r=await fetch(WEBAPP_URL+"?action=pull&_t="+Date.now());const j=await r.json();if(Array.isArray(j.notifications)){items=j.notifications;render();}}catch(e){}}',
    'function speak(txt){if("speechSynthesis" in window){window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(txt);u.lang="vi-VN";window.speechSynthesis.speak(u);}}',
    'function copyTxt(t){navigator.clipboard&&navigator.clipboard.writeText(t);alert("Đã sao chép: "+t);}',
    'function render(){',
    'const q=(document.getElementById("q").value||"").toLowerCase();',
    'let tin=0,tout=0;',
    'items.forEach(n=>{const m=TX_RE.exec((n.title||"")+" "+bodyOf(n));if(m){const v=parseInt(m[2].replace(/[.,]/g,""),10)||0;if(m[1]==="+")tin+=v;else tout+=v;}});',
    'const bBox=document.getElementById("bankSummary");',
    'if(curTab==="bank"||tin>0||tout>0){bBox.style.display="grid";bBox.innerHTML=`<div><div style="font-size:11px;color:#949BB0">Tổng vào</div><div style="color:#34D399;font-weight:800">+${tin.toLocaleString("vi-VN")} đ</div></div><div><div style="font-size:11px;color:#949BB0">Tổng ra</div><div style="color:#F87171;font-weight:800">-${tout.toLocaleString("vi-VN")} đ</div></div><div><div style="font-size:11px;color:#949BB0">Chênh lệch</div><div style="color:#60A5FA;font-weight:800">${(tin-tout).toLocaleString("vi-VN")} đ</div></div>`;}else{bBox.style.display="none";}',
    'const filtered=items.filter(n=>{',
    'const txt=((n.appName||"")+" "+(n.title||"")+" "+bodyOf(n)).toLowerCase();',
    'if(q&&!txt.includes(q))return false;',
    'if(curTab==="revoked")return Boolean(n.isRevoked);',
    'if(curTab==="starred")return Boolean(n.isStarred);',
    'if(curTab==="media")return Boolean(n.pictureB64&&n.pictureB64.length>20);',
    'if(curTab==="bank")return TX_RE.test(txt);',
    'if(curTab==="chat")return /zalo|messenger|orca|telegram|sms|imessage|viber|whatsapp/i.test(txt)||Boolean(n.hasRemoteInput);',
    'if(curTab==="links")return PHONE_RE.test(txt)||URL_RE.test(txt);',
    'return true;});',
    'document.getElementById("list").innerHTML=filtered.map(n=>{',
    'const b=bodyOf(n);const comb=(n.title||"")+" "+b;',
    'const otpM=OTP_RE.exec(comb);const phones=comb.match(PHONE_RE)||[];const urls=comb.match(URL_RE)||[];',
    'const imgHtml=(n.pictureB64&&n.pictureB64.length>20)?`<div style="margin-top:8px"><img src="data:image/jpeg;base64,${n.pictureB64}" style="max-width:100%;max-height:260px;border-radius:12px"/></div>`:"";',
    'return `<div class="card ${n.isRevoked?"revoked":""}">',
    '${n.isRevoked?`<div class="rev-tag">🚫 ĐÃ THU HỒI - ĐÃ GIỮ LẠI</div>`:""}',
    '<div class="meta"><span class="app">${n.appName||"App"}</span><span style="margin-left:auto">${new Date(n.time||Date.now()).toLocaleString("vi-VN")}</span></div>',
    '<div class="ctitle">${n.title||""}</div><div class="cbody">${b}</div>${imgHtml}',
    '<div class="chips">',
    '${otpM?`<button class="chip chip-otp" onclick="copyTxt(\'${otpM[1]}\')">📋 Copy OTP: ${otpM[1]}</button>`:""}',
    '${phones.map(p=>`<a class="chip" href="tel:${p}">📞 ${p}</a>`).join("")}',
    '${urls.map(u=>`<a class="chip" href="${u}" target="_blank">🔗 Mở Link</a>`).join("")}',
    '<button class="chip" onclick="speak(\'${(n.appName||"")+" "+(n.title||"").replace(/\'/g,"")}\')">🔊 Đọc</button>',
    '</div></div>`;',
    '}).join("");}',
    'render();',
    '</script></body></html>'
  ].join('\n');

  return HtmlService.createHtmlOutput(html)
    .setTitle('NotiStar Cloud — iOS 18 & OneUI 7')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function formatIsoDate(ts) {
  var d = new Date(Number(ts) || Date.now());
  var m = String(d.getMonth() + 1).padStart(2, '0');
  var day = String(d.getDate()).padStart(2, '0');
  return d.getFullYear() + '-' + m + '-' + day;
}
