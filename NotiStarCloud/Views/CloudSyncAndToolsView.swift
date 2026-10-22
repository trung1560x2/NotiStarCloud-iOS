import SwiftUI
import UniformTypeIdentifiers
import UIKit

struct CloudSyncAndToolsView: View {
    @ObservedObject var syncService = GoogleCloudSyncService.shared
    @ObservedObject var securityService = VoiceAnnouncerAndSecurityService.shared
    @Environment(\.dismiss) private var dismiss

    @State private var showFileImporter: Bool = false
    @State private var exportedFileURL: URL?
    @State private var showShareSheet: Bool = false
    @State private var statusBanner: String?

    // Manual quick-create notification form
    @State private var customApp: String = "Zalo"
    @State private var customSender: String = ""
    @State private var customBody: String = ""
    @State private var customIsRevoked: Bool = false

    var body: some View {
        NavigationStack {
            Form {
                // Section 1: Google Drive & Apps Script Cloud Sync
                Section {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Trạng thái: \(syncService.lastSyncStatus)")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.green)

                        Toggle("Tự động đồng bộ hai chiều (45 giây)", isOn: $syncService.autoSyncEnabled)
                            .font(.system(size: 14))
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Google Drive Folder ID")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("Drive Folder ID", text: $syncService.driveFolderId)
                            .font(.system(size: 13, design: .monospaced))
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Google Apps Script Web App URL")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("https://script.google.com/macros/s/.../exec", text: $syncService.webAppUrl)
                            .font(.system(size: 12, design: .monospaced))
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Webhook phụ (Telegram / Discord / Custom JSON - Tùy chọn)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("https://api.telegram.org/...", text: $syncService.customWebhookUrl)
                            .font(.system(size: 12, design: .monospaced))
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                    }

                    Button {
                        Task {
                            await syncService.pullFromCloud(silent: false)
                            showBanner("Đã tải dữ liệu mới nhất từ Google Drive!")
                        }
                    } label: {
                        HStack {
                            Image(systemName: "icloud.and.arrow.down.fill")
                            Text("Kéo thông báo & tin thu hồi từ Google Drive")
                                .fontWeight(.semibold)
                            if syncService.isSyncing {
                                Spacer()
                                ProgressView()
                            }
                        }
                    }
                    .foregroundColor(.cyan)

                    Button {
                        Task {
                            await syncService.pushItemsToCloud(syncService.notifications)
                            showBanner("Đã đẩy toàn bộ thông báo lên Google Drive!")
                        }
                    } label: {
                        Label("Đẩy toàn bộ dữ liệu iPhone lên Google Drive", systemImage: "icloud.and.arrow.up.fill")
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.green)

                    Button {
                        syncService.driveFolderId = CloudConstants.DEFAULT_DRIVE_FOLDER_ID
                        syncService.webAppUrl = CloudConstants.DEFAULT_WEBAPP_URL
                        showBanner("Đã khôi phục cấu hình Google Cloud mặc định!")
                    } label: {
                        Label("Khôi phục cấu hình Cloud mặc định", systemImage: "arrow.counterclockwise")
                            .font(.system(size: 13))
                    }
                    .foregroundColor(.orange)
                } header: {
                    Text("☁️ ĐỒNG BỘ GOOGLE DRIVE & APPS SCRIPT")
                }

                // Section 2: Vietnamese Voice Announcer & Security
                Section {
                    Toggle("🔊 Đọc số tiền chuyển khoản (Ting ting!)", isOn: $securityService.isVoiceBankEnabled)
                    Toggle("🚨 Đọc cảnh báo khi có tin nhắn thu hồi", isOn: $securityService.isVoiceRevokedEnabled)

                    Button {
                        securityService.testVoiceAnnouncement()
                    } label: {
                        Label("Nghe thử giọng đọc Tiếng Việt (vi-VN)", systemImage: "speaker.wave.3.fill")
                            .foregroundColor(.cyan)
                    }

                    Toggle("🙈 Chế độ che mờ nội dung riêng tư (Privacy Mask)", isOn: $securityService.isPrivacyMaskActive)
                    Toggle("🔒 Khóa ứng dụng bằng FaceID / TouchID & PIN", isOn: $securityService.isBiometricLockEnabled)

                    HStack {
                        Text("Mã PIN dự phòng (4 số)")
                        Spacer()
                        TextField("1234", text: $securityService.savedPinCode)
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 90)
                            .font(.system(size: 15, weight: .bold, design: .monospaced))
                    }
                } header: {
                    Text("🛡️ GIỌNG ĐỌC TIẾNG VIỆT & BẢO MẬT FACEID")
                }

                // Section 3: Backup & Restore (.JSON & .CSV)
                Section {
                    Button {
                        if let url = syncService.exportJSONFileURL() {
                            exportedFileURL = url
                            showShareSheet = true
                        }
                    } label: {
                        Label("Xuất file sao lưu chuẩn (.JSON)", systemImage: "Curlybraces")
                    }

                    Button {
                        if let url = syncService.exportCSVFileURL() {
                            exportedFileURL = url
                            showShareSheet = true
                        }
                    } label: {
                        Label("Xuất bảng tính Excel Tiếng Việt (.CSV UTF-8)", systemImage: "tablecells.fill")
                    }

                    Button {
                        showFileImporter = true
                    } label: {
                        Label("Nhập file sao lưu (.JSON) từ Tệp / iCloud / Drive", systemImage: "square.and.arrow.down.on.square.fill")
                            .foregroundColor(.yellow)
                    }
                } header: {
                    Text("💾 SAO LƯU & KHÔI PHỤC DỮ LIỆU")
                }

                // Section 4: Quick Add / Simulate Notification
                Section {
                    TextField("Tên ứng dụng (VD: Zalo, Messenger, VCB)", text: $customApp)
                    TextField("Người gửi / Tiêu đề", text: $customSender)
                    TextField("Nội dung tin nhắn / số tiền / link...", text: $customBody)
                    Toggle("Đánh dấu là Tin nhắn đã thu hồi (🚫)", isOn: $customIsRevoked)

                    Button {
                        guard !customBody.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
                        let nowMs = Int64(Date().timeIntervalSince1970 * 1000)
                        let item = NotiItem(
                            id: "ios_manual_\(nowMs)",
                            key: "ios.manual|\(nowMs)",
                            notificationId: Int(nowMs % 100000),
                            packageName: "ios.manual.\(customApp.lowercased())",
                            appName: customApp.isEmpty ? "Ghi chú iOS" : customApp,
                            title: customSender.isEmpty ? customApp : customSender,
                            contentText: customBody,
                            bigText: customBody,
                            time: nowMs,
                            isStarred: false,
                            isSynced: false,
                            isRevoked: customIsRevoked
                        )
                        syncService.addOrMergeNotification(item, triggerCloudPush: true)
                        customBody = ""
                        showBanner("Đã lưu & đồng bộ lên Google Drive!")
                    } label: {
                        Label("Lưu & Đồng bộ lên Cloud ngay", systemImage: "plus.circle.fill")
                            .fontWeight(.bold)
                            .foregroundColor(.green)
                    }
                } header: {
                    Text("✍️ GHI NHANH / GIẢ LẬP THÔNG BÁO MỚI")
                }

                // Section 5: iOS Shortcuts & Jailbreak BulletinBoard Guide
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("1. Máy iPhone KHÔNG Jailbreak (iOS 16 - iOS 18):")
                            .font(.system(size: 13, weight: .bold))
                            .foregroundColor(.cyan)
                        Text("• Mở ứng dụng Phím tắt (Shortcuts) → Tự động hóa (Automation) → Khi nhận được Tin nhắn / Email / Giao dịch hoặc Chạm vào mặt lưng (Back Tap).\n• Chọn hành động \"Lưu thông báo vào NotiStar Cloud\" để tự động đẩy mọi thông báo lên Google Drive.\n• Hoặc dùng tính năng đồng bộ 2 chiều để xem tức thì mọi tin nhắn Zalo/Messenger bị thu hồi từ máy phụ Android.")
                            .font(.system(size: 12))
                            .foregroundColor(.secondary)

                        Divider()

                        Text("2. Máy iPhone ĐÃ Jailbreak (Dopamine / Palera1n / Unc0ver):")
                            .font(.system(size: 13, weight: .bold))
                            .foregroundColor(.orange)
                        Text("• Cài gói tinh chỉnh `NotiStarCloudTweak` (trong thư mục `JailbreakTweak/Tweak.x`).\n• Tweak móc trực tiếp vào `BBServer` (`BulletinBoard.framework`) của SpringBoard để bắt 100% thông báo hệ thống và chặn lệnh thu hồi `withdrawBulletinRequests` của Zalo/Messenger/Telegram theo thời gian thực.")
                            .font(.system(size: 12))
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 4)
                } header: {
                    Text("📱 HƯỚNG DẪN BẮT THÔNG BÁO TRÊN iOS")
                }
            }
            .navigationTitle("Cấu hình Cloud & Công cụ")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Xong") {
                        dismiss()
                    }
                    .fontWeight(.bold)
                }
            }
            .fileImporter(
                isPresented: $showFileImporter,
                allowedContentTypes: [.json, .plainText],
                allowsMultipleSelection: false
            ) { result in
                if case .success(let urls) = result, let firstURL = urls.first {
                    let count = syncService.importBackupFile(from: firstURL)
                    showBanner("Đã nhập thêm \(count) thông báo từ file sao lưu!")
                }
            }
            .sheet(isPresented: $showShareSheet) {
                if let url = exportedFileURL {
                    ActivityShareSheet(items: [url])
                }
            }
            .overlay(alignment: .bottom) {
                if let banner = statusBanner {
                    Text(banner)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Capsule().fill(Color.green.opacity(0.92)))
                        .padding(.bottom, 20)
                }
            }
        }
    }

    private func showBanner(_ text: String) {
        withAnimation {
            statusBanner = text
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.4) {
            withAnimation {
                statusBanner = nil
            }
        }
    }
}

