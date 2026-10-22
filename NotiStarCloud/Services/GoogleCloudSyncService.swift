import Foundation
import SwiftUI
import UIKit

@MainActor
final class GoogleCloudSyncService: ObservableObject {
    static let shared = GoogleCloudSyncService()

    @Published var notifications: [NotiItem] = []
    @Published var isSyncing: Bool = false
    @Published var lastSyncStatus: String = "Sẵn sàng đồng bộ Google Drive"
    @Published var lastSyncTimestamp: Date?

    @Published var driveFolderId: String {
        didSet {
            let clean = driveFolderId.trimmingCharacters(in: .whitespacesAndNewlines)
            UserDefaults.standard.set(clean.isEmpty ? CloudConstants.DEFAULT_DRIVE_FOLDER_ID : clean, forKey: "notistar_drive_folder_id")
        }
    }

    @Published var webAppUrl: String {
        didSet {
            let clean = webAppUrl.trimmingCharacters(in: .whitespacesAndNewlines)
            UserDefaults.standard.set(clean.isEmpty ? CloudConstants.DEFAULT_WEBAPP_URL : clean, forKey: "notistar_webapp_url")
        }
    }

    @Published var customWebhookUrl: String {
        didSet {
            UserDefaults.standard.set(customWebhookUrl.trimmingCharacters(in: .whitespacesAndNewlines), forKey: "notistar_custom_webhook_url")
        }
    }

    @Published var autoSyncEnabled: Bool {
        didSet {
            UserDefaults.standard.set(autoSyncEnabled, forKey: "notistar_auto_sync_enabled")
        }
    }

    private var refreshTimer: Timer?

    private init() {
        let defaults = UserDefaults.standard
        let storedFolder = defaults.string(forKey: "notistar_drive_folder_id") ?? ""
        self.driveFolderId = storedFolder.isEmpty ? CloudConstants.DEFAULT_DRIVE_FOLDER_ID : storedFolder

        let storedUrl = defaults.string(forKey: "notistar_webapp_url") ?? ""
        self.webAppUrl = storedUrl.isEmpty ? CloudConstants.DEFAULT_WEBAPP_URL : storedUrl

        self.customWebhookUrl = defaults.string(forKey: "notistar_custom_webhook_url") ?? ""
        if defaults.object(forKey: "notistar_auto_sync_enabled") == nil {
            defaults.set(true, forKey: "notistar_auto_sync_enabled")
        }
        self.autoSyncEnabled = defaults.bool(forKey: "notistar_auto_sync_enabled")

        loadLocalNotifications()
        startAutoRefreshTimer()
    }

    // MARK: - Local Persistence

