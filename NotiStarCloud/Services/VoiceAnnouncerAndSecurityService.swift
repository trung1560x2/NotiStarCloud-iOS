import Foundation
import AVFoundation
import LocalAuthentication
import SwiftUI

final class VoiceAnnouncerAndSecurityService: NSObject, ObservableObject {
    static let shared = VoiceAnnouncerAndSecurityService()

    private let synthesizer = AVSpeechSynthesizer()
    private var announcedItemIds: Set<String> = []

    @Published var isVoiceBankEnabled: Bool {
        didSet { UserDefaults.standard.set(isVoiceBankEnabled, forKey: "notistar_voice_bank_enabled") }
    }

    @Published var isVoiceRevokedEnabled: Bool {
        didSet { UserDefaults.standard.set(isVoiceRevokedEnabled, forKey: "notistar_voice_revoked_enabled") }
    }

    @Published var isBiometricLockEnabled: Bool {
        didSet {
            UserDefaults.standard.set(isBiometricLockEnabled, forKey: "notistar_biometric_lock_enabled")
            if !isBiometricLockEnabled {
                isUnlocked = true
            }
        }
    }

    @Published var savedPinCode: String {
        didSet { UserDefaults.standard.set(savedPinCode, forKey: "notistar_pin_code") }
    }

    @Published var isPrivacyMaskActive: Bool {
        didSet { UserDefaults.standard.set(isPrivacyMaskActive, forKey: "notistar_privacy_mask_active") }
    }

    @Published var isAppInBackgroundSwitcher: Bool = false
    @Published var isUnlocked: Bool = true
    @Published var authErrorMessage: String?

    override init() {
        let defaults = UserDefaults.standard
        if defaults.object(forKey: "notistar_voice_bank_enabled") == nil {
            defaults.set(true, forKey: "notistar_voice_bank_enabled")
        }
        if defaults.object(forKey: "notistar_voice_revoked_enabled") == nil {
            defaults.set(true, forKey: "notistar_voice_revoked_enabled")
        }

        let bioLock = defaults.bool(forKey: "notistar_biometric_lock_enabled")
        self.isVoiceBankEnabled = defaults.bool(forKey: "notistar_voice_bank_enabled")
        self.isVoiceRevokedEnabled = defaults.bool(forKey: "notistar_voice_revoked_enabled")
        self.isBiometricLockEnabled = bioLock
        self.savedPinCode = defaults.string(forKey: "notistar_pin_code") ?? "1234"
        self.isPrivacyMaskActive = defaults.bool(forKey: "notistar_privacy_mask_active")
        self.isUnlocked = !bioLock

        super.init()
    }

    var shouldBlurContent: Bool {
        isPrivacyMaskActive || isAppInBackgroundSwitcher || (isBiometricLockEnabled && !isUnlocked)
    }

    // MARK: - Vietnamese Voice Announcer (AVSpeechSynthesizer)

    func announceItemIfNeeded(_ item: NotiItem) {
        let uniqueKey = "\(item.id)_\(item.isRevoked)"
        guard !announcedItemIds.contains(uniqueKey) else { return }
        announcedItemIds.insert(uniqueKey)

        if item.isRevoked && isVoiceRevokedEnabled {
            let sender = item.title.isEmpty ? item.appName : item.title
            let preview = String(item.fullDisplayText.prefix(100))
            speakVietnamese("Cảnh báo thu hồi! \(sender) trên \(item.appName) vừa thu hồi tin nhắn: \(preview)")
            return
        }

        if let tx = item.bankingTransaction, isVoiceBankEnabled {
            let amountInt = Int64(abs(tx.amount))
            if tx.isCredit {
                speakVietnamese("Ting ting! \(tx.bankName) vừa nhận cộng \(amountInt) đồng.")
            } else {
                speakVietnamese("Biến động số dư \(tx.bankName), trừ \(amountInt) đồng.")
            }
        }
    }

    func speakVietnamese(_ text: String) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            do {
                let session = AVAudioSession.sharedInstance()
                try session.setCategory(.playback, mode: .spokenAudio, options: [.duckOthers, .mixWithOthers])
                try session.setActive(true, options: .notifyOthersOnDeactivation)
            } catch {
                // Continue speaking even if audio session adjustment fails
            }

            if self.synthesizer.isSpeaking {
                self.synthesizer.stopSpeaking(at: .immediate)
            }

            let utterance = AVSpeechUtterance(string: text)
            utterance.voice = AVSpeechSynthesisVoice(language: "vi-VN") ?? AVSpeechSynthesisVoice(language: "en-US")
            utterance.rate = AVSpeechUtteranceDefaultSpeechRate
            utterance.pitchMultiplier = 1.05
            utterance.volume = 1.0
            self.synthesizer.speak(utterance)
        }
    }

    func testVoiceAnnouncement() {
        speakVietnamese("Ting ting! NotiStar Cloud đã kích hoạt đọc thông báo chuyển khoản và tin nhắn thu hồi bằng tiếng Việt. Nhận cộng 5,000,000 đồng!")
    }

    // MARK: - FaceID / TouchID & PIN Security

    func authenticateWithBiometrics() {
        let context = LAContext()
        context.localizedFallbackTitle = "Nhập mã PIN"
        var error: NSError?

        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            let reason = "Mở khóa bảo mật NotiStar Cloud (FaceID / TouchID)"
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { [weak self] success, evalError in
                DispatchQueue.main.async {
                    if success {
                        self?.isUnlocked = true
                        self?.authErrorMessage = nil
                    } else {
                        self?.authErrorMessage = evalError?.localizedDescription ?? "Không thể xác thực sinh trắc học. Vui lòng dùng mã PIN."
                    }
                }
            }
        } else {
            DispatchQueue.main.async { [weak self] in
                self?.authErrorMessage = "Thiết bị không hỗ trợ hoặc chưa bật FaceID/TouchID. Vui lòng nhập mã PIN 4 số."
            }
        }
    }

    func verifyPin(_ inputPin: String) -> Bool {
        let trimmed = inputPin.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed == savedPinCode {
            isUnlocked = true
            authErrorMessage = nil
            return true
        } else {
            authErrorMessage = "Mã PIN không chính xác!"
            return false
        }
    }

    func handleScenePhase(_ phase: ScenePhase) {
        switch phase {
        case .active:
            isAppInBackgroundSwitcher = false
            if isBiometricLockEnabled && !isUnlocked {
                authenticateWithBiometrics()
            }
        case .inactive:
            isAppInBackgroundSwitcher = true
        case .background:
            isAppInBackgroundSwitcher = true
            if isBiometricLockEnabled {
                isUnlocked = false
            }
        @unknown default:
            break
        }
    }
}
