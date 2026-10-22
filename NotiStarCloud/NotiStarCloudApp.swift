import SwiftUI

@main
struct NotiStarCloudApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var syncService = GoogleCloudSyncService.shared
    @StateObject private var securityService = VoiceAnnouncerAndSecurityService.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .onChange(of: scenePhase) { newPhase in
                    securityService.handleScenePhase(newPhase)
                    if newPhase == .active {
                        syncService.loadLocalNotifications()
                        if syncService.autoSyncEnabled {
                            Task {
                                await syncService.pullFromCloud(silent: true)
                            }
                        }
                    }
                }
                .onOpenURL { incomingURL in
                    handleIncomingURL(incomingURL)
                }
        }
    }

    private func handleIncomingURL(_ url: URL) {
        // 1. Handle .json backup file opened directly from iPhone Files / AirDrop / Drive
        if url.pathExtension.lowercased() == "json" {
            _ = syncService.importBackupFile(from: url)
            return
        }

        // 2. Handle URL Scheme: notistarcloud://capture?app=Zalo&title=Sender&body=Hello&revoked=1
        guard url.scheme?.lowercased() == "notistarcloud" else { return }
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false) else { return }
        let queryItems = components.queryItems ?? []

        func param(_ name: String) -> String {
            queryItems.first(where: { $0.name.lowercased() == name.lowercased() })?.value ?? ""
        }

        let appName = param("app").isEmpty ? "URL Shortcut iOS" : param("app")
        let title = param("title").isEmpty ? appName : param("title")
        let body = param("body")
        let isRevoked = ["1", "true", "yes"].contains(param("revoked").lowercased())

        guard !body.isEmpty else { return }
        let nowMs = Int64(Date().timeIntervalSince1970 * 1000)
        let newItem = NotiItem(
            id: "ios_url_\(nowMs)",
            key: "ios.url.\(appName.lowercased())|\(nowMs)",
            notificationId: Int(nowMs % 100000),
            packageName: "ios.url.\(appName.lowercased())",
            appName: appName,
            title: title,
            contentText: body,
            bigText: body,
            time: nowMs,
            isStarred: false,
            isSynced: false,
            isRevoked: isRevoked
        )
        syncService.addOrMergeNotification(newItem, triggerCloudPush: true)
    }
}
