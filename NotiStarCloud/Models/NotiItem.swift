import Foundation
import SwiftUI
import UIKit

enum CloudConstants {
    static let DEFAULT_DRIVE_FOLDER_ID = "1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU"
    static let DEFAULT_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec"
    static let APP_GROUP_SUITE = "group.com.notistar.cloud.ios"
    static let STORAGE_KEY_NOTIFICATIONS = "notistar_saved_notifications_v1"
}

enum NotiFilterCategory: String, CaseIterable, Identifiable {
    case all = "Tất cả"
    case messages = "Tin nhắn"
    case revoked = "🚫 Đã thu hồi"
    case starred = "★ Đánh dấu"
    case mediaVault = "🖼️ Kho Ảnh"
    case banking = "🏦 Ngân hàng"
    case linksAndPhones = "🔗 Kho Link/SĐT"

    var id: String { rawValue }
}

struct BankingTransaction: Identifiable, Hashable, Codable {
    var id: String
    var bankName: String
    var isCredit: Bool
    var amount: Double
    var balanceAfter: String?
    var note: String
    var timestamp: Int64
    var dateStr: String
    var isRevoked: Bool

    var formattedAmount: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        formatter.maximumFractionDigits = 0
        let numStr = formatter.string(from: NSNumber(value: abs(amount))) ?? "\(Int64(abs(amount)))"
        return (isCredit ? "+" : "-") + numStr + " đ"
    }
}

struct ExtractedEntity: Identifiable, Hashable, Codable {
    enum EntityType: String, Codable, CaseIterable {
        case link = "LINK"
        case phone = "SĐT"
        case email = "EMAIL"
        case otp = "OTP"

        var iconName: String {
            switch self {
            case .link: return "link.circle.fill"
            case .phone: return "phone.circle.fill"
            case .email: return "envelope.circle.fill"
            case .otp: return "key.fill"
            }
        }
    }

    var id: String
    var type: EntityType
    var value: String
    var sourceApp: String
    var sourceTitle: String
    var timestamp: Int64
    var dateStr: String
    var isRevoked: Bool
}

struct NotiItem: Identifiable, Codable, Hashable, Equatable {
    var id: String
    var key: String
    var notificationId: Int
    var packageName: String
    var appName: String
    var title: String
    var contentText: String
    var bigText: String
    var inboxLines: [String]
    var time: Int64
    var dateStr: String
    var isOngoing: Bool
    var hasRemoteInput: Bool
    var color: Int
    var isStarred: Bool
    var isSynced: Bool
    var isRevoked: Bool
    var cloudId: String
    var smallIconB64: String
    var largeIconB64: String
    var pictureB64: String

    init(
        id: String = UUID().uuidString,
        key: String = "",
        notificationId: Int = Int.random(in: 1000...999999),
        packageName: String = "com.apple.mobileSMS",
        appName: String = "Tin nhắn",
        title: String = "",
        contentText: String = "",
        bigText: String = "",
        inboxLines: [String] = [],
        time: Int64 = Int64(Date().timeIntervalSince1970 * 1000),
        dateStr: String = "",
        isOngoing: Bool = false,
        hasRemoteInput: Bool = false,
        color: Int = -16744193,
        isStarred: Bool = false,
        isSynced: Bool = false,
        isRevoked: Bool = false,
        cloudId: String = "",
        smallIconB64: String = "",
        largeIconB64: String = "",
        pictureB64: String = ""
    ) {
        self.id = id
        self.key = key.isEmpty ? "\(packageName)|\(notificationId)|\(time)" : key
        self.notificationId = notificationId
        self.packageName = packageName
        self.appName = appName
        self.title = title
        self.contentText = contentText
        self.bigText = bigText.isEmpty ? contentText : bigText
        self.inboxLines = inboxLines
        self.time = time
        if dateStr.isEmpty {
            let formatter = DateFormatter()
            formatter.dateFormat = "dd/MM/yyyy HH:mm:ss"
            self.dateStr = formatter.string(from: Date(timeIntervalSince1970: TimeInterval(time) / 1000.0))
        } else {
            self.dateStr = dateStr
        }
        self.isOngoing = isOngoing
        self.hasRemoteInput = hasRemoteInput
        self.color = color
        self.isStarred = isStarred
        self.isSynced = isSynced
        self.isRevoked = isRevoked
        self.cloudId = cloudId
        self.smallIconB64 = smallIconB64
        self.largeIconB64 = largeIconB64
        self.pictureB64 = pictureB64
    }