// MARK: - Banking Ledger Summary Sheet

struct BankingLedgerSheetView: View {
    @ObservedObject var syncService = GoogleCloudSyncService.shared
    @Environment(\.dismiss) private var dismiss

    private var transactions: [BankingTransaction] {
        syncService.notifications.compactMap { $0.bankingTransaction }
    }

    private var totalCredit: Double {
        transactions.filter { $0.isCredit }.reduce(0) { $0 + $1.amount }
    }

    private var totalDebit: Double {
        transactions.filter { !$0.isCredit }.reduce(0) { $0 + $1.amount }
    }

    private func formatVND(_ value: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        formatter.maximumFractionDigits = 0
        return (formatter.string(from: NSNumber(value: value)) ?? "0") + " đ"
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color(red: 0.05, green: 0.06, blue: 0.09).ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 16) {
                        // Summary Cards
                        HStack(spacing: 12) {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("TỔNG TIỀN VÀO (+)")
                                    .font(.system(size: 11, weight: .bold))
                                    .foregroundColor(.green.opacity(0.85))
                                Text("+\(formatVND(totalCredit))")
                                    .font(.system(size: 17, weight: .heavy))
                                    .foregroundColor(.green)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(14)
                            .background(RoundedRectangle(cornerRadius: 16).fill(Color.green.opacity(0.12)))

                            VStack(alignment: .leading, spacing: 6) {
                                Text("TỔNG TIỀN RA (-)")
                                    .font(.system(size: 11, weight: .bold))
                                    .foregroundColor(.orange.opacity(0.85))
                                Text("-\(formatVND(totalDebit))")
                                    .font(.system(size: 17, weight: .heavy))
                                    .foregroundColor(.orange)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(14)
                            .background(RoundedRectangle(cornerRadius: 16).fill(Color.orange.opacity(0.12)))
                        }

                        // Net Balance Card
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("CHÊNH LỆCH DÒNG TIỀN RÒNG")
                                    .font(.system(size: 11, weight: .bold))
                                    .foregroundColor(.gray)
                                let net = totalCredit - totalDebit
                                Text((net >= 0 ? "+" : "-") + formatVND(abs(net)))
                                    .font(.system(size: 20, weight: .black))
                                    .foregroundColor(net >= 0 ? .cyan : .red)
                            }
                            Spacer()
                            Text("\(transactions.count) giao dịch")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundColor(.white.opacity(0.8))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(Capsule().fill(Color.white.opacity(0.1)))
                        }
                        .padding(14)
                        .background(RoundedRectangle(cornerRadius: 16).fill(Color(red: 0.10, green: 0.12, blue: 0.17)))

