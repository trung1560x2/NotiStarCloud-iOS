import SwiftUI
import UIKit

struct MessageHistoryView: View {
    let initialItem: NotiItem
    @ObservedObject var syncService = GoogleCloudSyncService.shared
    @ObservedObject var securityService = VoiceAnnouncerAndSecurityService.shared

    @State private var searchQuery: String = ""
    @State private var currentMatchIndex: Int = 0
    @State private var scopeAllFromApp: Bool = false
    @State private var selectedPreviewImage: UIImage?
    @State private var showImageModal: Bool = false
    @State private var toastText: String?

    private var threadMessages: [NotiItem] {
        let filtered = syncService.notifications.filter { item in
            if scopeAllFromApp {
                return item.packageName == initialItem.packageName || item.appName == initialItem.appName
            } else {
                let sameApp = (item.packageName == initialItem.packageName || item.appName == initialItem.appName)
                let sameSender = item.title.lowercased() == initialItem.title.lowercased()
                return sameApp && (initialItem.title.isEmpty || sameSender)
            }
        }
        // Chronological order (oldest -> newest) like a chat thread
        return filtered.sorted { $0.time < $1.time }
    }

    private var matchingMessageIDs: [String] {
        let q = searchQuery.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !q.isEmpty else { return [] }
        return threadMessages.filter {
            $0.title.lowercased().contains(q) || $0.fullDisplayText.lowercased().contains(q)
        }.map { $0.id }
    }

