import Foundation
import AppIntents

@available(iOS 16.0, *)
struct CaptureNotificationIntent: AppIntent {
    static var title: LocalizedStringResource = "Lưu thông báo vào NotiStar Cloud"
    static var description = IntentDescription(
        "Lưu ngay nội dung tin nhắn, biến động số dư hoặc thông báo vào NotiStar Cloud và đồng bộ lên Google Drive (dùng cho Tự động hóa Phím tắt iOS / Chạm mặt lưng)."
    )

    static var openAppWhenRun: Bool = false

    @Parameter(title: "Tên ứng dụng (VD: Zalo, Messenger, VCB)", default: "Shortcuts iOS")
    var appName: String

    @Parameter(title: "Người gửi / Tiêu đề", default: "Thông báo tự động")
    var senderTitle: String

    @Parameter(title: "Nội dung thông báo / tin nhắn")
    var messageContent: String

    @Parameter(title: "Đánh dấu Đã thu hồi?", default: false)
    var isRevoked: Bool

    static var parameterSummary: some ParameterSummary {
        Summary("Lưu thông báo từ \(\.$appName): \(\.$senderTitle) - \(\.$messageContent)") {
            \.$isRevoked
        }
    }

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let nowMs = Int64(Date().timeIntervalSince1970 * 1000)
        let pkg = "ios.shortcut." + appName.lowercased().replacingOccurrences(of: " ", with: "")
        let newItem = NotiItem(
            id: "ios_intent_\(nowMs)_\(Int.random(in: 100...999))",
            key: "\(pkg)|\(nowMs)",
            notificationId: Int(nowMs % 100000),
            packageName: pkg,
            appName: appName.isEmpty ? "Shortcuts iOS" : appName,
            title: senderTitle.isEmpty ? appName : senderTitle,
            contentText: messageContent,
            bigText: messageContent,
            inboxLines: messageContent.components(separatedBy: "\n"),
            time: nowMs,
            isStarred: false,
            isSynced: false,
            isRevoked: isRevoked
        )

        await GoogleCloudSyncService.enqueueShortcutItem(newItem)

        await MainActor.run {
            GoogleCloudSyncService.shared.addOrMergeNotification(newItem, triggerCloudPush: false)
        }
        await GoogleCloudSyncService.shared.pushItemsToCloud([newItem])

        return .result(dialog: "Đã lưu thông báo từ \(appName) vào NotiStar Cloud & Google Drive!")
    }
}

@available(iOS 16.0, *)
struct SyncCloudShortcutIntent: AppIntent {
    static var title: LocalizedStringResource = "Đồng bộ NotiStar Cloud ngay"
    static var description = IntentDescription("Kéo toàn bộ tin nhắn thu hồi và thông báo mới nhất từ Google Drive về iPhone.")
    static var openAppWhenRun: Bool = false

    func perform() async throws -> some IntentResult & ProvidesDialog {
        await GoogleCloudSyncService.shared.pullFromCloud(silent: false)
        let count = await MainActor.run { GoogleCloudSyncService.shared.notifications.count }
        return .result(dialog: "Đã đồng bộ thành công! Hiện có \(count) thông báo trong NotiStar Cloud.")
    }
}

@available(iOS 16.0, *)
struct NotiStarShortcutsProvider: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: CaptureNotificationIntent(),
            phrases: [
                "Lưu thông báo vào \(.applicationName)",
                "Ghi tin nhắn vào \(.applicationName)"
            ],
            shortTitle: "Lưu thông báo Cloud",
            systemImageName: "bell.badge.fill"
        )
        AppShortcut(
            intent: SyncCloudShortcutIntent(),
            phrases: [
                "Đồng bộ \(.applicationName)",
                "Cập nhật tin nhắn thu hồi \(.applicationName)"
            ],
            shortTitle: "Đồng bộ Google Drive",
            systemImageName: "icloud.and.arrow.down.fill"
        )
    }
}