    enum CodingKeys: String, CodingKey {
        case id
        case key
        case notificationId
        case packageName
        case appName
        case title
        case contentText
        case bigText
        case inboxLines
        case time
        case dateStr
        case isOngoing
        case hasRemoteInput
        case color
        case isStarred
        case isSynced
        case isRevoked
        case cloudId
        case smallIconB64
        case largeIconB64
        case pictureB64
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        if let strId = try? container.decode(String.self, forKey: .id), !strId.isEmpty {
            self.id = strId
        } else if let intId = try? container.decode(Int64.self, forKey: .id) {
            self.id = String(intId)
        } else {
            self.id = UUID().uuidString
        }

        self.packageName = (try? container.decode(String.self, forKey: .packageName)) ?? "unknown.package"
        self.appName = (try? container.decode(String.self, forKey: .appName)) ?? "Ứng dụng"
        self.title = (try? container.decode(String.self, forKey: .title)) ?? ""
        self.contentText = (try? container.decode(String.self, forKey: .contentText)) ?? ""
        let decodedBig = (try? container.decode(String.self, forKey: .bigText)) ?? ""
        self.bigText = decodedBig.isEmpty ? self.contentText : decodedBig

        if let lines = try? container.decode([String].self, forKey: .inboxLines) {
            self.inboxLines = lines
        } else if let singleLine = try? container.decode(String.self, forKey: .inboxLines), !singleLine.isEmpty {
            self.inboxLines = singleLine.components(separatedBy: "\n")
        } else {
            self.inboxLines = []
        }

        if let intNotiId = try? container.decode(Int.self, forKey: .notificationId) {
            self.notificationId = intNotiId
        } else if let strNotiId = try? container.decode(String.self, forKey: .notificationId), let parsed = Int(strNotiId) {
            self.notificationId = parsed
        } else {
            self.notificationId = 0
        }

        if let intTime = try? container.decode(Int64.self, forKey: .time) {
            self.time = intTime
        } else if let dblTime = try? container.decode(Double.self, forKey: .time) {
            self.time = Int64(dblTime)
        } else if let strTime = try? container.decode(String.self, forKey: .time), let parsed = Int64(strTime) {
            self.time = parsed
        } else {
            self.time = Int64(Date().timeIntervalSince1970 * 1000)
        }

        let decodedKey = (try? container.decode(String.self, forKey: .key)) ?? ""
        self.key = decodedKey.isEmpty ? "\(self.packageName)|\(self.notificationId)|\(self.time)" : decodedKey

        let decodedDate = (try? container.decode(String.self, forKey: .dateStr)) ?? ""
        if decodedDate.isEmpty {
            let formatter = DateFormatter()
            formatter.dateFormat = "dd/MM/yyyy HH:mm:ss"
            self.dateStr = formatter.string(from: Date(timeIntervalSince1970: TimeInterval(self.time) / 1000.0))
        } else {
            self.dateStr = decodedDate
        }

        self.isOngoing = Self.decodeFlexBool(from: container, key: .isOngoing)
        self.hasRemoteInput = Self.decodeFlexBool(from: container, key: .hasRemoteInput)
        self.isStarred = Self.decodeFlexBool(from: container, key: .isStarred)
        self.isSynced = Self.decodeFlexBool(from: container, key: .isSynced)
        self.isRevoked = Self.decodeFlexBool(from: container, key: .isRevoked)

