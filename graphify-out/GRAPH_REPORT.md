# Graph Report - NotiStarCloud_iOS  (2026-11-02)

## Corpus Check
- 30 files · ~22,435 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 641 nodes · 1465 edges · 33 communities (28 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 31
- Community 32

## God Nodes (most connected - your core abstractions)
1. `NotiItem` - 52 edges
2. `GoogleCloudSyncService` - 42 edges
3. `showToast()` - 40 edges
4. `showToast()` - 40 edges
5. `renderApp()` - 34 edges
6. `renderApp()` - 34 edges
7. `CodingKeys` - 25 edges
8. `VoiceAnnouncerAndSecurityService` - 22 edges
9. `initNotiStarIosApp()` - 21 edges
10. `initNotiStarIosApp()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `.totalCredit` --references--> `BankingTransaction`  [INFERRED]
  NotiStarCloud/Views/CloudSyncAndToolsView.swift → NotiStarCloud/Models/NotiItem.swift
- `.totalDebit` --references--> `BankingTransaction`  [INFERRED]
  NotiStarCloud/Views/CloudSyncAndToolsView.swift → NotiStarCloud/Models/NotiItem.swift
- `.transactions` --references--> `GoogleCloudSyncService`  [INFERRED]
  NotiStarCloud/Views/CloudSyncAndToolsView.swift → NotiStarCloud/Services/GoogleCloudSyncService.swift
- `.body` --calls--> `NotiItem`  [INFERRED]
  NotiStarCloud/Views/CloudSyncAndToolsView.swift → NotiStarCloud/Models/NotiItem.swift
- `.matchingMessageIDs` --references--> `NotiItem`  [INFERRED]
  NotiStarCloud/Views/MessageHistoryView.swift → NotiStarCloud/Models/NotiItem.swift

## Import Cycles
- None detected.

## Communities (33 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (22): AVFoundation, Foundation, LocalAuthentication, BankingLedgerSheetView, .body, .totalCredit, .totalDebit, .transactions (+14 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (37): allNotifications, announcedIds, appendMoreNotificationsToDom(), applyUnsharpMaskOnCanvas(), backspacePin(), blobUrlCache, blobUrlToDataUrlMap, calendarViewMonth (+29 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (37): allNotifications, announcedIds, appendMoreNotificationsToDom(), applyUnsharpMaskOnCanvas(), backspacePin(), blobUrlCache, blobUrlToDataUrlMap, calendarViewMonth (+29 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (32): CODE_SIGN_IDENTITY, CODE_SIGNING_ALLOWED, CODE_SIGNING_REQUIRED, CURRENT_PROJECT_VERSION, ENABLE_PREVIEWS, GENERATE_INFOPLIST_FILE, INFOPLIST_FILE, IPHONEOS_DEPLOYMENT_TARGET (+24 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (21): BankingTransaction, .formattedAmount, CloudConstants, EntityType, email, .iconName, link, otp (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (9): build_mobileconfig(), make_icon_png(), plist_recv(), plist_send(), push_profile_over_usb(), usbmux_connect(), usbmux_reply(), usbmux_request() (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (8): GoogleCloudSyncService, .autoSyncEnabled, .customWebhookUrl, .driveFolderId, .localFileURL, .webAppUrl, .allEntities, .filteredNotifications

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (22): CodingKeys, appName, bigText, cloudId, color, contentText, dateStr, hasRemoteInput (+14 more)

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (23): computeNotificationUid(), formatDateOnly(), generateCrispAppleTouchIcon(), generateTinyDemoPhotoB64(), getTodayDateStr(), getYesterdayDateStr(), handleQuickIosPhotoUpload(), handleUrlQueryActions() (+15 more)

### Community 9 - "Community 9"
Cohesion: 0.16
Nodes (23): computeNotificationUid(), formatDateOnly(), generateCrispAppleTouchIcon(), generateTinyDemoPhotoB64(), getTodayDateStr(), getYesterdayDateStr(), handleQuickIosPhotoUpload(), handleUrlQueryActions() (+15 more)

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (22): checkOtaUpdate(), cleanSpamAppsNow(), clearLocalDatabase(), clearSearch(), deleteNotificationByUid(), deleteNotificationsByApp(), getBlockedAppsSet(), onSearchChange() (+14 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (22): checkOtaUpdate(), cleanSpamAppsNow(), clearLocalDatabase(), clearSearch(), deleteNotificationByUid(), deleteNotificationsByApp(), getBlockedAppsSet(), onSearchChange() (+14 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (20): name, runs-on, steps, jobs, build-unsigned-ipa, name, on, pull_request (+12 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (9): NotiItem, .extractedOTP, .formattedTimeShort, .fullDisplayText, .hasMediaImage, .isMessageApp, .searchableText, .uiAvatarImage (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.14
Nodes (20): announceNotificationIfImportant(), computeBankingSummary(), copyAppsScriptV2Code(), copyNotificationByUid(), copyTextToClipboard(), exportBackupCsv(), extractBankTransaction(), extractLinksPhonesEmails() (+12 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (20): announceNotificationIfImportant(), computeBankingSummary(), copyAppsScriptV2Code(), copyNotificationByUid(), copyTextToClipboard(), exportBackupCsv(), extractBankTransaction(), extractLinksPhonesEmails() (+12 more)

### Community 16 - "Community 16"
Cohesion: 0.15
Nodes (19): applyQuickDateInput(), closeModal(), closeModalOnBackdrop(), copyShortcutWebhookTemplate(), getDriveFolderId(), getWebAppUrl(), importBackupJsonFile(), isChatNotification() (+11 more)

### Community 17 - "Community 17"
Cohesion: 0.15
Nodes (19): applyQuickDateInput(), closeModal(), closeModalOnBackdrop(), copyShortcutWebhookTemplate(), getDriveFolderId(), getWebAppUrl(), importBackupJsonFile(), isChatNotification() (+11 more)

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (3): .body, .emptyStateView, .searchAndClipboardBar

### Community 19 - "Community 19"
Cohesion: 0.14
Nodes (8): VoiceAnnouncerAndSecurityService, .isBiometricLockEnabled, .isPrivacyMaskActive, .isVoiceBankEnabled, .isVoiceRevokedEnabled, .savedPinCode, .shouldBlurContent, .biometricLockOverlay

### Community 20 - "Community 20"
Cohesion: 0.24
Nodes (16): escapeAttr(), escapeHtml(), formatB64Src(), formatShortSmartTime(), formatVnd(), getAppBrandStyle(), getItemMediaB64(), getVipKeywords() (+8 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (15): background_color, categories, description, dir, display, display_override, icons, lang (+7 more)

### Community 22 - "Community 22"
Cohesion: 0.24
Nodes (16): escapeAttr(), escapeHtml(), formatB64Src(), formatShortSmartTime(), formatVnd(), getAppBrandStyle(), getItemMediaB64(), getVipKeywords() (+8 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (15): background_color, categories, description, dir, display, display_override, icons, lang (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.20
Nodes (6): AppIntents, CaptureNotificationIntent, .parameterSummary, NotiStarShortcutsProvider, .appShortcuts, SyncCloudShortcutIntent

### Community 25 - "Community 25"
Cohesion: 0.30
Nodes (4): ContentView, .body, .filterChipsScrollBar, .topHeaderDashboard

### Community 26 - "Community 26"
Cohesion: 0.29
Nodes (10): exportAllDailyBackupsSeparate(), exportBackupJson(), exportDailyBackupJson(), getDeviceName(), getGroupedDailyNotificationsMap(), pushAllToCloud(), pushDailyFileToCloud(), pushItemsToCloud() (+2 more)

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (10): exportAllDailyBackupsSeparate(), exportBackupJson(), exportDailyBackupJson(), getDeviceName(), getGroupedDailyNotificationsMap(), pushAllToCloud(), pushDailyFileToCloud(), pushItemsToCloud() (+2 more)

## Knowledge Gaps
- **61 isolated node(s):** `AppIntents`, `.parameterSummary`, `all`, `messages`, `revoked` (+56 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 200 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `NotiItem` connect `Community 13` to `Community 0`, `Community 4`, `Community 6`, `Community 7`, `Community 18`, `Community 25`, `Community 28`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `NotiItem` (e.g. with `.perform()` and `.handleIncomingURL()`) actually correct?**
  _`NotiItem` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AppIntents`, `.parameterSummary`, `all` to the rest of the system?**
  _61 weakly-connected nodes found - possible missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07030527289546716 - nodes in this community are weakly interconnected._
- **Why does `CodingKeys` connect `Community 7` to `Community 13`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `GoogleCloudSyncService` (e.g. with `.transactions` and `.allEntities`) actually correct?**
  _`GoogleCloudSyncService` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07948717948717948 - nodes in this community are weakly interconnected._