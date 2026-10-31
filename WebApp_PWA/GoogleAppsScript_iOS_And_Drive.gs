/**
 * ============================================================================
 * NOTISTAR CLOUD V2 (ANDROID + iOS 18 LIQUID) — DAILY MULTI-FILE DRIVE BACKEND
 * ============================================================================
 * Tệp: GoogleAppsScript_iOS_And_Drive.gs
 *
 * Cấu hình Cloud mặc định của người dùng:
 * - Thư mục Google Drive ID : 1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU
 * - Link Thư mục Google Drive: https://drive.google.com/drive/folders/1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU
 * - Web App URL              : https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec
 *
 * NÂNG CẤP KIẾN TRÚC LƯU TRỮ V2 (MỖI NGÀY 1 FILE + BỎ GIỚI HẠN 2.000 TIN NHẮN):
 * 1. Tách riêng mỗi ngày 1 tệp sao lưu trên Google Drive:
 *    - Tên tệp theo ngày: `notistar_backup_YYYY-MM-DD.json`
 *      (Ví dụ: `notistar_backup_2026-10-22.json`, `notistar_backup_2026-10-26.json`...)
 *    - Tự động chuyển đổi (auto-migrate) tệp `notistar_cloud_backup.json` cũ thành các tệp
 *      tách riêng theo từng ngày ngay trong lần đồng bộ đầu tiên!
 * 2. Không giới hạn tổng số lượng tin nhắn qua các ngày (Unlimited Days Archive):
 *    - Mỗi ngày có tệp riêng chứa tối đa 20.000 thông báo/ngày (thay vì giới hạn 2.000 tin cho
 *      toàn bộ lịch sử như trước đây). Dữ liệu của các ngày trước KHÔNG BAO GIỜ bị ghi đè!
 * 3. Tự động lưu ảnh gốc `.JPG` vào thư mục con `NotiStar_Photos` trên Google Drive.
 * ============================================================================
 */