                        // Transaction List
                        if transactions.isEmpty {
                            Text("Chưa có thông báo biến động số dư ngân hàng nào.")
                                .foregroundColor(.gray)
                                .padding(.top, 40)
                        } else {
                            ForEach(transactions) { tx in
                                VStack(alignment: .leading, spacing: 6) {
                                    HStack {
                                        Text(tx.bankName)
                                            .font(.system(size: 14, weight: .bold))
                                            .foregroundColor(.cyan)
                                        Spacer()
                                        Text(tx.formattedAmount)
                                            .font(.system(size: 15, weight: .heavy))
                                            .foregroundColor(tx.isCredit ? .green : .orange)
                                    }

                                    Text(tx.note)
                                        .font(.system(size: 13))
                                        .foregroundColor(.white.opacity(0.9))
                                        .lineLimit(3)

                                    HStack {
                                        if let bal = tx.balanceAfter {
                                            Text("Số dư: \(bal)")
                                                .font(.system(size: 11, weight: .semibold))
                                                .foregroundColor(.yellow)
                                        }
                                        Spacer()
                                        Text(tx.dateStr)
                                            .font(.system(size: 11))
                                            .foregroundColor(.gray)
                                    }
                                }
                                .padding(13)
                                .background(RoundedRectangle(cornerRadius: 14).fill(Color(red: 0.10, green: 0.12, blue: 0.16)))
                            }
                        }
                    }
                    .padding(16)
                }
            }
            .navigationTitle("🏦 Sổ Cái Biến Động Số Dư")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Đóng") { dismiss() }
                }
            }
        }
    }
}