        if let intColor = try? container.decode(Int.self, forKey: .color) {
            self.color = intColor
        } else if let strColor = try? container.decode(String.self, forKey: .color), let parsed = Int(strColor) {
            self.color = parsed
        } else {
            self.color = -16744193
        }

        self.cloudId = (try? container.decode(String.self, forKey: .cloudId)) ?? ""
        self.smallIconB64 = (try? container.decode(String.self, forKey: .smallIconB64)) ?? ""
        self.largeIconB64 = (try? container.decode(String.self, forKey: .largeIconB64)) ?? ""
        self.pictureB64 = (try? container.decode(String.self, forKey: .pictureB64)) ?? ""
    }

    private static func decodeFlexBool(from container: KeyedDecodingContainer<CodingKeys>, key: CodingKeys) -> Bool {
        if let b = try? container.decode(Bool.self, forKey: key) {
            return b
        }
        if let i = try? container.decode(Int.self, forKey: key) {
            return i != 0
        }
        if let s = try? container.decode(String.self, forKey: key) {
            let lower = s.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
            return lower == "true" || lower == "1" || lower == "yes"
        }
        return false
    }

    // MARK: - Display & Search Helpers

    var fullDisplayText: String {
        if !bigText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return bigText
        }
        if !inboxLines.isEmpty {
            return inboxLines.joined(separator: "\n")
        }
        return contentText
    }

    var searchableText: String {
        "\(appName) \(packageName) \(title) \(contentText) \(bigText) \(inboxLines.joined(separator: " ")) \(dateStr)"
    }

    var formattedTimeShort: String {
        let date = Date(timeIntervalSince1970: TimeInterval(time) / 1000.0)
        let formatter = DateFormatter()
        if Calendar.current.isDateInToday(date) {
            formatter.dateFormat = "HH:mm:ss"
        } else {
            formatter.dateFormat = "HH:mm · dd/MM"
        }
        return formatter.string(from: date)
    }

    var isMessageApp: Bool {
        let lowerPkg = packageName.lowercased()
        let lowerApp = appName.lowercased()
        let msgKeywords = [
            "zalo", "orca", "messenger", "whatsapp", "telegram", "viber",
            "mms", "sms", "messages", "mobilesms", "instagram", "tiktok",
            "line", "wechat", "discord", "slack", "threads", "skype", "signal"
        ]
        return msgKeywords.contains { lowerPkg.contains($0) || lowerApp.contains($0) } || hasRemoteInput
    }

    var hasMediaImage: Bool {
        !pictureB64.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var uiPictureImage: UIImage? {
        Self.decodeBase64Image(pictureB64)
    }

    var uiAvatarImage: UIImage? {
        if let large = Self.decodeBase64Image(largeIconB64) {
            return large
        }
        return Self.decodeBase64Image(smallIconB64)
    }

    static func decodeBase64Image(_ b64: String) -> UIImage? {
        let trimmed = b64.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        let cleanB64: String
        if let commaIndex = trimmed.firstIndex(of: ","), trimmed.hasPrefix("data:image") {
            cleanB64 = String(trimmed[trimmed.index(after: commaIndex)...])
        } else {
            cleanB64 = trimmed
        }
        guard let data = Data(base64Encoded: cleanB64, options: .ignoreUnknownCharacters) else {
            return nil
        }
        return UIImage(data: data)
    }

    // MARK: - Smart OTP Extractor

    var extractedOTP: String? {
        let combined = "\(title) \(fullDisplayText)"
        let lower = combined.lowercased()

        let otpKeywords = [
            "otp", "mã xác thực", "ma xac thuc", "mã xác nhận", "ma xac nhan",
            "verification", "verify", "code", "passcode", "mã bảo mật",
            "ma bao mat", "mã đăng nhập", "mã giao dịch", "smart otp",
            "mã kích hoạt", "authentication", "security code", "pin"
        ]
        let hasKeyword = otpKeywords.contains { lower.contains($0) }
        guard hasKeyword else { return nil }

        // Avoid mistaking banking currency amounts right before VND/d
        let pattern = #"(?<![0-9.,])\b([0-9]{4,8})\b(?![0-9.,]|\s*(?:vnd|đ|d|vnđ))"#
        guard let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]) else {
            return nil
        }
        let nsRange = NSRange(combined.startIndex..<combined.endIndex, in: combined)
        let matches = regex.matches(in: combined, options: [], range: nsRange)

        for match in matches {
            if match.numberOfRanges > 1, let r = Range(match.range(at: 1), in: combined) {
                let candidate = String(combined[r])
                // Exclude typical 4-digit current years (e.g. 2024..2030) if there are other numbers or date context
                if candidate.count == 4, let yr = Int(candidate), (2020...2035).contains(yr) {
                    continue
                }
                return candidate
            }
        }
        return nil
    }

    // MARK: - Smart Banking Balance Parser

    var bankingTransaction: BankingTransaction? {
        let combined = "\(appName) \(title) \(fullDisplayText)"
        let lower = combined.lowercased()

        let bankMap: [(keywords: [String], displayName: String)] = [
            (["vietcombank", "vcb", "vcb digibank"], "Vietcombank"),
            (["mb bank", "mbbank", "mb ", "quân đội"], "MB Bank"),
            (["techcombank", "tcb", "techcom"], "Techcombank"),
            (["acb", "á châu"], "ACB"),
            (["bidv", "smartbanking"], "BIDV"),
            (["vietinbank", "vietin", "ipay"], "VietinBank"),
            (["cake", "cake by vpbank"], "Cake"),
            (["timo"], "Timo"),
            (["momo"], "MoMo"),
            (["zalopay", "zalo pay"], "ZaloPay"),
            (["vpbank", "vp bank"], "VPBank"),
            (["tpbank", "tp bank", "tienphong"], "TPBank"),
            (["sacombank", "sacom"], "Sacombank"),
            (["agribank"], "Agribank"),
            (["vibr", "vib "], "VIB"),
            (["shinhan"], "Shinhan Bank")
        ]

        var detectedBank: String?
        for entry in bankMap {
            if entry.keywords.contains(where: { lower.contains($0) }) {
                detectedBank = entry.displayName
                break
            }
        }

        // Also match generic balance change keywords ("số dư", "sd:", "biến động", "gd:", "tk ")
        let hasBalanceCue = lower.contains("số dư") || lower.contains("so du") || lower.contains("biến động") || lower.contains("tk ") || lower.contains("vnd") || lower.contains("vnđ")
        guard detectedBank != nil || hasBalanceCue else { return nil }

        // Regex matching +1,500,000 VND / -250.000đ / + 50,000 VND
        let amountPattern = #"([+\-])\s*([0-9]{1,3}(?:[.,][0-9]{3})+|[0-9]{4,12})\s*(?:vnd|vnđ|đ|d\b)"#
        guard let regex = try? NSRegularExpression(pattern: amountPattern, options: [.caseInsensitive]) else {
            return nil
        }

        let nsRange = NSRange(combined.startIndex..<combined.endIndex, in: combined)
        guard let match = regex.firstMatch(in: combined, options: [], range: nsRange),
              match.numberOfRanges >= 3,
              let signRange = Range(match.range(at: 1), in: combined),
              let digitsRange = Range(match.range(at: 2), in: combined) else {
            return nil
        }

        let signStr = String(combined[signRange])
        let rawDigits = String(combined[digitsRange])
            .replacingOccurrences(of: ",", with: "")
            .replacingOccurrences(of: ".", with: "")

        guard let amountVal = Double(rawDigits), amountVal > 0 else { return nil }

        // Optional ending balance extraction
        var balanceAfterStr: String?
        let balPattern = #"(?:số dư|so du|sd|còn lại|con lai)[:\s]*([0-9]{1,3}(?:[.,][0-9]{3})+|[0-9]{4,12})\s*(?:vnd|vnđ|đ|d\b)?"#
        if let balRegex = try? NSRegularExpression(pattern: balPattern, options: [.caseInsensitive]),
           let balMatch = balRegex.firstMatch(in: combined, options: [], range: nsRange),
           balMatch.numberOfRanges >= 2,
           let r = Range(balMatch.range(at: 1), in: combined) {
            balanceAfterStr = String(combined[r]) + " đ"
        }

        return BankingTransaction(
            id: id,
            bankName: detectedBank ?? (appName.isEmpty ? "Ngân hàng" : appName),
            isCredit: signStr == "+",
            amount: amountVal,
            balanceAfter: balanceAfterStr,
            note: fullDisplayText,
            timestamp: time,
            dateStr: dateStr,
            isRevoked: isRevoked
        )
    }

    // MARK: - Smart Link, Vietnamese Phone & Email Extractor

    var extractedEntities: [ExtractedEntity] {
        var results: [ExtractedEntity] = []
        let combined = "\(title)\n\(fullDisplayText)"
        let nsRange = NSRange(combined.startIndex..<combined.endIndex, in: combined)

        // 1. Links (https:// or http://)
        let linkPattern = #"https?://[^\s<>\"\'\)\]]+"#
        if let linkRegex = try? NSRegularExpression(pattern: linkPattern, options: [.caseInsensitive]) {
            for match in linkRegex.matches(in: combined, options: [], range: nsRange) {
                if let r = Range(match.range, in: combined) {
                    let val = String(combined[r]).trimmingCharacters(in: CharacterSet(charactersIn: ".,;!?"))
                    results.append(ExtractedEntity(
                        id: "\(id)_link_\(val)",
                        type: .link,
                        value: val,
                        sourceApp: appName,
                        sourceTitle: title,
                        timestamp: time,
                        dateStr: dateStr,
                        isRevoked: isRevoked
                    ))
                }
            }
        }

        // 2. Vietnamese Phone Numbers (09x, 03x, 07x, 08x, 05x, +84...)
        let phonePattern = #"(?<!\d)(?:\+84|84|0)(?:3[2-9]|5[25689]|7[06-9]|8[1-9]|9[0-9])[0-9]{7}(?!\d)"#
        if let phoneRegex = try? NSRegularExpression(pattern: phonePattern, options: []) {
            for match in phoneRegex.matches(in: combined, options: [], range: nsRange) {
                if let r = Range(match.range, in: combined) {
                    let val = String(combined[r])
                    results.append(ExtractedEntity(
                        id: "\(id)_phone_\(val)",
                        type: .phone,
                        value: val,
                        sourceApp: appName,
                        sourceTitle: title,
                        timestamp: time,
                        dateStr: dateStr,
                        isRevoked: isRevoked
                    ))
                }
            }
        }

        // 3. Emails
        let emailPattern = #"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,64}"#
        if let emailRegex = try? NSRegularExpression(pattern: emailPattern, options: []) {
            for match in emailRegex.matches(in: combined, options: [], range: nsRange) {
                if let r = Range(match.range, in: combined) {
                    let val = String(combined[r])
                    results.append(ExtractedEntity(
                        id: "\(id)_email_\(val)",
                        type: .email,
                        value: val,
                        sourceApp: appName,
                        sourceTitle: title,
                        timestamp: time,
                        dateStr: dateStr,
                        isRevoked: isRevoked
                    ))
                }
            }
        }

        // 4. OTP if present
        if let otp = extractedOTP {
            results.append(ExtractedEntity(
                id: "\(id)_otp_\(otp)",
                type: .otp,
                value: otp,
                sourceApp: appName,
                sourceTitle: title,
                timestamp: time,
                dateStr: dateStr,
                isRevoked: isRevoked
            ))
        }

        return results
    }
}