const DEFAULT_DRIVE_FOLDER_ID = '1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU';
const DEFAULT_WEBAPP_URL = 'https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec';
const LEGACY_BACKUP_FILE_NAME = 'notistar_cloud_backup.json';
const DAILY_FILE_PREFIX = 'notistar_backup_';
const SHEET_NAME = 'NotiStar_History';
const MAX_ITEMS_PER_DAY = 20000;
const MAX_ROLLING_PULL_ITEMS = 15000;

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
      return handlePullRequest(folderId, payload.date || '', payload.limit || 0);
    }
    if (action === 'list_days') {
      return handleListDailyFiles(folderId);
    }

    var device = payload.device || 'NotiStar_Device';
    var items = Array.isArray(payload.notifications) ? payload.notifications : [];

    // Hỗ trợ iOS Shortcuts gửi 1 object thông báo đơn lẻ
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

    // 1. Ghi lịch sử vào Google Sheets
    try {
      appendItemsToSheet(device, items, folderId);
    } catch (sheetErr) {}

    // 2. Hợp nhất vào các tệp theo từng ngày: `notistar_backup_YYYY-MM-DD.json`
    var dailyStats = mergeIntoDailyDriveBackups(device, items, folderId);

    // 3. Tự động lưu ảnh đính kèm thành tệp .JPG vào thư mục con `NotiStar_Photos`
    try {
      savePhotosToDriveSubfolder(items, folderId);
    } catch (photoErr) {}

    return jsonResponse({
      status: 'ok',
      storageMode: 'daily_files_unlimited',
      syncedCount: items.length,
      updatedDailyFiles: dailyStats.updatedFiles,
      totalDaysCount: dailyStats.totalDays,
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
 * - `?action=list_days`: Trả về danh sách toàn bộ các tệp `notistar_backup_YYYY-MM-DD.json` trên Drive.
 * - `?action=pull&date=YYYY-MM-DD`: Tải tệp sao lưu của riêng ngày `YYYY-MM-DD`.
 * - `?action=pull`: Đọc các tệp sao lưu theo ngày trên Google Drive và trả về danh sách gộp.
 */
function doGet(e) {
  var params = (e && e.parameter) ? e.parameter : {};
  var folderId = String(params.folderId || DEFAULT_DRIVE_FOLDER_ID).trim() || DEFAULT_DRIVE_FOLDER_ID;
  var action = String(params.action || '').toLowerCase();

  if (action === 'list_days') {
    return handleListDailyFiles(folderId);
  }

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
    mergeIntoDailyDriveBackups('iPhone Shortcut', [singleItem], folderId);
    return jsonResponse({ status: 'ok', captured: true, item: singleItem });
  }

  return handlePullRequest(folderId, params.date || '', params.limit || 0);
}

/**
 * Tự động tách tệp `notistar_cloud_backup.json` cũ (nếu có) sang các tệp theo từng ngày
 * `notistar_backup_YYYY-MM-DD.json` và lưu mọi thông báo mới theo đúng ngày của nó.
 */
function mergeIntoDailyDriveBackups(device, newItems, folderId) {
  var targetFolderId = folderId || DEFAULT_DRIVE_FOLDER_ID;
  var folder = getTargetFolder(targetFolderId);

  // Tự động migrate dữ liệu từ tệp đơn `notistar_cloud_backup.json` cũ (nếu chưa tách)
  var legacyItems = readLegacyBackupIfUnmigrated(folder);
  var allIncoming = legacyItems.concat(Array.isArray(newItems) ? newItems : []);

  // Nhóm thông báo theo từng ngày (YYYY-MM-DD)
  var byDate = {};
  for (var i = 0; i < allIncoming.length; i++) {
    var item = allIncoming[i];
    if (!item) continue;
    var dStr = item.dateStr || formatIsoDate(item.time || Date.now());
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dStr)) {
      dStr = formatIsoDate(item.time || Date.now());
    }
    item.dateStr = dStr;
    if (!byDate[dStr]) byDate[dStr] = [];
    byDate[dStr].push(item);
  }

  var updatedFiles = [];
  var dateKeys = Object.keys(byDate).sort();

  for (var dIdx = 0; dIdx < dateKeys.length; dIdx++) {
    var dateStr = dateKeys[dIdx];
    var dayNewItems = byDate[dateStr];

    // Tự động phân mảnh (Auto-Sharding): Nếu phần hiện tại đã đủ 10.000 tin thì tự tạo tiếp _part2.json, _part3.json...
    // Đảm bảo KHÔNG BAO GIỜ MISS bất kỳ thông báo nào dù 1 ngày có 50.000 hay 500.000 thông báo!
    var partIdx = 1;
    var targetFile = null;
    var existingPartItems = [];

    while (true) {
      var candidateName = partIdx === 1
        ? (DAILY_FILE_PREFIX + dateStr + '.json')
        : (DAILY_FILE_PREFIX + dateStr + '_part' + partIdx + '.json');
      var f = findFileByNameInFolder(folder, candidateName);
      if (!f) {
        break;
      }
      var parsedItems = [];
      try {
        var parsed = JSON.parse(f.getBlob().getDataAsString('UTF-8'));
        if (Array.isArray(parsed.notifications)) {
          parsedItems = parsed.notifications;
        }
      } catch (ignore) {}

      if (parsedItems.length < 10000) {
        targetFile = f;
        existingPartItems = parsedItems;
        break;
      }
      partIdx++;
    }

    var mergedAll = deduplicateNotificationsList(existingPartItems.concat(dayNewItems));

    for (var offset = 0; offset < mergedAll.length; offset += 10000) {
      var chunk = mergedAll.slice(offset, offset + 10000);
      var curPart = partIdx + Math.floor(offset / 10000);
      var curFileName = curPart === 1
        ? (DAILY_FILE_PREFIX + dateStr + '.json')
        : (DAILY_FILE_PREFIX + dateStr + '_part' + curPart + '.json');
      var curFile = (offset === 0 && targetFile) ? targetFile : findFileByNameInFolder(folder, curFileName);

      var dayObj = {
        status: 'ok',
        app: 'NotiStarCloud',
        version: 2,
        storageMode: 'daily_sharded_unlimited',
        date: dateStr,
        part: curPart,
        fileName: curFileName,
        device: device,
        folderId: targetFolderId,
        exportTime: Date.now(),
        exportDate: new Date().toISOString(),
        count: chunk.length,
        notifications: chunk
      };

      var jsonStr = JSON.stringify(dayObj, null, 2);
      if (curFile) {
        curFile.setContent(jsonStr);
      } else if (folder) {
        curFile = folder.createFile(curFileName, jsonStr, MimeType.PLAIN_TEXT);
      } else {
        curFile = DriveApp.createFile(curFileName, jsonStr, MimeType.PLAIN_TEXT);
      }

      updatedFiles.push({
        date: dateStr,
        part: curPart,
        fileName: curFileName,
        count: chunk.length,
        fileId: curFile ? curFile.getId() : ''
      });
    }
  }

  return {
    updatedFiles: updatedFiles,
    totalDays: updatedFiles.length
  };
}

