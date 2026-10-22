import SwiftUI
import UIKit

struct ContentView: View {
    @ObservedObject var syncService = GoogleCloudSyncService.shared
    @ObservedObject var securityService = VoiceAnnouncerAndSecurityService.shared

    @State private var selectedFilter: NotiFilterCategory = .all
    @State private var searchText: String = ""
    @State private var showCloudToolsSheet: Bool = false
    @State private var showBankingLedgerSheet: Bool = false
    @State private var showExtractorVaultSheet: Bool = false
    @State private var pinInput: String = ""
    @State private var toastMessage: String?

    private var filteredNotifications: [NotiItem] {
        let base: [NotiItem]
        switch selectedFilter {
        case .all:
            base = syncService.notifications
        case .messages:
            base = syncService.notifications.filter { $0.isMessageApp }
        case .revoked:
            base = syncService.notifications.filter { $0.isRevoked }
        case .starred:
            base = syncService.notifications.filter { $0.isStarred }
        case .mediaVault:
            base = syncService.notifications.filter { $0.hasMediaImage }
        case .banking:
            base = syncService.notifications.filter { $0.bankingTransaction != nil }
        case .linksAndPhones:
            base = syncService.notifications.filter { !$0.extractedEntities.isEmpty }
        }

        let q = searchText.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !q.isEmpty else { return base }
        return base.filter { $0.searchableText.lowercased().contains(q) }
    }