// MARK: - Smart Link / Phone / Email / OTP Extractor Sheet

struct SmartExtractorVaultSheetView: View {
    @ObservedObject var syncService = GoogleCloudSyncService.shared
    @Environment(\.dismiss) private var dismiss
    @State private var selectedType: ExtractedEntity.EntityType? = nil
    @State private var copiedValue: String? = nil

    private var allEntities: [ExtractedEntity] {
        let flat = syncService.notifications.flatMap { $0.extractedEntities }
        if let filter = selectedType {
            return flat.filter { $0.type == filter }
        }
        return flat
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color(red: 0.05, green: 0.06, blue: 0.09).ignoresSafeArea()

                VStack(spacing: 0) {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            filterChip(title: "Tất cả (\(syncService.notifications.flatMap { $0.extractedEntities }.count))", type: nil)
                            ForEach(ExtractedEntity.EntityType.allCases, id: \.self) { t in
                                filterChip(title: t.rawValue, type: t)
                            }
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                    }
                    .background(Color(red: 0.09, green: 0.10, blue: 0.14))

                    if allEntities.isEmpty {
                        Spacer()
                        Text("Không tìm thấy Link, Số điện thoại, Email hay OTP nào.")
                            .foregroundColor(.gray)
                        Spacer()
                    } else {
                        List {
                            ForEach(allEntities) { entity in
                                HStack(spacing: 12) {
                                    Image(systemName: entity.type.iconName)
                                        .font(.system(size: 20))
                                        .foregroundColor(colorForEntity(entity.type))

                                    VStack(alignment: .leading, spacing: 4) {
                                        HStack {
                                            Text(entity.value)
                                                .font(.system(size: 14, weight: .bold))
                                                .foregroundColor(.white)
                                                .lineLimit(2)
                                            if entity.isRevoked {
                                                Text("🚫 Thu hồi")
                                                    .font(.system(size: 10, weight: .bold))
                                                    .foregroundColor(.white)
                                                    .padding(.horizontal, 6)
                                                    .padding(.vertical, 2)
                                                    .background(Capsule().fill(Color.red))
                                            }
                                        }
                                        Text("\(entity.sourceApp) · \(entity.sourceTitle) · \(entity.dateStr)")
                                            .font(.system(size: 11))
                                            .foregroundColor(.gray)
                                    }

                                    Spacer()

                                    Button {
                                        UIPasteboard.general.string = entity.value
                                        copiedValue = entity.value
                                    } label: {
                                        Image(systemName: copiedValue == entity.value ? "checkmark.circle.fill" : "doc.on.doc")
                                            .foregroundColor(copiedValue == entity.value ? .green : .cyan)
                                    }
                                    .buttonStyle(.plain)

                                    if let actionURL = actionURL(for: entity) {
                                        Link(destination: actionURL) {
                                            Image(systemName: "arrow.up.right.square.fill")
                                                .foregroundColor(.green)
                                        }
                                        .buttonStyle(.plain)
                                    }
                                }
                                .listRowBackground(Color(red: 0.10, green: 0.12, blue: 0.16))
                            }
                        }
                        .scrollContentBackground(.hidden)
                    }
                }
            }
            .navigationTitle("🔗 Kho Trích Xuất Link / SĐT / OTP")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Đóng") { dismiss() }
                }
            }
        }
    }

    private func filterChip(title: String, type: ExtractedEntity.EntityType?) -> some View {
        let isSelected = selectedType == type
        return Button {
            selectedType = type
        } label: {
            Text(title)
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(isSelected ? .black : .white)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Capsule().fill(isSelected ? Color.cyan : Color.white.opacity(0.12)))
        }
    }

    private func colorForEntity(_ type: ExtractedEntity.EntityType) -> Color {
        switch type {
        case .link: return .cyan
        case .phone: return .green
        case .email: return .orange
        case .otp: return .yellow
        }
    }

    private func actionURL(for entity: ExtractedEntity) -> URL? {
        switch entity.type {
        case .link:
            return URL(string: entity.value)
        case .phone:
            return URL(string: "tel:\(entity.value)")
        case .email:
            return URL(string: "mailto:\(entity.value)")
        case .otp:
            return nil
        }
    }
}

struct ActivityShareSheet: UIViewControllerRepresentable {
    let items: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}