/**
 * Đọc dữ liệu từ các tệp sao lưu theo ngày `notistar_backup_YYYY-MM-DD.json` trên Google Drive.
 * - Nếu truyền `targetDate` (VD: `2026-10-26`), chỉ trả về tệp của ngày đó.
 * - Nếu không truyền `targetDate`, đọc tất cả các tệp `notistar_backup_*.json` (kèm tệp cũ nếu có)
 *   và trả về danh sách thông báo không giới hạn 2.000 tin như trước!
 */
function handlePullRequest(folderId, targetDate, limitParam) {
  try {
    var targetFolderId = folderId || DEFAULT_DRIVE_FOLDER_ID;
    var folder = getTargetFolder(targetFolderId);
    var requestedLimit = Number(limitParam) > 0 ? Math.min(Number(limitParam), MAX_ROLLING_PULL_ITEMS) : MAX_ROLLING_PULL_ITEMS;

    // Đảm bảo nếu chỉ mới có file cũ thì tự động tách ra các file theo ngày luôn
    mergeIntoDailyDriveBackups('AutoMigrate', [], targetFolderId);

    var dailyFilesMeta = listDailyFilesInFolder(folder);
    var combined = [];

    if (targetDate && /^\d{4}-\d{2}-\d{2}$/.test(targetDate)) {
      for (var dIdx = 0; dIdx < dailyFilesMeta.length; dIdx++) {
        var dMeta = dailyFilesMeta[dIdx];
        if (dMeta.baseDate === targetDate || dMeta.date === targetDate || String(dMeta.date).indexOf(targetDate) === 0) {
          try {
            var dFile = DriveApp.getFileById(dMeta.fileId);
            var parsedPart = JSON.parse(dFile.getBlob().getDataAsString('UTF-8'));
            if (Array.isArray(parsedPart.notifications)) {
              combined = combined.concat(parsedPart.notifications);
            }
          } catch (e) {}
        }
      }
    } else {
      // Đọc các tệp theo ngày từ mới nhất đến cũ nhất
      for (var i = 0; i < dailyFilesMeta.length; i++) {
        var meta = dailyFilesMeta[i];
        try {
          var f = DriveApp.getFileById(meta.fileId);
          var p = JSON.parse(f.getBlob().getDataAsString('UTF-8'));
          if (Array.isArray(p.notifications)) {
            combined = combined.concat(p.notifications);
          }
        } catch (e) {}
        if (combined.length >= requestedLimit) break;
      }

      // Nếu chưa có tệp theo ngày nào, fallback đọc tệp `notistar_cloud_backup.json`
      if (combined.length === 0) {
        var legacyFile = findFileByNameInFolder(folder, LEGACY_BACKUP_FILE_NAME);
        if (legacyFile) {
          try {
            var legacyParsed = JSON.parse(legacyFile.getBlob().getDataAsString('UTF-8'));
            if (Array.isArray(legacyParsed.notifications)) {
              combined = legacyParsed.notifications;
            }
          } catch (e) {}
        }
      }
    }

    var deduped = deduplicateNotificationsList(combined);
    if (!targetDate && requestedLimit > 0 && deduped.length > requestedLimit) {
      deduped = deduped.slice(0, requestedLimit);
    }
    return jsonResponse({
      status: 'ok',
      app: 'NotiStarCloud',
      version: 2,
      storageMode: 'daily_files_unlimited',
      folderId: targetFolderId,
      dailyFiles: dailyFilesMeta,
      exportTime: Date.now(),
      count: deduped.length,
      notifications: deduped
    });
  } catch (err) {
    return jsonResponse({
      status: 'error',
      message: err.toString(),
      notifications: []
    });
  }
}

function handleListDailyFiles(folderId) {
  var targetFolderId = folderId || DEFAULT_DRIVE_FOLDER_ID;
  var folder = getTargetFolder(targetFolderId);
  var list = listDailyFilesInFolder(folder);
  return jsonResponse({
    status: 'ok',
    folderId: targetFolderId,
    totalDays: list.length,
    dailyFiles: list
  });
}