    private var localFileURL: URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        return docs.appendingPathComponent("NotiStarCloud_LocalDB.json")
    }

    func loadLocalNotifications() {
        var loaded: [NotiItem] = []

        if let data = try? Data(contentsOf: localFileURL),
           let decoded = try? JSONDecoder().decode([NotiItem].self, from: data) {
            loaded = decoded
        } else if let data = UserDefaults.standard.data(forKey: CloudConstants.STORAGE_KEY_NOTIFICATIONS),
                  let decoded = try? JSONDecoder().decode([NotiItem].self, from: data) {
            loaded = decoded
        }

        // Merge any pending items queued by AppIntents / Shortcuts in App Group or Standard Defaults
        let pendingFromShortcuts = Self.consumeShortcutPendingItems()
        if !pendingFromShortcuts.isEmpty {
            for item in pendingFromShortcuts {
                if !loaded.contains(where: { $0.id == item.id || $0.key == item.key }) {
                    loaded.insert(item, at: 0)
                }
            }
        }

        if loaded.isEmpty && !UserDefaults.standard.bool(forKey: "notistar_seeded_initial_demo") {
            loaded = Self.createInitialShowcaseItems()
            UserDefaults.standard.set(true, forKey: "notistar_seeded_initial_demo")
        }

        loaded.sort { $0.time > $1.time }
        self.notifications = loaded
        saveLocalNotifications()
    }

    func saveLocalNotifications() {
        let sorted = notifications.sorted { $0.time > $1.time }
        notifications = sorted
        if let data = try? JSONEncoder().encode(sorted) {
            try? data.write(to: localFileURL, options: .atomic)
            UserDefaults.standard.set(data, forKey: CloudConstants.STORAGE_KEY_NOTIFICATIONS)
        }
    }

    static func enqueueShortcutItem(_ item: NotiItem) {
        let key = "notistar_shortcut_pending_queue"
        var queue: [NotiItem] = []
        if let data = UserDefaults.standard.data(forKey: key),
           let existing = try? JSONDecoder().decode([NotiItem].self, from: data) {
            queue = existing
        }
        queue.insert(item, at: 0)
        if let encoded = try? JSONEncoder().encode(queue) {
            UserDefaults.standard.set(encoded, forKey: key)
        }
        if let groupDefaults = UserDefaults(suiteName: CloudConstants.APP_GROUP_SUITE),
           let encoded = try? JSONEncoder().encode(queue) {
            groupDefaults.set(encoded, forKey: key)
        }
    }

    private static func consumeShortcutPendingItems() -> [NotiItem] {
        let key = "notistar_shortcut_pending_queue"
        var collected: [NotiItem] = []
        if let data = UserDefaults.standard.data(forKey: key),
           let decoded = try? JSONDecoder().decode([NotiItem].self, from: data) {
            collected.append(contentsOf: decoded)
            UserDefaults.standard.removeObject(forKey: key)
        }
        if let groupDefaults = UserDefaults(suiteName: CloudConstants.APP_GROUP_SUITE),
           let data = groupDefaults.data(forKey: key),
           let decoded = try? JSONDecoder().decode([NotiItem].self, from: data) {
            collected.append(contentsOf: decoded)
            groupDefaults.removeObject(forKey: key)
        }
        return collected
    }

    private func startAutoRefreshTimer() {
        refreshTimer?.invalidate()
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 45.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            Task { @MainActor in
                let shortcutItems = Self.consumeShortcutPendingItems()
                if !shortcutItems.isEmpty {
                    for item in shortcutItems {
                        self.addOrMergeNotification(item, triggerCloudPush: self.autoSyncEnabled)
                    }
                }
                if self.autoSyncEnabled {
                    await self.pullFromCloud(silent: true)
                }
            }
        }
    }

    // MARK: - CRUD & Clipboard Vault

    func addOrMergeNotification(_ item: NotiItem, triggerCloudPush: Bool = true) {
        if let idx = notifications.firstIndex(where: { $0.id == item.id || (!item.key.isEmpty && $0.key == item.key) }) {
            var updated = notifications[idx]
            if item.isRevoked && !updated.isRevoked {
                updated.isRevoked = true
                VoiceAnnouncerAndSecurityService.shared.announceItemIfNeeded(updated)
            }
            if !item.pictureB64.isEmpty && updated.pictureB64.isEmpty {
                updated.pictureB64 = item.pictureB64
            }
            if !item.largeIconB64.isEmpty && updated.largeIconB64.isEmpty {
                updated.largeIconB64 = item.largeIconB64
            }
            if item.isSynced {
                updated.isSynced = true
            }
            notifications[idx] = updated
        } else {
            notifications.insert(item, at: 0)
            VoiceAnnouncerAndSecurityService.shared.announceItemIfNeeded(item)
        }
        saveLocalNotifications()

        if triggerCloudPush {
            Task {
                await pushItemsToCloud([item])
            }
        }
    }

    func toggleStar(for item: NotiItem) {
        guard let idx = notifications.firstIndex(where: { $0.id == item.id }) else { return }
        notifications[idx].isStarred.toggle()
        saveLocalNotifications()
    }

    func markAsRevoked(for item: NotiItem) {
        guard let idx = notifications.firstIndex(where: { $0.id == item.id }) else { return }
        notifications[idx].isRevoked = true
        let updated = notifications[idx]
        saveLocalNotifications()
        VoiceAnnouncerAndSecurityService.shared.announceItemIfNeeded(updated)
        Task {
            await pushItemsToCloud([updated])
        }
    }

    func deleteNotification(_ item: NotiItem) {
        notifications.removeAll { $0.id == item.id }
        saveLocalNotifications()
    }

    func clearNonStarred() {
        notifications.removeAll { !$0.isStarred }
        saveLocalNotifications()
    }

    func saveFromClipboard() -> Bool {
        if let str = UIPasteboard.general.string, !str.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            let nowMs = Int64(Date().timeIntervalSince1970 * 1000)
            let newItem = NotiItem(
                id: "ios_clip_\(nowMs)",
                key: "com.apple.clipboard|\(nowMs)",
                notificationId: Int(nowMs % 100000),
                packageName: "com.apple.clipboard.vault",
                appName: "Clipboard Vault iOS",
                title: "📋 Đã lưu nhanh từ bộ nhớ tạm iPhone",
                contentText: str,
                bigText: str,
                inboxLines: str.components(separatedBy: "\n"),
                time: nowMs,
                isStarred: true,
                isSynced: false,
                isRevoked: false
            )
            addOrMergeNotification(newItem, triggerCloudPush: true)
            return true
        } else if let image = UIPasteboard.general.image,
                  let jpegData = image.jpegData(compressionQuality: 0.72) {
            let nowMs = Int64(Date().timeIntervalSince1970 * 1000)
            let b64 = jpegData.base64EncodedString()
            let newItem = NotiItem(
                id: "ios_clip_img_\(nowMs)",
                key: "com.apple.clipboard.image|\(nowMs)",
                notificationId: Int(nowMs % 100000),
                packageName: "com.apple.clipboard.vault",
                appName: "Clipboard Vault iOS",
                title: "🖼️ Ảnh đã lưu từ Clipboard iPhone",
                contentText: "Hình ảnh chụp màn hình / sao chép từ bộ nhớ tạm",
                bigText: "Hình ảnh chụp màn hình / sao chép từ bộ nhớ tạm",
                time: nowMs,
                isStarred: true,
                isSynced: false,
                isRevoked: false,
                pictureB64: b64
            )
            addOrMergeNotification(newItem, triggerCloudPush: true)
            return true
        }
        return false
    }

    // MARK: - Google Apps Script Cloud Pull & Push

    func pullFromCloud(silent: Bool = false) async {
        let baseUrl = webAppUrl.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !baseUrl.isEmpty else {
            lastSyncStatus = "Chưa cấu hình Web App URL"
            return
        }

        if !silent {
            isSyncing = true
            lastSyncStatus = "Đang tải dữ liệu từ Google Drive..."
        }

        defer {
            if !silent {
                isSyncing = false
            }
        }

        let sep = baseUrl.contains("?") ? "&" : "?"
        let pullUrlString = "\(baseUrl)\(sep)action=pull&driveFolderId=\(driveFolderId.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? driveFolderId)"

        guard let url = URL(string: pullUrlString) else {
            lastSyncStatus = "URL Google Apps Script không hợp lệ"
            return
        }

        do {
            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.timeoutInterval = 25

            let (data, response) = try await URLSession.shared.data(for: request)
            guard let httpResp = response as? HTTPURLResponse, (200...299).contains(httpResp.statusCode) else {
                lastSyncStatus = "Google Cloud trả về mã lỗi HTTP"
                return
            }

            let pulledItems = Self.parseCloudResponseData(data)
            var newOrUpdatedCount = 0

            for var remoteItem in pulledItems {
                remoteItem.isSynced = true
                if let idx = notifications.firstIndex(where: {
                    $0.id == remoteItem.id || (!remoteItem.key.isEmpty && $0.key == remoteItem.key && abs($0.time - remoteItem.time) < 2000)
                }) {
                    var local = notifications[idx]
                    let becameRevoked = remoteItem.isRevoked && !local.isRevoked
                    if becameRevoked {
                        local.isRevoked = true
                        newOrUpdatedCount += 1
                        VoiceAnnouncerAndSecurityService.shared.announceItemIfNeeded(local)
                    }
                    if !remoteItem.pictureB64.isEmpty && local.pictureB64.isEmpty {
                        local.pictureB64 = remoteItem.pictureB64
                        newOrUpdatedCount += 1
                    }
                    if !remoteItem.largeIconB64.isEmpty && local.largeIconB64.isEmpty {
                        local.largeIconB64 = remoteItem.largeIconB64
                    }
                    local.isSynced = true
                    notifications[idx] = local
                } else {
                    notifications.append(remoteItem)
                    newOrUpdatedCount += 1
                    VoiceAnnouncerAndSecurityService.shared.announceItemIfNeeded(remoteItem)
                }
            }

            saveLocalNotifications()
            lastSyncTimestamp = Date()
            let fmt = DateFormatter()
            fmt.dateFormat = "HH:mm:ss"
            lastSyncStatus = "Đã đồng bộ Drive (\(fmt.string(from: Date()))) · +\(newOrUpdatedCount) tin mới"
        } catch {
            if !silent {
                lastSyncStatus = "Lỗi kết nối Cloud: \(error.localizedDescription)"
            }
        }
    }

    func pushUnsyncedToCloud() async {
        let unsynced = notifications.filter { !$0.isSynced }
        if unsynced.isEmpty {
            await pullFromCloud(silent: false)
            return
        }
        await pushItemsToCloud(unsynced)
        await pullFromCloud(silent: true)
    }

    func pushItemsToCloud(_ items: [NotiItem]) async {
        guard !items.isEmpty else { return }
        let baseUrl = webAppUrl.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let url = URL(string: baseUrl) else { return }

        isSyncing = true
        lastSyncStatus = "Đang đẩy \(items.count) thông báo lên Google Drive..."
        defer { isSyncing = false }

        do {
            let itemsData = try JSONEncoder().encode(items)
            let itemsJsonArray = (try? JSONSerialization.jsonObject(with: itemsData)) ?? []

            var payload: [String: Any] = [
                "action": "sync",
                "sourcePlatform": "iOS",
                "driveFolderId": driveFolderId,
                "folderId": driveFolderId,
                "notifications": itemsJsonArray,
                "items": itemsJsonArray
            ]

            // Also include first item's direct fields for single-record script handlers
            if let firstObj = (itemsJsonArray as? [[String: Any]])?.first {
                for (k, v) in firstObj {
                    payload[k] = v
                }
            }

            let bodyData = try JSONSerialization.data(withJSONObject: payload, options: [])

            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json; charset=utf-8", forHTTPHeaderField: "Content-Type")
            request.httpBody = bodyData
            request.timeoutInterval = 30

            let (_, response) = try await URLSession.shared.data(for: request)
            if let httpResp = response as? HTTPURLResponse, (200...399).contains(httpResp.statusCode) {
                let ids = Set(items.map { $0.id })
                for idx in notifications.indices {
                    if ids.contains(notifications[idx].id) {
                        notifications[idx].isSynced = true
                    }
                }
                saveLocalNotifications()
                lastSyncTimestamp = Date()
                let fmt = DateFormatter()
                fmt.dateFormat = "HH:mm:ss"
                lastSyncStatus = "Đã lưu lên Google Drive lúc \(fmt.string(from: Date()))"
            } else {
                lastSyncStatus = "Không thể ghi lên Google Drive (kiểm tra quyền Web App)"
            }

            // Optional Secondary Webhook (Telegram / Discord / Custom JSON)
            if !customWebhookUrl.isEmpty, let hookUrl = URL(string: customWebhookUrl) {
                var hookReq = URLRequest(url: hookUrl)
                hookReq.httpMethod = "POST"
                hookReq.setValue("application/json", forHTTPHeaderField: "Content-Type")
                hookReq.httpBody = bodyData
                _ = try? await URLSession.shared.data(for: hookReq)
            }
        } catch {
            lastSyncStatus = "Lỗi đẩy Cloud: \(error.localizedDescription)"
        }
    }

    private static func parseCloudResponseData(_ data: Data) -> [NotiItem] {
        let decoder = JSONDecoder()
        if let directArray = try? decoder.decode([NotiItem].self, from: data) {
            return directArray
        }
        if let singleItem = try? decoder.decode(NotiItem.self, from: data) {
            return [singleItem]
        }
        guard let jsonObj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return []
        }
        let candidateKeys = ["notifications", "items", "data", "records", "result"]
        for key in candidateKeys {
            if let arr = jsonObj[key],
               let subData = try? JSONSerialization.data(withJSONObject: arr),
               let decoded = try? decoder.decode([NotiItem].self, from: subData) {
                return decoded
            }
        }
        return []
    }

    // MARK: - Backup Export / Import (.JSON & UTF-8 .CSV)

    func exportJSONFileURL() -> URL? {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        guard let data = try? encoder.encode(notifications) else { return nil }
        let fileName = "NotiStarCloud_Backup_\(Int(Date().timeIntervalSince1970)).json"
        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent(fileName)
        do {
            try data.write(to: tempURL, options: .atomic)
            return tempURL
        } catch {
            return nil
        }
    }

    func exportCSVFileURL() -> URL? {
        var csv = "\u{FEFF}ID,Time,DateStr,AppName,PackageName,Title,ContentText,BigText,IsRevoked,IsStarred,IsSynced,OTP,BankAmount\n"
        for item in notifications {
            let otp = item.extractedOTP ?? ""
            let bankAmt = item.bankingTransaction?.formattedAmount ?? ""
            let row = [
                Self.escapeCSV(item.id),
                "\(item.time)",
                Self.escapeCSV(item.dateStr),
                Self.escapeCSV(item.appName),
                Self.escapeCSV(item.packageName),
                Self.escapeCSV(item.title),
                Self.escapeCSV(item.contentText),
                Self.escapeCSV(item.bigText),
                item.isRevoked ? "TRUE" : "FALSE",
                item.isStarred ? "TRUE" : "FALSE",
                item.isSynced ? "TRUE" : "FALSE",
                Self.escapeCSV(otp),
                Self.escapeCSV(bankAmt)
            ].joined(separator: ",")
            csv.append(row + "\n")
        }

        let fileName = "NotiStarCloud_Excel_\(Int(Date().timeIntervalSince1970)).csv"
        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent(fileName)
        do {
            try csv.data(using: .utf8)?.write(to: tempURL, options: .atomic)
            return tempURL
        } catch {
            return nil
        }
    }

    func importBackupFile(from url: URL) -> Int {
        let accessed = url.startAccessingSecurityScopedResource()
        defer {
            if accessed { url.stopAccessingSecurityScopedResource() }
        }

        guard let data = try? Data(contentsOf: url) else { return 0 }
        if let decoded = try? JSONDecoder().decode([NotiItem].self, from: data) {
            var count = 0
            for item in decoded {
                if !notifications.contains(where: { $0.id == item.id }) {
                    notifications.append(item)
                    count += 1
                }
            }
            saveLocalNotifications()
            lastSyncStatus = "Đã nhập thành công \(count) thông báo từ file JSON"
            return count
        }
        return 0
    }

    private static func escapeCSV(_ value: String) -> String {
        let cleaned = value.replacingOccurrences(of: "\"", with: "\"\"")
            .replacingOccurrences(of: "\r\n", with: " ")
            .replacingOccurrences(of: "\n", with: " ")
        return "\"\(cleaned)\""
    }

    // MARK: - Initial Showcase Data

    static func createInitialShowcaseItems() -> [NotiItem] {
        let now = Int64(Date().timeIntervalSince1970 * 1000)
        return [
            NotiItem(
                id: "demo_revoked_zalo_1",
                key: "com.zing.zalo|1001|\(now - 60000)",
                notificationId: 1001,
                packageName: "com.zing.zalo",
                appName: "Zalo",
                title: "Nguyễn Minh Anh (Zalo)",
                contentText: "Tối nay nhớ chuyển khoản cọc hợp đồng 15 triệu qua số 0912345678 nhé, tài liệu tại https://drive.google.com/file/d/contract2026",
                bigText: "Tối nay nhớ chuyển khoản cọc hợp đồng 15 triệu qua số 0912345678 nhé, tài liệu tại https://drive.google.com/file/d/contract2026",
                time: now - 60000,
                isStarred: true,
                isSynced: true,
                isRevoked: true
            ),
            NotiItem(
                id: "demo_bank_vcb_2",
                key: "com.VCB|1002|\(now - 180000)",
                notificationId: 1002,
                packageName: "com.VCB",
                appName: "Vietcombank",
                title: "Biến động số dư VCB Digibank",
                contentText: "SD TK 0071001234567 +5,500,000 VND lúc 14:20. Số dư: 48,250,000 VND. ND: THANH TOAN DON HANG NOTISTAR CLOUD",
                bigText: "SD TK 0071001234567 +5,500,000 VND lúc 14:20. Số dư: 48,250,000 VND. ND: THANH TOAN DON HANG NOTISTAR CLOUD",
                time: now - 180000,
                isStarred: true,
                isSynced: true,
                isRevoked: false
            ),
            NotiItem(
                id: "demo_otp_tcb_3",
                key: "vn.com.techcombank.bb.app|1003|\(now - 320000)",
                notificationId: 1003,
                packageName: "vn.com.techcombank.bb.app",
                appName: "Techcombank",
                title: "Smart OTP Xác Thực Giao Dịch",
                contentText: "Mã xác thực OTP của quý khách là 849201. Tuyệt đối không chia sẻ mã này cho bất kỳ ai.",
                bigText: "Mã xác thực OTP của quý khách là 849201. Tuyệt đối không chia sẻ mã này cho bất kỳ ai.",
                time: now - 320000,
                isStarred: false,
                isSynced: true,
                isRevoked: false
            ),
            NotiItem(
                id: "demo_bank_mb_4",
                key: "com.mbmobile|1004|\(now - 540000)",
                notificationId: 1004,
                packageName: "com.mbmobile",
                appName: "MB Bank",
                title: "Thông báo biến động số dư",
                contentText: "TK 999988886666GD: -350,000 VND. Số dư: 12,400,000 VND. ND: Thanh toan hoa don Apple Services.",
                bigText: "TK 999988886666GD: -350,000 VND. Số dư: 12,400,000 VND. ND: Thanh toan hoa don Apple Services.",
                time: now - 540000,
                isStarred: false,
                isSynced: true,
                isRevoked: false
            )
        ]
    }
}