    var body: some View {
        ZStack {
            Color(red: 0.05, green: 0.06, blue: 0.09)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                headerScopeBar
                inChatSearchBar

                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(threadMessages) { msg in
                                let isMatch = matchingMessageIDs.contains(msg.id)
                                let isFocusedMatch = isMatch &&
                                    !matchingMessageIDs.isEmpty &&
                                    matchingMessageIDs[min(currentMatchIndex, matchingMessageIDs.count - 1)] == msg.id

                                chatBubbleCard(for: msg, isMatch: isMatch, isFocusedMatch: isFocusedMatch)
                                    .id(msg.id)
                            }
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 16)
                    }
                    .onAppear {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.12) {
                            withAnimation(.easeInOut(duration: 0.25)) {
                                proxy.scrollTo(initialItem.id, anchor: .center)
                            }
                        }
                    }
                    .onChange(of: currentMatchIndex) { _ in
                        scrollToFocusedMatch(proxy: proxy)
                    }
                    .onChange(of: searchQuery) { _ in
                        currentMatchIndex = 0
                        scrollToFocusedMatch(proxy: proxy)
                    }
                }
            }

            if let toast = toastText {
                VStack {
                    Spacer()
                    Text(toast)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Capsule().fill(Color.green.opacity(0.92)))
                        .padding(.bottom, 24)
                }
                .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
        .navigationTitle(initialItem.title.isEmpty ? initialItem.appName : initialItem.title)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showImageModal) {
            if let img = selectedPreviewImage {
                FullScreenImagePreviewSheet(image: img)
            }
        }
    }

    // MARK: - Subviews

    private var headerScopeBar: some View {
        HStack(spacing: 10) {
            Label(initialItem.appName, systemImage: "app.badge.fill")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.cyan)

            Spacer()

            Picker("Phạm vi", selection: $scopeAllFromApp) {
                Text("Người gửi này").tag(false)
                Text("Toàn bộ \(initialItem.appName)").tag(true)
            }
            .pickerStyle(.segmented)
            .frame(maxWidth: 220)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color(red: 0.09, green: 0.10, blue: 0.14))
    }

    private var inChatSearchBar: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)

            TextField("Tìm từ khóa trong hội thoại...", text: $searchQuery)
                .font(.system(size: 14))
                .foregroundColor(.white)
                .autocorrectionDisabled()

            if !searchQuery.isEmpty {
                Text(matchingMessageIDs.isEmpty ? "0/0" : "\(currentMatchIndex + 1)/\(matchingMessageIDs.count)")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(matchingMessageIDs.isEmpty ? .red : .yellow)

                Button {
                    guard !matchingMessageIDs.isEmpty else { return }
                    if currentMatchIndex > 0 {
                        currentMatchIndex -= 1
                    } else {
                        currentMatchIndex = matchingMessageIDs.count - 1
                    }
                } label: {
                    Text("▲")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(RoundedRectangle(cornerRadius: 6).fill(Color.white.opacity(0.14)))
                }

                Button {
                    guard !matchingMessageIDs.isEmpty else { return }
                    currentMatchIndex = (currentMatchIndex + 1) % matchingMessageIDs.count
                } label: {
                    Text("▼")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(RoundedRectangle(cornerRadius: 6).fill(Color.white.opacity(0.14)))
                }

                Button {
                    searchQuery = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 9)
        .background(Color(red: 0.11, green: 0.12, blue: 0.17))
        .overlay(
            Rectangle()
                .frame(height: 1)
                .foregroundColor(Color.white.opacity(0.07)),
            alignment: .bottom
        )
    }

    private func chatBubbleCard(for msg: NotiItem, isMatch: Bool, isFocusedMatch: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text(msg.title.isEmpty ? msg.appName : msg.title)
                    .font(.system(size: 13, weight: .bold))
                    .foregroundColor(.cyan)

                if msg.isRevoked {
                    Text("🚫 ĐÃ THU HỒI (ĐÃ GIỮ LẠI)")
                        .font(.system(size: 10, weight: .heavy))
                        .foregroundColor(.white)
                        .padding(.horizontal, 7)
                        .padding(.vertical, 3)
                        .background(Capsule().fill(Color.red))
                }

                Spacer()

                if msg.isSynced {
                    Text("☁️")
                        .font(.system(size: 12))
                }

                Text(msg.dateStr)
                    .font(.system(size: 11))
                    .foregroundColor(.gray)
            }

            Text(msg.fullDisplayText)
                .font(.system(size: 15))
                .foregroundColor(.white)
                .blur(radius: securityService.shouldBlurContent ? 8 : 0)
                .textSelection(.enabled)

            if let pic = msg.uiPictureImage {
                Button {
                    selectedPreviewImage = pic
                    showImageModal = true
                } label: {
                    ZStack(alignment: .bottomTrailing) {
                        Image(uiImage: pic)
                            .resizable()
                            .scaledToFit()
                            .frame(maxHeight: 220)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .blur(radius: securityService.shouldBlurContent ? 14 : 0)

                        Label("Xem ảnh gốc", systemImage: "arrow.up.left.and.arrow.down.right")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Capsule().fill(Color.black.opacity(0.7)))
                            .padding(8)
                    }
                }
                .buttonStyle(.plain)
            }

            // Smart Action Pills (OTP, Banking, Links/Phone, TTS, Copy)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    if let otp = msg.extractedOTP {
                        Button {
                            UIPasteboard.general.string = otp
                            showToast("Đã sao chép OTP: \(otp)")
                        } label: {
                            Label("Copy OTP: \(otp)", systemImage: "key.fill")
                                .font(.system(size: 12, weight: .bold))
                                .foregroundColor(.black)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(Capsule().fill(Color.green))
                        }
                    }

                    if let bank = msg.bankingTransaction {
                        Text("\(bank.bankName): \(bank.formattedAmount)")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundColor(bank.isCredit ? .green : .orange)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(
                                Capsule().fill((bank.isCredit ? Color.green : Color.orange).opacity(0.16))
                            )
                    }

                    Button {
                        UIPasteboard.general.string = msg.fullDisplayText
                        showToast("Đã sao chép nội dung tin nhắn")
                    } label: {
                        Label("Sao chép", systemImage: "doc.on.doc")
                            .font(.system(size: 11, weight: .medium))
                            .foregroundColor(.white.opacity(0.85))
                            .padding(.horizontal, 9)
                            .padding(.vertical, 5)
                            .background(Capsule().fill(Color.white.opacity(0.1)))
                    }

                    Button {
                        securityService.speakVietnamese("\(msg.title). \(msg.fullDisplayText)")
                    } label: {
                        Label("Đọc", systemImage: "speaker.wave.2.fill")
                            .font(.system(size: 11, weight: .medium))
                            .foregroundColor(.cyan)
                            .padding(.horizontal, 9)
                            .padding(.vertical, 5)
                            .background(Capsule().fill(Color.cyan.opacity(0.14)))
                    }
                }
            }
        }
        .padding(13)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(
                    msg.isRevoked
                        ? Color.red.opacity(0.14)
                        : (msg.id == initialItem.id ? Color.blue.opacity(0.18) : Color(red: 0.11, green: 0.13, blue: 0.18))
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(
                    isFocusedMatch
                        ? Color.yellow
                        : (isMatch ? Color.orange.opacity(0.7) : (msg.isRevoked ? Color.red.opacity(0.55) : Color.white.opacity(0.08))),
                    lineWidth: isFocusedMatch ? 2.5 : 1.0
                )
        )
    }

    private func scrollToFocusedMatch(proxy: ScrollViewProxy) {
        guard !matchingMessageIDs.isEmpty else { return }
        let safeIdx = min(max(0, currentMatchIndex), matchingMessageIDs.count - 1)
        let targetId = matchingMessageIDs[safeIdx]
        withAnimation(.easeInOut(duration: 0.25)) {
            proxy.scrollTo(targetId, anchor: .center)
        }
    }

    private func showToast(_ text: String) {
        withAnimation {
            toastText = text
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            withAnimation {
                toastText = nil
            }
        }
    }
}

struct FullScreenImagePreviewSheet: View {
    let image: UIImage
    @Environment(\.dismiss) private var dismiss
    @State private var scale: CGFloat = 1.0
    @State private var copiedFeedback: Bool = false

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .scaleEffect(scale)
                    .gesture(
                        MagnificationGesture()
                            .onChanged { val in
                                scale = max(1.0, min(val, 4.0))
                            }
                    )
                    .onTapGesture(count: 2) {
                        withAnimation {
                            scale = scale > 1.0 ? 1.0 : 2.2
                        }
                    }
            }
            .navigationTitle("Xem Ảnh Đã Giữ Lại")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Đóng") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        UIPasteboard.general.image = image
                        copiedFeedback = true
                    } label: {
                        Label(copiedFeedback ? "Đã chép ảnh!" : "Chép ảnh", systemImage: "doc.on.doc.fill")
                            .foregroundColor(.green)
                    }
                }
            }
        }
    }
}