function listDailyFilesInFolder(folder) {
  var result = [];
  if (!folder) return result;
  var files = folder.getFiles();
  while (files.hasNext()) {
    var f = files.next();
    var name = f.getName();
    if (name.indexOf(DAILY_FILE_PREFIX) === 0 && name.slice(-5) === '.json') {
      var datePart = name.replace(DAILY_FILE_PREFIX, '').replace('.json', '');
      var baseDate = datePart.substring(0, 10);
      result.push({
        date: datePart,
        baseDate: baseDate,
        fileName: name,
        fileId: f.getId(),
        sizeBytes: f.getSize(),
        updatedAt: f.getLastUpdated().getTime()
      });
    }
  }
  result.sort(function(a, b) {
    return b.date.localeCompare(a.date);
  });
  return result;
}

function readLegacyBackupIfUnmigrated(folder) {
  if (!folder) return [];
  var existingDaily = listDailyFilesInFolder(folder);
  if (existingDaily.length > 0) return [];
  var legacyFile = findFileByNameInFolder(folder, LEGACY_BACKUP_FILE_NAME);
  if (!legacyFile) return [];
  try {
    var parsed = JSON.parse(legacyFile.getBlob().getDataAsString('UTF-8'));
    if (Array.isArray(parsed.notifications)) {
      return parsed.notifications;
    }
  } catch (e) {}
  return [];
}

function deduplicateNotificationsList(allInput) {
  var map = {};
  var orderKeys = [];

  function makeUid(n) {
    var dStr = n.dateStr || formatIsoDate(n.time || Date.now());
    var pkg = n.packageName || n.appName || 'app';
    var title = String(n.title || '').substring(0, 50);
    var body = String(n.bigText || n.contentText || '').substring(0, 80);
    var picSig = (n.pictureB64 && n.pictureB64.length > 40) ? String(n.pictureB64).slice(-20) : '';
    var timeBucket = body.length <= 12 ? String(Math.floor((Number(n.time) || 0) / 3600000)) : dStr;
    return pkg + '_' + timeBucket + '_' + title + '_' + body + '_' + picSig;
  }

  for (var i = 0; i < allInput.length; i++) {
    var item = allInput[i];
    if (!item) continue;
    var uid = makeUid(item);
    if (!map[uid]) {
      map[uid] = item;
      orderKeys.push(uid);
    } else {
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
  combined.sort(function(a, b) {
    return (Number(b.time) || 0) - (Number(a.time) || 0);
  });
  return combined;
}

function getTargetFolder(folderId) {
  try {
    return DriveApp.getFolderById(folderId || DEFAULT_DRIVE_FOLDER_ID);
  } catch (e) {
    return null;
  }
}

function findFileByNameInFolder(folder, fileName) {
  try {
    if (folder) {
      var iter = folder.getFilesByName(fileName);
      if (iter.hasNext()) return iter.next();
    }
  } catch (e) {}
  var rootIter = DriveApp.getFilesByName(fileName);
  if (rootIter.hasNext()) return rootIter.next();
  return null;
}

/**
 * Lưu các ảnh đính kèm (pictureB64) thành tệp ảnh .JPG riêng biệt bên trong thư mục con `NotiStar_Photos`
 * thuộc thư mục Google Drive `1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU`.
 */
function savePhotosToDriveSubfolder(items, folderId) {
  if (!items || items.length === 0) return;
  var targetFolderId = folderId || DEFAULT_DRIVE_FOLDER_ID;
  var parentFolder = DriveApp.getFolderById(targetFolderId);
  var subIter = parentFolder.getFoldersByName('NotiStar_Photos');
  var photoFolder = subIter.hasNext() ? subIter.next() : parentFolder.createFolder('NotiStar_Photos');
  var savedCount = 0;

  for (var i = 0; i < items.length; i++) {
    var n = items[i];
    if (!n || !n.pictureB64 || n.pictureB64.length < 100) continue;
    if (savedCount >= 8) break;
    var safeApp = String(n.appName || 'App').replace(/[^a-zA-Z0-9_-]/g, '');
    var ts = n.time || Date.now();
    var fileName = 'NotiStar_' + safeApp + '_' + ts + '.jpg';
    if (!photoFolder.getFilesByName(fileName).hasNext()) {
      var cleanB64 = String(n.pictureB64).replace(/^data:image\/\w+;base64,/, '');
      var bytes = Utilities.base64Decode(cleanB64);
      var blob = Utilities.newBlob(bytes, 'image/jpeg', fileName);
      photoFolder.createFile(blob);
      savedCount++;
    }
  }
}

/**
 * Ghi lịch sử thông báo vào Google Sheets (`NotiStar_History`).
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