    var body: some View {
        NavigationStack {
            ZStack {
                // OneUI 7 / iOS 18 Deep Dark Background
                LinearGradient(
                    colors: [
                        Color(red: 0.04, green: 0.05, blue: 0.08),
                        Color(red: 0.07, green: 0.08, blue: 0.13)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                VStack(spacing: 0) {
                    topHeaderDashboard
                    searchAndClipboardBar
                    filterChipsScrollBar

                    if filteredNotifications.isEmpty {
                        emptyStateView
                    } else {
                        List {
                            ForEach(filteredNotifications) { item in
                                ZStack {
                                    NavigationLink(destination: MessageHistoryView(initialItem: item)) {
                                        EmptyView()
                                    }
                                    .opacity(0)

                                    notificationCard(for: item)
                                }
                                .listRowBackground(Color.clear)
                                .listRowSeparator(.hidden)
                                .listRowInsets(EdgeInsets(top: 6, leading: 14, bottom: 6, trailing: 14))
                                .swipeActions(edge: .leading, allowsFullSwipe: true) {
                                    Button {
                                        syncService.toggleStar(for: item)
                                    } label: {
                                        Label(item.isStarred ? "Bỏ sao" : "Đánh dấu ★", systemImage: "star.fill")
                                    }
                                    .tint(.yellow)

                                    if !item.isRevoked {
                                        Button {
                                            syncService.markAsRevoked(for: item)
                                            showToast("Đã đánh dấu Thu hồi & giữ lại nội dung!")
                                        } label: {
                                            Label("Thu hồi", systemImage: "exclamationmark.shield.fill")
                                        }
                                        .tint(.orange)
                                    }
                                }
                                .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                                    Button(role: .destructive) {
                                        syncService.deleteNotification(item)
                                    } label: {
                                        Label("Xóa", systemImage: "trash.fill")
                                    }
                                }
                            }
                        }
                        .listStyle(.plain)
                        .scrollContentBackground(.hidden)
                        .refreshable {
                            await syncService.pullFromCloud(silent: false)
                        }
                    }
                }

                // Biometric / PIN Lock Screen Overlay
                if securityService.isBiometricLockEnabled && !securityService.isUnlocked {
                    biometricLockOverlay
                }

                // Floating Toast Feedback
                if let toast = toastMessage {
                    VStack {
                        Spacer()
                        Text(toast)
                            .font(.system(size: 13, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 18)
                            .padding(.vertical, 11)
                            .background(Capsule().fill(Color.green.opacity(0.95)))
                            .shadow(color: .black.opacity(0.4), radius: 8, y: 4)
                            .padding(.bottom, 26)
                    }
                    .transition(.move(edge: .bottom).combined(with: .opacity))
                }
            }
            .navigationBarHidden(true)
            .sheet(isPresented: $showCloudToolsSheet) {
                CloudSyncAndToolsView()
            }
            .sheet(isPresented: $showBankingLedgerSheet) {
                BankingLedgerSheetView()
            }
            .sheet(isPresented: $showExtractorVaultSheet) {
                SmartExtractorVaultSheetView()
            }
            .task {
                await syncService.pullFromCloud(silent: true)
            }
        }
        .preferredColorScheme(.dark)
    }

    // MARK: - Top Header Dashboard

    private var topHeaderDashboard: some View {
        VStack(spacing: 10) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 3) {
                    HStack(spacing: 6) {
                        Text("NotiStar Cloud")
                            .font(.system(size: 24, weight: .black, design: .rounded))
                            .foregroundColor(.white)

                        Text("OneUI 7 · iOS")
                            .font(.system(size: 11, weight: .heavy))
                            .foregroundColor(.black)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Capsule().fill(Color.cyan))
                    }

                    HStack(spacing: 6) {
                        Circle()
                            .fill(syncService.isSyncing ? Color.yellow : Color.green)
                            .frame(width: 7, height: 7)
                        Text(syncService.lastSyncStatus)
                            .font(.system(size: 11, weight: .medium))
                            .foregroundColor(.gray)
                            .lineLimit(1)
                    }
                }

                Spacer()

                // Quick Privacy Mask Toggle (🙈)
                Button {
                    securityService.isPrivacyMaskActive.toggle()
                    showToast(securityService.isPrivacyMaskActive ? "🙈 Đã bật che mờ nội dung nhạy cảm" : "👁️ Đã hiện nội dung thông báo")
                } label: {
                    Text(securityService.isPrivacyMaskActive ? "🙈" : "👁️")
                        .font(.system(size: 18))
                        .frame(width: 38, height: 38)
                        .background(
                            Circle()
                                .fill(securityService.isPrivacyMaskActive ? Color.orange.opacity(0.28) : Color.white.opacity(0.1))
                        )
                }

                // Banking Ledger Button
                Button {
                    showBankingLedgerSheet = true
                } label: {
                    Image(systemName: "building.columns.fill")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundColor(.green)
                        .frame(width: 38, height: 38)
                        .background(Circle().fill(Color.green.opacity(0.15)))
                }

                // Cloud Sync & Settings Button
                Button {
                    showCloudToolsSheet = true
                } label: {
                    Image(systemName: "icloud.and.arrow.up.fill")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.cyan)
                        .frame(width: 38, height: 38)
                        .background(Circle().fill(Color.cyan.opacity(0.16)))
                }
            }

            // Stats Strip
            HStack(spacing: 8) {
                statPill(
                    label: "Tổng lưu",
                    value: "\(syncService.notifications.count)",
                    color: .cyan
                ) {
                    selectedFilter = .all
                }

                statPill(
                    label: "🚫 Thu hồi",
                    value: "\(syncService.notifications.filter { $0.isRevoked }.count)",
                    color: .red
                ) {
                    selectedFilter = .revoked
                }

                statPill(
                    label: "🏦 Ngân hàng",
                    value: "\(syncService.notifications.filter { $0.bankingTransaction != nil }.count)",
                    color: .green
                ) {
                    showBankingLedgerSheet = true
                }

                statPill(
                    label: "🔗 Link/SĐT",
                    value: "\(syncService.notifications.flatMap { $0.extractedEntities }.count)",
                    color: .orange
                ) {
                    showExtractorVaultSheet = true
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 10)
        .padding(.bottom, 8)
    }

    private func statPill(label: String, value: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 2) {
                Text(value)
                    .font(.system(size: 15, weight: .heavy, design: .rounded))
                    .foregroundColor(color)
                Text(label)
                    .font(.system(size: 10, weight: .semibold))
                    .foregroundColor(.white.opacity(0.75))
                    .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 7)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(color.opacity(0.11))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color.opacity(0.25), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: - Search & Clipboard Vault Bar

    private var searchAndClipboardBar: some View {
        HStack(spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.gray)
                    .font(.system(size: 14))

                TextField("Tìm tin nhắn, số tiền, SĐT, ứng dụng...", text: $searchText)
                    .font(.system(size: 14))
                    .foregroundColor(.white)
                    .autocorrectionDisabled()

                if !searchText.isEmpty {
                    Button {
                        searchText = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.gray)
                    }
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 9)
            .background(
                RoundedRectangle(cornerRadius: 14)
                    .fill(Color.white.opacity(0.08))
            )

            // Clipboard Vault Button (📋 Lưu Clipboard)
            Button {
                if syncService.saveFromClipboard() {
                    showToast("📋 Đã lưu Clipboard vào NotiStar & đẩy lên Google Drive!")
                } else {
                    showToast("Bộ nhớ tạm (Clipboard) hiện đang trống!")
                }
            } label: {
                Text("📋 Lưu Clipboard")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundColor(.black)
                    .padding(.horizontal, 11)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 14)
                            .fill(Color.cyan)
                    )
            }

            // Quick Cloud Pull Button
            Button {
                Task {
                    await syncService.pullFromCloud(silent: false)
                    showToast("☁️ Đã cập nhật từ Google Drive!")
                }
            } label: {
                Image(systemName: "arrow.triangle.2.circlepath")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.white)
                    .frame(width: 38, height: 38)
                    .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.12)))
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 6)
    }

    // MARK: - Filter Chips Bar

    private var filterChipsScrollBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(NotiFilterCategory.allCases) { category in
                    let isSelected = selectedFilter == category
                    Button {
                        withAnimation(.spring(response: 0.28, dampingFraction: 0.8)) {
                            selectedFilter = category
                        }
                    } label: {
                        Text(category.rawValue)
                            .font(.system(size: 13, weight: isSelected ? .heavy : .semibold))
                            .foregroundColor(isSelected ? .black : .white.opacity(0.9))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 8)
                            .background(
                                Capsule()
                                    .fill(
                                        isSelected
                                            ? (category == .revoked ? Color.red : Color.cyan)
                                            : Color.white.opacity(0.09)
                                    )
                            )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
        }
    }

    // MARK: - Notification Card (OneUI 7 + iOS 18 Style)

    private func notificationCard(for item: NotiItem) -> some View {
        VStack(alignment: .leading, spacing: 9) {
            // Top Row: Avatar/Icon + App Name + Revoked Badge + Star/Cloud/Time
            HStack(spacing: 8) {
                if let avatar = item.uiAvatarImage {
                    Image(uiImage: avatar)
                        .resizable()
                        .scaledToFill()
                        .frame(width: 26, height: 26)
                        .clipShape(RoundedRectangle(cornerRadius: 7))
                } else {
                    Image(systemName: iconForApp(item))
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.white)
                        .frame(width: 26, height: 26)
                        .background(
                            RoundedRectangle(cornerRadius: 7)
                                .fill(item.isRevoked ? Color.red : Color.blue.opacity(0.75))
                        )
                }

                Text(item.appName)
                    .font(.system(size: 12, weight: .bold))
                    .foregroundColor(.cyan)
                    .lineLimit(1)

                if item.isRevoked {
                    Text("🚫 ĐÃ THU HỒI (ĐÃ GIỮ LẠI)")
                        .font(.system(size: 10, weight: .black))
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(Capsule().fill(Color.red))
                }

                Spacer()

                if item.isStarred {
                    Text("★")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.yellow)
                }

                if item.isSynced {
                    Text("☁️")
                        .font(.system(size: 12))
                }

                Text(item.formattedTimeShort)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.gray)
            }

            // Sender / Title
            if !item.title.isEmpty {
                Text(item.title)
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
            }

            // Message Content (respects Privacy Mask blur)
            Text(item.fullDisplayText)
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.88))
                .lineLimit(4)
                .blur(radius: securityService.shouldBlurContent ? 8 : 0)

            // Attached Media Image Preview if available
            if let pic = item.uiPictureImage {
                Image(uiImage: pic)
                    .resizable()
                    .scaledToFill()
                    .frame(height: 145)
                    .frame(maxWidth: .infinity)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .blur(radius: securityService.shouldBlurContent ? 14 : 0)
            }

            // Bottom Smart Action Pills (1-tap OTP Copy, Banking Amount, Extracted Link/Phone)
            let otp = item.extractedOTP
            let bank = item.bankingTransaction
            let entities = item.extractedEntities.filter { $0.type != .otp }

            if otp != nil || bank != nil || !entities.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        if let otpCode = otp {
                            Button {
                                UIPasteboard.general.string = otpCode
                                showToast("🔑 Đã sao chép mã OTP: \(otpCode)")
                            } label: {
                                HStack(spacing: 4) {
                                    Image(systemName: "doc.on.doc.fill")
                                    Text("Copy OTP: \(otpCode)")
                                }
                                .font(.system(size: 12, weight: .heavy))
                                .foregroundColor(.black)
                                .padding(.horizontal, 11)
                                .padding(.vertical, 5)
                                .background(Capsule().fill(Color.green))
                            }
                            .buttonStyle(.plain)
                        }

                        if let tx = bank {
                            HStack(spacing: 4) {
                                Image(systemName: tx.isCredit ? "arrow.down.left.circle.fill" : "arrow.up.right.circle.fill")
                                Text("\(tx.bankName): \(tx.formattedAmount)")
                            }
                            .font(.system(size: 12, weight: .bold))
                            .foregroundColor(tx.isCredit ? .green : .orange)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(
                                Capsule().fill((tx.isCredit ? Color.green : Color.orange).opacity(0.16))
                            )
                        }

                        ForEach(entities.prefix(2)) { entity in
                            Button {
                                UIPasteboard.general.string = entity.value
                                showToast("Đã sao chép \(entity.type.rawValue): \(entity.value)")
                            } label: {
                                HStack(spacing: 4) {
                                    Image(systemName: entity.type.iconName)
                                    Text(entity.value)
                                        .lineLimit(1)
                                }
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.cyan)
                                .frame(maxWidth: 190)
                                .padding(.horizontal, 9)
                                .padding(.vertical, 5)
                                .background(Capsule().fill(Color.cyan.opacity(0.14)))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(
                    item.isRevoked
                        ? Color(red: 0.22, green: 0.07, blue: 0.09)
                        : Color(red: 0.10, green: 0.12, blue: 0.17)
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(
                    item.isRevoked ? Color.red.opacity(0.65) : Color.white.opacity(0.08),
                    lineWidth: item.isRevoked ? 1.5 : 1.0
                )
        )
    }

    // MARK: - Empty State

    private var emptyStateView: some View {
        VStack(spacing: 14) {
            Spacer()
            Image(systemName: selectedFilter == .revoked ? "shield.lefthalf.filled.badge.checkmark" : "bell.and.waves.left.and.right.fill")
                .font(.system(size: 46))
                .foregroundColor(.cyan.opacity(0.7))

            Text("Không có thông báo nào trong mục \"\(selectedFilter.rawValue)\"")
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.white)

            Text("Kéo xuống hoặc bấm nút Đồng bộ Google Drive để tải tin nhắn thu hồi & thông báo mới nhất.")
                .font(.system(size: 13))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 36)

            Button {
                Task {
                    await syncService.pullFromCloud(silent: false)
                }
            } label: {
                Label("Đồng bộ từ Google Drive ngay", systemImage: "icloud.and.arrow.down.fill")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.black)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 10)
                    .background(Capsule().fill(Color.cyan))
            }
            .padding(.top, 6)

            Spacer()
        }
    }

    // MARK: - Biometric Lock Overlay

    private var biometricLockOverlay: some View {
        ZStack {
            Color.black.opacity(0.96).ignoresSafeArea()

            VStack(spacing: 20) {
                Image(systemName: "faceid")
                    .font(.system(size: 56))
                    .foregroundColor(.cyan)

                Text("NotiStar Cloud Đang Khóa Bảo Mật")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white)

                if let err = securityService.authErrorMessage {
                    Text(err)
                        .font(.system(size: 13))
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 24)
                }

                HStack(spacing: 10) {
                    SecureField("Nhập PIN 4 số", text: $pinInput)
                        .keyboardType(.numberPad)
                        .padding(12)
                        .frame(width: 160)
                        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.12)))
                        .foregroundColor(.white)

                    Button("Mở khóa") {
                        if securityService.verifyPin(pinInput) {
                            pinInput = ""
                        }
                    }
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.black)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(RoundedRectangle(cornerRadius: 12).fill(Color.green))
                }

                Button {
                    securityService.authenticateWithBiometrics()
                } label: {
                    Label("Mở bằng FaceID / TouchID", systemImage: "lock.open.fill")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundColor(.cyan)
                        .padding(.top, 8)
                }
            }
            .padding(28)
        }
    }

    private func iconForApp(_ item: NotiItem) -> String {
        if item.bankingTransaction != nil {
            return "banknote.fill"
        }
        if item.isMessageApp {
            return "message.badge.filled.fill"
        }
        if item.extractedOTP != nil {
            return "key.fill"
        }
        return "bell.fill"
    }

    private func showToast(_ text: String) {
        withAnimation {
            toastMessage = text
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.3) {
            withAnimation {
                toastMessage = nil
            }
        }
    }
}
