import os
import re

path = r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace the entire <style>...</style> block with an authentic iOS 18 + OneUI 7 Luxe Design System
new_style = """  <style>
    :root {
      --bg-root: #000000;
      --bg-surface: #111114;
      --bg-grouped: #1C1C1E;
      --bg-card: rgba(28, 28, 32, 0.78);
      --bg-card-hover: rgba(40, 40, 46, 0.88);
      --bg-glass: rgba(14, 14, 18, 0.76);
      --border-subtle: rgba(255, 255, 255, 0.09);
      --border-hairline: rgba(255, 255, 255, 0.07);
      --border-highlight: rgba(10, 132, 255, 0.45);
      --text-primary: #FFFFFF;
      --text-secondary: rgba(235, 235, 245, 0.62);
      --text-muted: rgba(235, 235, 245, 0.38);
      --accent-blue: #0A84FF;
      --accent-blue-light: #409CFF;
      --accent-purple: #5E5CE6;
      --accent-green: #30D158;
      --accent-red: #FF453A;
      --accent-amber: #FF9F0A;
      --safe-top: env(safe-area-inset-top, 20px);
      --safe-bottom: env(safe-area-inset-bottom, 20px);
      --safe-left: env(safe-area-inset-left, 0px);
      --safe-right: env(safe-area-inset-right, 0px);
      --radius-xl: 24px;
      --radius-lg: 20px;
      --radius-md: 14px;
      --radius-pill: 999px;
    }

    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    html, body {
      margin: 0;
      padding: 0;
      background-color: var(--bg-root);
      background-image: radial-gradient(ellipse 110% 320px at 50% -60px, rgba(10, 132, 255, 0.22), rgba(94, 92, 230, 0.09) 55%, transparent 100%);
      background-attachment: fixed;
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      overscroll-behavior-y: none;
      min-height: 100vh;
      min-height: 100dvh;
      user-select: none;
      letter-spacing: -0.15px;
    }

    .selectable {
      user-select: text;
      -webkit-user-select: text;
    }

    .app-shell {
      max-width: 680px;
      margin: 0 auto;
      padding-top: calc(var(--safe-top) + 4px);
      padding-bottom: calc(var(--safe-bottom) + 104px);
      padding-left: calc(var(--safe-left) + 16px);
      padding-right: calc(var(--safe-right) + 16px);
    }

    /* Sticky iOS 18 Translucent Navigation Header */
    .top-header {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-glass);
      backdrop-filter: blur(32px) saturate(200%);
      -webkit-backdrop-filter: blur(32px) saturate(200%);
      margin: 0 -16px 14px -16px;
      padding: 10px 16px 12px 16px;
      border-bottom: 0.5px solid var(--border-subtle);
    }

    .brand-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
    }

    .brand-left {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .app-squircle-logo {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: linear-gradient(145deg, #0A84FF 0%, #5E5CE6 55%, #BF5AF2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 6px 20px rgba(10, 132, 255, 0.36), inset 0 1px 0 rgba(255, 255, 255, 0.35);
      position: relative;
      flex-shrink: 0;
      cursor: pointer;
    }

    .app-squircle-logo svg {
      width: 22px;
      height: 22px;
      fill: #FFFFFF;
    }

    .live-dot {
      position: absolute;
      bottom: -2px;
      right: -2px;
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: var(--accent-green);
      border: 2px solid #000000;
    }

    .brand-titles {
      min-width: 0;
    }

    .brand-titles h1 {
      font-size: 22px;
      font-weight: 700;
      margin: 0;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 7px;
      color: #FFFFFF;
    }

    .ios-badge {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: var(--radius-pill);
      background: rgba(10, 132, 255, 0.18);
      border: 0.5px solid rgba(10, 132, 255, 0.45);
      color: #64D2FF;
      letter-spacing: 0.2px;
    }

    .sync-status-line {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 1px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 220px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 7px;
    }

    .icon-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      background: rgba(255, 255, 255, 0.08);
      color: #FFFFFF;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      cursor: pointer;
      transition: transform 0.15s cubic-bezier(0.2, 0.8, 0.2, 1), background 0.15s ease;
    }

    .icon-btn svg {
      width: 18px;
      height: 18px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .icon-btn:active {
      transform: scale(0.88);
      background: rgba(255, 255, 255, 0.18);
    }

    .icon-btn.active {
      background: rgba(10, 132, 255, 0.28);
      border-color: rgba(10, 132, 255, 0.6);
      color: #64D2FF;
    }

    .icon-btn.spinning svg,
    .icon-btn.spinning span {
      animation: spin 0.85s linear infinite;
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    /* iOS 18 Frosted Search Field */
    .search-row {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 11px;
    }

    .search-input-wrap {
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
    }

    .search-input-wrap .search-icon {
      position: absolute;
      left: 12px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      pointer-events: none;
    }

    .search-input-wrap .search-icon svg {
      width: 16px;
      height: 16px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2.2;
    }

    .search-input {
      width: 100%;
      padding: 9px 34px 9px 36px;
      border-radius: 12px;
      border: 0.5px solid rgba(255, 255, 255, 0.08);
      background: rgba(118, 118, 128, 0.24);
      color: #FFFFFF;
      font-size: 15px;
      outline: none;
      transition: background 0.2s, border-color 0.2s;
    }

    .search-input::placeholder {
      color: rgba(235, 235, 245, 0.42);
    }

    .search-input:focus {
      background: rgba(118, 118, 128, 0.34);
      border-color: rgba(10, 132, 255, 0.55);
    }

    .clear-search-btn {
      position: absolute;
      right: 8px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: rgba(235, 235, 245, 0.3);
      border: none;
      color: #000;
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 0;
    }

    /* Filter Capsule Pills */
    .filter-tabs-scroll {
      display: flex;
      gap: 7px;
      overflow-x: auto;
      scrollbar-width: none;
      -ms-overflow-style: none;
      padding-bottom: 2px;
    }

    .filter-tabs-scroll::-webkit-scrollbar {
      display: none;
    }

    .tab-pill {
      flex-shrink: 0;
      padding: 6px 13px;
      border-radius: var(--radius-pill);
      background: rgba(255, 255, 255, 0.07);
      border: 0.5px solid rgba(255, 255, 255, 0.08);
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.18s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    .tab-pill:active {
      transform: scale(0.95);
    }

    .tab-pill.active {
      background: #FFFFFF;
      border-color: #FFFFFF;
      color: #000000;
      box-shadow: 0 4px 14px rgba(255, 255, 255, 0.18);
    }

    .tab-pill.tab-revoked.active {
      background: var(--accent-red);
      border-color: #FF6961;
      color: #FFFFFF;
      box-shadow: 0 4px 14px rgba(255, 69, 58, 0.35);
    }

    .tab-count {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: var(--radius-pill);
      background: rgba(120, 120, 128, 0.28);
      color: inherit;
      font-weight: 700;
    }

    .tab-pill.active .tab-count {
      background: rgba(0, 0, 0, 0.12);
      color: #000000;
    }

    .tab-pill.tab-revoked.active .tab-count {
      background: rgba(0, 0, 0, 0.22);
      color: #FFFFFF;
    }

    .bento-stats {
      display: none !important;
    }

    /* Sticky Date Section Header */
    .date-group-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 4px 6px 4px;
      font-size: 13px;
      font-weight: 700;
      color: var(--text-secondary);
      letter-spacing: -0.1px;
    }

    .date-group-header:first-child {
      padding-top: 2px;
    }

    .date-group-count {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-muted);
    }

    /* iOS 18 Notification Center Cards */
    .noti-list {
      display: flex;
      flex-direction: column;
      gap: 9px;
    }

    .noti-card {
      background: var(--bg-card);
      backdrop-filter: blur(28px) saturate(180%);
      -webkit-backdrop-filter: blur(28px) saturate(180%);
      border: 0.5px solid rgba(255, 255, 255, 0.11);
      border-radius: 20px;
      padding: 13px 14px;
      position: relative;
      transition: transform 0.15s cubic-bezier(0.2, 0.8, 0.2, 1), background 0.15s ease;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.06);
      cursor: pointer;
    }

    .noti-card:active {
      transform: scale(0.982);
      background: var(--bg-card-hover);
    }

    .noti-card.revoked {
      background: linear-gradient(145deg, rgba(58, 16, 22, 0.86), rgba(28, 20, 26, 0.88));
      border: 0.5px solid rgba(255, 69, 58, 0.48);
    }

    .noti-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }

    /* Avatar + Mini App Badge */
    .avatar-wrap {
      position: relative;
      width: 44px;
      height: 44px;
      flex-shrink: 0;
      margin-top: 1px;
    }

    .app-icon-box {
      width: 44px;
      height: 44px;
      border-radius: 13px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 19px;
      font-weight: 800;
      color: #FFFFFF;
      overflow: hidden;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.25);
    }

    .app-icon-box img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .app-icon-box svg {
      width: 23px;
      height: 23px;
      fill: currentColor;
    }

    .mini-app-badge {
      position: absolute;
      bottom: -3px;
      right: -3px;
      width: 18px;
      height: 18px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 800;
      color: #FFF;
      border: 1.5px solid #161618;
      box-shadow: 0 1px 4px rgba(0,0,0,0.5);
    }

    .noti-main {
      flex: 1;
      min-width: 0;
    }

    .noti-header-line {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 2px;
    }

    .card-title {
      font-size: 15.5px;
      font-weight: 600;
      color: #FFFFFF;
      line-height: 1.28;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      letter-spacing: -0.25px;
    }

    .card-time-wrap {
      display: flex;
      align-items: center;
      gap: 5px;
      flex-shrink: 0;
    }

    .card-time {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
       font-variant-numeric: tabular-nums;
    }

    .card-subline {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 4px;
    }

    .app-name-label {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .pill-badge {
      font-size: 10.5px;
      font-weight: 700;
      padding: 1.5px 7px;
      border-radius: var(--radius-pill);
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }

    .badge-revoked {
      background: rgba(255, 69, 58, 0.22);
      color: #FF6961;
      border: 0.5px solid rgba(255, 69, 58, 0.5);
    }

    .badge-bank-in {
      background: rgba(48, 209, 88, 0.18);
      color: #30D158;
      border: 0.5px solid rgba(48, 209, 88, 0.4);
    }

    .badge-bank-out {
      background: rgba(255, 69, 58, 0.18);
      color: #FF6961;
      border: 0.5px solid rgba(255, 69, 58, 0.4);
    }

    .badge-cloud {
      background: rgba(10, 132, 255, 0.16);
      color: #64D2FF;
    }

    .card-body {
      font-size: 14.5px;
      line-height: 1.42;
      color: rgba(235, 235, 245, 0.86);
      word-break: break-word;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      transition: filter 0.2s ease;
    }

    body.privacy-masked .card-body,
    body.privacy-masked .card-media-img {
      filter: blur(8px);
    }

    body.privacy-masked .noti-card:hover .card-body,
    body.privacy-masked .noti-card:active .card-body,
    body.privacy-masked .noti-card:hover .card-media-img,
    body.privacy-masked .noti-card:active .card-media-img {
      filter: blur(0);
    }

    /* Attached Photo Preview inside Card */
    .card-media-wrap {
      margin-top: 9px;
      border-radius: 14px;
      overflow: hidden;
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      background: #0B0B0E;
      max-height: 210px;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .card-media-img {
      width: 100%;
      max-height: 210px;
      object-fit: cover;
      display: block;
    }

    .media-zoom-pill {
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      color: #FFF;
      font-size: 11px;
      font-weight: 600;
      padding: 4px 9px;
      border-radius: 999px;
      border: 0.5px solid rgba(255,255,255,0.2);
      pointer-events: none;
    }

    /* Contextual Smart Chips (Only shown for OTP / Phone / Link) */
    .smart-actions-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 9px;
    }

    .otp-copy-btn {
      background: rgba(48, 209, 88, 0.18);
      border: 0.5px solid rgba(48, 209, 88, 0.5);
      color: #30D158;
      font-size: 12.5px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .smart-chip {
      background: rgba(255, 255, 255, 0.08);
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      color: var(--text-primary);
      font-size: 12px;
      font-weight: 600;
      padding: 5px 11px;
      border-radius: var(--radius-pill);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      text-decoration: none;
    }

    .smart-chip:active {
      transform: scale(0.95);
      background: rgba(255, 255, 255, 0.16);
    }

    /* Banking Panel (iOS Wallet / Apple Card Style) */
    .banking-panel {
      background: linear-gradient(145deg, #161A26 0%, #10121A 100%);
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      border-radius: 22px;
      padding: 16px;
      margin-bottom: 14px;
      display: none;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
    }

    .banking-panel.visible {
      display: block;
    }

    .banking-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .banking-header h3 {
      margin: 0;
      font-size: 15px;
      font-weight: 700;
      color: #FFFFFF;
    }

    .banking-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 12px;
    }

    .bank-metric {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 14px;
      padding: 10px;
      border: 0.5px solid rgba(255, 255, 255, 0.06);
    }

    .bank-metric-label {
      font-size: 11px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .bank-metric-val {
      font-size: 13.5px;
      font-weight: 700;
    }

    .val-in { color: #30D158; }
    .val-out { color: #FF6961; }
    .val-net { color: #64D2FF; }

    .bank-chips-row {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      scrollbar-width: none;
      padding-bottom: 2px;
    }

    .bank-chip {
      flex-shrink: 0;
      font-size: 11.5px;
      padding: 5px 11px;
      border-radius: var(--radius-pill);
      background: rgba(255, 255, 255, 0.07);
      border: 0.5px solid rgba(255, 255, 255, 0.1);
      color: var(--text-secondary);
      cursor: pointer;
      font-weight: 600;
    }

    .bank-chip.active {
      background: var(--accent-blue);
      color: #FFF;
      border-color: var(--accent-blue-light);
    }

    /* Apple Photos Style Gallery Grid in Kho Ảnh */
    .photo-gallery-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      margin-bottom: 16px;
    }

    @media (min-width: 520px) {
      .photo-gallery-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }

    .photo-grid-item {
      position: relative;
      border-radius: 18px;
      overflow: hidden;
      background: #141416;
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      aspect-ratio: 1 / 1;
      cursor: pointer;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      transition: transform 0.15s ease;
    }

    .photo-grid-item:active {
      transform: scale(0.96);
    }

    .photo-grid-item img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .photo-grid-caption {
      position: absolute;
      inset: auto 0 0 0;
      padding: 20px 10px 8px 10px;
      background: linear-gradient(transparent, rgba(0, 0, 0, 0.86));
      font-size: 11.5px;
      color: #FFFFFF;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 600;
    }

    /* iOS 18 Settings Grouped Style for Management Tab */
    .mgmt-section {
      background: var(--bg-grouped);
      border: 0.5px solid rgba(255, 255, 255, 0.09);
      border-radius: 18px;
      padding: 15px 16px;
      margin-bottom: 14px;
    }

    .mgmt-section-title {
      font-size: 15px;
      font-weight: 700;
      color: #FFFFFF;
      margin: 0 0 6px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .mgmt-section-sub {
      font-size: 12.5px;
      color: var(--text-secondary);
      margin: 0 0 12px 0;
      line-height: 1.45;
    }

    .app-mgmt-row {
      display: flex;
      align-items: center;
      gap: 11px;
      padding: 10px 0;
      border-bottom: 0.5px solid rgba(255, 255, 255, 0.07);
    }

    .app-mgmt-row:last-child {
      border-bottom: none;
      padding-bottom: 2px;
    }

    .app-mgmt-info {
      flex: 1;
      min-width: 0;
    }

    .app-mgmt-name {
      font-size: 14px;
      font-weight: 600;
      color: #FFFFFF;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .app-mgmt-meta {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 1px;
    }

    .ota-banner {
      background: linear-gradient(135deg, rgba(10, 132, 255, 0.24), rgba(94, 92, 230, 0.24));
      border: 0.5px solid rgba(64, 156, 255, 0.45);
      border-radius: 20px;
      padding: 16px;
      margin-bottom: 14px;
    }

    /* Floating iOS 18 Capsule Bottom Tab Bar */
    .bottom-dock {
      position: fixed;
      bottom: calc(var(--safe-bottom) + 8px);
      left: 50%;
      transform: translateX(-50%);
      width: calc(100% - 28px);
      max-width: 460px;
      background: rgba(24, 24, 28, 0.84);
      backdrop-filter: blur(36px) saturate(210%);
      -webkit-backdrop-filter: blur(36px) saturate(210%);
      border: 0.5px solid rgba(255, 255, 255, 0.15);
      border-radius: 32px;
      padding: 6px 8px;
      display: flex;
      justify-content: space-around;
      align-items: center;
      z-index: 90;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .dock-btn {
      background: none;
      border: none;
      color: rgba(235, 235, 245, 0.5);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
      font-size: 10.5px;
      font-weight: 600;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: 22px;
      transition: all 0.18s cubic-bezier(0.2, 0.8, 0.2, 1);
      flex: 1;
    }

    .dock-btn .dock-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 22px;
    }

    .dock-btn svg {
      width: 21px;
      height: 21px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .dock-btn.active {
      color: #FFFFFF;
      background: rgba(255, 255, 255, 0.11);
    }

    .dock-btn.active svg {
      stroke: #0A84FF;
    }

    /* Modals & Bottom Sheets (iOS 18 Sheet Presentation) */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.68);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      z-index: 120;
      display: none;
      align-items: flex-end;
      justify-content: center;
    }

    .modal-backdrop.open {
      display: flex;
    }

    .modal-sheet {
      width: 100%;
      max-width: 640px;
      max-height: 88dvh;
      background: #1C1C1E;
      border-top: 0.5px solid rgba(255, 255, 255, 0.16);
      border-radius: 28px 28px 0 0;
      padding: 14px 18px calc(var(--safe-bottom) + 20px) 18px;
      overflow-y: auto;
      animation: slideUp 0.24s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideUp {
      from { transform: translateY(100%); }
      to { transform: translateY(0); }
    }

    .sheet-handle {
      width: 40px;
      height: 5px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.24);
      margin: 0 auto 12px auto;
    }

    .sheet-title {
      font-size: 17px;
      font-weight: 700;
      margin: 0 0 14px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .form-group { margin-bottom: 12px; }
    .form-label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 6px;
    }

    .form-input, .form-textarea, .form-select {
      width: 100%;
      padding: 11px 13px;
      border-radius: 12px;
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      background: #2C2C2E;
      color: #FFFFFF;
      font-size: 14px;
      outline: none;
      font-family: inherit;
    }

    .btn-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
    }

    .btn {
      padding: 10px 15px;
      border-radius: 13px;
      border: 0.5px solid rgba(255, 255, 255, 0.12);
      background: #2C2C2E;
      color: #FFFFFF;
      font-size: 13.5px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      text-decoration: none;
      flex: 1;
      transition: transform 0.14s ease, opacity 0.14s ease;
    }

    .btn:active { transform: scale(0.96); }
    .btn-primary { background: var(--accent-blue); border-color: var(--accent-blue-light); color: #FFF; }
    .btn-success { background: #248A3D; border-color: #30D158; color: #FFF; }
    .btn-danger { background: rgba(255, 69, 58, 0.18); border-color: rgba(255, 69, 58, 0.4); color: #FF6961; }

    /* Chat Thread Bubbles inside Detail Sheet */
    .chat-thread-box {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 12px;
      max-height: 52dvh;
      overflow-y: auto;
      padding: 4px 2px;
    }

    .chat-bubble {
      background: #2C2C2E;
      border: 0.5px solid rgba(255, 255, 255, 0.08);
      border-radius: 18px 18px 18px 6px;
      padding: 10px 13px;
      position: relative;
    }

    .chat-bubble.active-bubble {
      background: rgba(10, 132, 255, 0.22);
      border-color: rgba(10, 132, 255, 0.55);
    }

    .chat-bubble.revoked-bubble {
      background: rgba(255, 69, 58, 0.18);
      border-color: rgba(255, 69, 58, 0.45);
    }

    .chat-bubble-meta {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .chat-bubble-text {
      font-size: 14.5px;
      line-height: 1.4;
      color: #FFFFFF;
      word-break: break-word;
    }

    /* Quick Action Grid inside Detail Sheet */
    .sheet-action-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 7px;
      margin-bottom: 14px;
    }

    .sheet-action-btn {
      background: #2C2C2E;
      border: 0.5px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      padding: 9px 4px;
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 600;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 5px;
      cursor: pointer;
    }

    .sheet-action-btn:active {
      transform: scale(0.94);
      background: #3A3A3C;
    }

    /* Lock Screen, Lightbox, Toast & Empty State */
    .lock-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.94);
      backdrop-filter: blur(32px);
      -webkit-backdrop-filter: blur(32px);
      z-index: 200;
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .lock-overlay.locked { display: flex; }
    .pin-dots { display: flex; gap: 16px; margin: 22px 0 32px 0; }
    .pin-dot { width: 14px; height: 14px; border-radius: 50%; border: 2px solid #0A84FF; transition: all 0.15s ease; }
    .pin-dot.filled { background: #0A84FF; transform: scale(1.15); }
    .pin-keypad { display: grid; grid-template-columns: repeat(3, 74px); gap: 16px; }
    .pin-key {
      width: 74px; height: 74px; border-radius: 50%;
      border: 0.5px solid rgba(255, 255, 255, 0.16);
      background: rgba(255, 255, 255, 0.08);
      color: #FFF; font-size: 26px; font-weight: 500;
      cursor: pointer; display: flex; align-items: center; justify-content: center;
    }
    .pin-key:active { background: rgba(10, 132, 255, 0.4); }

    .lightbox-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.94);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 180;
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .lightbox-overlay.open { display: flex; }
    .lightbox-overlay img {
      max-width: 96vw;
      max-height: 76dvh;
      border-radius: 18px;
      object-fit: contain;
      box-shadow: 0 12px 40px rgba(0,0,0,0.7);
    }

    .toast-box {
      position: fixed;
      top: calc(var(--safe-top) + 12px);
      left: 50%;
      transform: translateX(-50%) translateY(-130px);
      background: rgba(28, 28, 32, 0.95);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 0.5px solid rgba(255, 255, 255, 0.18);
      color: #FFF;
      padding: 10px 18px;
      border-radius: var(--radius-pill);
      font-size: 13px;
      font-weight: 600;
      z-index: 250;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.55);
      transition: transform 0.26s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
      text-align: center;
      max-width: 90vw;
    }
    .toast-box.show { transform: translateX(-50%) translateY(0); }

    .empty-state {
      text-align: center;
      padding: 48px 20px;
      background: var(--bg-grouped);
      border: 0.5px solid rgba(255, 255, 255, 0.08);
      border-radius: 22px;
      color: var(--text-secondary);
      margin-top: 8px;
    }

    .install-banner {
      background: rgba(10, 132, 255, 0.14);
      border: 0.5px solid rgba(10, 132, 255, 0.35);
      border-radius: 16px;
      padding: 10px 13px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 12px;
      color: #D1E9FF;
    }
  </style>"""

html = re.sub(r"<style>.*?</style>", new_style, html, count=1, flags=re.S)

# 2. Replace Header & Filter Tabs & Bottom Dock with sleek iOS 18 SVG Icons
old_header_section = re.search(r"<!-- Sticky Header -->.*?</nav>", html, flags=re.S)
new_header_and_dock = """<!-- Sticky Header -->
    <header class="top-header">
      <div class="brand-row">
        <div class="brand-left">
          <div class="app-squircle-logo" onclick="syncNow(true)" title="Chạm để đồng bộ ngay">
            <svg viewBox="0 0 24 24">
              <path d="M12 22c1.1 0 2-.9 2-2h-4a2 2 0 002 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
            </svg>
            <span class="live-dot" id="liveSyncDot"></span>
          </div>
          <div class="brand-titles">
            <h1>
              NotiStar
              <span class="ios-badge">OneUI 7</span>
            </h1>
            <div class="sync-status-line" id="syncStatusText">
              Đã đồng bộ Cloud
            </div>
          </div>
        </div>

        <div class="header-actions">
          <button class="icon-btn" id="btnSyncNow" onclick="syncNow(true)" title="Đồng bộ Google Drive">
            <svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>
          </button>
          <button class="icon-btn" id="btnVoiceToggle" onclick="toggleVoiceAnnouncer()" title="Loa Ting-Ting đọc thông báo">
            <span id="voiceIconSpan" style="display:flex;"><svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg></span>
          </button>
          <button class="icon-btn" id="btnPrivacyMask" onclick="togglePrivacyMask()" title="Che nội dung nhạy cảm">
            <svg viewBox="0 0 24 24"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
          <button class="icon-btn" onclick="openModal('captureModal')" title="Lưu nhanh ảnh / clipboard" style="background:var(--accent-blue);border-color:var(--accent-blue-light);">
            <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
        </div>
      </div>

      <!-- Search Row -->
      <div class="search-row">
        <div class="search-input-wrap">
          <span class="search-icon">
            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </span>
          <input
            type="search"
            id="searchInput"
            class="search-input"
            placeholder="Tìm tin nhắn, người gửi, số tiền, OTP..."
            oninput="onSearchChange()"
          />
          <button id="clearSearchBtn" class="clear-search-btn" onclick="clearSearch()">✕</button>
        </div>
      </div>

      <!-- Filter Pills -->
      <div class="filter-tabs-scroll" id="filterTabsBar">
        <button class="tab-pill active" data-tab="all" onclick="switchTab('all')">
          Tất cả <span class="tab-count" id="countAll">0</span>
        </button>
        <button class="tab-pill" data-tab="chat" onclick="switchTab('chat')">
          Tin nhắn <span class="tab-count" id="countChat">0</span>
        </button>
        <button class="tab-pill tab-revoked" data-tab="revoked" onclick="switchTab('revoked')">
          Đã thu hồi <span class="tab-count" id="countRevoked">0</span>
        </button>
        <button class="tab-pill" data-tab="media" onclick="switchTab('media')">
          Kho Ảnh <span class="tab-count" id="countMedia">0</span>
        </button>
        <button class="tab-pill" data-tab="bank" onclick="switchTab('bank')">
          Ngân hàng <span class="tab-count" id="countBank">0</span>
        </button>
        <button class="tab-pill" data-tab="starred" onclick="switchTab('starred')">
          Đánh dấu <span class="tab-count" id="countStarred">0</span>
        </button>
        <button class="tab-pill" data-tab="links" onclick="switchTab('links')">
          Link &amp; SĐT <span class="tab-count" id="countLinks">0</span>
        </button>
      </div>
    </header>

    <div id="iosInstallBanner" class="install-banner" style="display:none;">
      <div class="install-banner-text">
        <strong>Cài App Full-Screen:</strong> Nhấn nút <strong>Chia sẻ [↑]</strong> &rarr; <strong>"Thêm vào MH chính"</strong>
      </div>
      <button class="icon-btn" onclick="openModal('iosGuideModal')" title="Hướng dẫn">ℹ️</button>
    </div>

    <section class="bento-stats">
      <div class="bento-card"><div class="bento-num" id="statTotal">0</div></div>
      <div class="bento-card"><div class="bento-num" id="statRevoked">0</div></div>
      <div class="bento-card"><div class="bento-num" id="statMedia">0</div></div>
      <div class="bento-card"><div class="bento-num" id="statBankTx">0</div></div>
    </section>

    <!-- Smart Banking Ledger Panel -->
    <section id="bankingLedgerPanel" class="banking-panel">
      <div class="banking-header">
        <h3>Sổ phụ Ngân hàng &amp; Biến động</h3>
        <button class="smart-chip" onclick="speakBankingSummary()">Đọc tổng kết</button>
      </div>
      <div class="banking-grid">
        <div class="bank-metric">
          <div class="bank-metric-label">Tiền vào (+)</div>
          <div class="bank-metric-val val-in" id="bankTotalIn">+0 ₫</div>
        </div>
        <div class="bank-metric">
          <div class="bank-metric-label">Tiền ra (-)</div>
          <div class="bank-metric-val val-out" id="bankTotalOut">-0 ₫</div>
        </div>
        <div class="bank-metric">
          <div class="bank-metric-label">Chênh lệch</div>
          <div class="bank-metric-val val-net" id="bankNetChange">0 ₫</div>
        </div>
      </div>
      <div class="bank-chips-row" id="bankBreakdownRow"></div>
    </section>

    <!-- Notification List Container -->
    <main id="notiListContainer" class="noti-list"></main>
  </div>

  <!-- iOS 18 Translucent Floating Capsule Dock -->
  <nav class="bottom-dock">
    <button class="dock-btn active" id="dockAll" onclick="switchTab('all')">
      <span class="dock-icon">
        <svg viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
      </span>
      <span>Thông báo</span>
    </button>
    <button class="dock-btn" id="dockRevoked" onclick="switchTab('revoked')">
      <span class="dock-icon">
        <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </span>
      <span>Thu hồi</span>
    </button>
    <button class="dock-btn" id="dockMedia" onclick="switchTab('media')">
      <span class="dock-icon">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="3" ry="3"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      </span>
      <span>Kho Ảnh</span>
    </button>
    <button class="dock-btn" id="dockBank" onclick="switchTab('bank')">
      <span class="dock-icon">
        <svg viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
      </span>
      <span>Ngân hàng</span>
    </button>
    <button class="dock-btn" id="dockManage" onclick="switchTab('manage')">
      <span class="dock-icon">
        <svg viewBox="0 0 24 24"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>
      </span>
      <span>Quản lý</span>
    </button>
  </nav>

  <!-- Modal Detail & Conversation Sheet (Opens when tapping any Notification Card) -->
  <div id="detailModal" class="modal-backdrop" onclick="closeModalOnBackdrop(event, 'detailModal')">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div id="detailModalContent"></div>
    </div>
  </div>"""

if old_header_section:
    html = html[:old_header_section.start()] + new_header_and_dock + html[old_header_section.end():]

# 3. Update CURRENT_OTA_VERSION_CODE to 5 and CURRENT_OTA_VERSION_NAME to "9.1.0-iOS18"
html = html.replace('const CURRENT_OTA_VERSION_CODE = 3;', 'const CURRENT_OTA_VERSION_CODE = 5;')
html = html.replace('const CURRENT_OTA_VERSION_NAME = "9.0.82-OTA";', 'const CURRENT_OTA_VERSION_NAME = "9.1.0-iOS18";')

# 4. Replace the rendering logic (from `const htmlParts = [];` inside `renderApp` through `function renderNotificationCardHtml(item) { ... }`)
old_render_cards = re.search(
    r"const htmlParts = \[\];\s*if \(currentTab === \"media\".*?function toggleRevokedByUid\(uid\)",
    html,
    flags=re.S
)

new_render_cards = """const htmlParts = [];
      if (currentTab === "media" && filtered.length > 0) {
        htmlParts.push(renderPhotoGalleryGridHtml(filtered));
      }

      let lastDateHeader = "";
      for (const item of filtered.slice(0, 250)) {
        const dHeader = getFriendlyDateHeader(item.time);
        if (dHeader !== lastDateHeader) {
          lastDateHeader = dHeader;
          htmlParts.push(`
            <div class="date-group-header">
              <span>${escapeHtml(dHeader)}</span>
            </div>
          `);
        }
        htmlParts.push(renderNotificationCardHtml(item));
      }
      container.innerHTML = htmlParts.join("");
    }

    function getFriendlyDateHeader(ts) {
      const d = new Date(Number(ts) || Date.now());
      const now = new Date();
      const todayStr = now.toDateString();
      const yest = new Date(now.getTime() - 86400000).toDateString();
      if (d.toDateString() === todayStr) return "Hôm nay";
      if (d.toDateString() === yest) return "Hôm qua";
      const dd = String(d.getDate()).padStart(2, "0");
      const mm = String(d.getMonth() + 1).padStart(2, "0");
      const yyyy = d.getFullYear();
      return `Ngày ${dd} tháng ${mm}, ${yyyy}`;
    }

    function formatShortSmartTime(ts) {
      const ms = Number(ts) || Date.now();
      const diffSec = Math.floor((Date.now() - ms) / 1000);
      if (diffSec >= 0 && diffSec < 60) return "Vừa xong";
      if (diffSec >= 60 && diffSec < 3600) return `${Math.floor(diffSec / 60)} phút`;
      const d = new Date(ms);
      const hh = String(d.getHours()).padStart(2, "0");
      const mi = String(d.getMinutes()).padStart(2, "0");
      return `${hh}:${mi}`;
    }

    function getAppBrandStyle(appName, pkgName, isBank) {
      const hay = `${appName || ""} ${pkgName || ""}`.toLowerCase();
      if (hay.includes("zalo")) {
        return { bg: "linear-gradient(145deg, #0068FF, #0052CC)", label: "Z", badgeColor: "#0068FF" };
      }
      if (hay.includes("telegram")) {
        return {
          bg: "linear-gradient(145deg, #2AABEE, #229ED9)",
          svg: `<svg viewBox="0 0 24 24"><path d="M21.9 4.4 2.9 11.7c-1.3.5-1.3 1.2-.2 1.6l4.9 1.5 11.3-7.1c.5-.3 1-.1.6.2l-9.2 8.3-.3 4.8c.5 0 .7-.2 1-.5l2.4-2.3 5 3.7c.9.5 1.6.2 1.8-.9L23 5.6c.3-1.2-.5-1.8-1.1-1.2z"/></svg>`,
          label: "T",
          badgeColor: "#2AABEE"
        };
      }
      if (hay.includes("messenger") || hay.includes("orca")) {
        return {
          bg: "linear-gradient(145deg, #00B2FF, #006AFF, #9B00E8)",
          svg: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.14 2 11.25c0 2.91 1.45 5.51 3.72 7.21V22l3.4-1.87c.91.25 1.88.38 2.88.38 5.52 0 10-4.14 10-9.25S17.52 2 12 2zm1.08 12.42-2.55-2.72-4.97 2.72 5.47-5.8 2.61 2.72 4.91-2.72-5.47 5.8z"/></svg>`,
          label: "M",
          badgeColor: "#006AFF"
        };
      }
      if (hay.includes("facebook") || hay.includes("katana")) {
        return { bg: "linear-gradient(145deg, #1877F2, #0C5DC7)", label: "f", badgeColor: "#1877F2" };
      }
      if (hay.includes("youtube")) {
        return {
          bg: "linear-gradient(145deg, #FF0033, #CC0000)",
          svg: `<svg viewBox="0 0 24 24"><polygon points="9.5 7.5 16.5 12 9.5 16.5 9.5 7.5"/></svg>`,
          label: "▶",
          badgeColor: "#FF0033"
        };
      }
      if (hay.includes("shopee")) {
        return { bg: "linear-gradient(145deg, #FF6533, #EE4D2D)", label: "S", badgeColor: "#EE4D2D" };
      }
      if (hay.includes("photos") || hay.includes("gallery") || hay.includes("iphoto")) {
        return { bg: "linear-gradient(145deg, #FF5E3A, #FF2A68, #5856D6)", label: "✿", badgeColor: "#5856D6" };
      }
      if (hay.includes("tiktok") || hay.includes("trill")) {
        return { bg: "linear-gradient(145deg, #111111, #25F4EE, #FE2C55)", label: "♪", badgeColor: "#FE2C55" };
      }
      if (hay.includes("gmail") || hay.includes("mail")) {
        return { bg: "linear-gradient(145deg, #EA4335, #C5221F)", label: "M", badgeColor: "#EA4335" };
      }
      if (isBank || hay.includes("bank") || hay.includes("momo") || hay.includes("zalopay")) {
        return { bg: "linear-gradient(145deg, #30D158, #1E8E3E)", label: "₫", badgeColor: "#30D158" };
      }
      if (hay.includes("phone") || hay.includes("call") || hay.includes("incallui") || hay.includes("điện thoại")) {
        return { bg: "linear-gradient(145deg, #34C759, #248A3D)", label: "✆", badgeColor: "#34C759" };
      }
      const firstChar = String(appName || "N").trim().charAt(0).toUpperCase() || "N";
      return { bg: "linear-gradient(145deg, #0A84FF, #5E5CE6)", label: firstChar, badgeColor: "#0A84FF" };
    }

    function renderAppAvatarHtml(item, tx) {
      const brand = getAppBrandStyle(item.appName, item.packageName, Boolean(tx));
      if (item.largeIconB64 && item.largeIconB64.length > 50) {
        const avatarSrc = formatB64Src(item.largeIconB64);
        return `
          <div class="avatar-wrap">
            <div class="app-icon-box" style="background:#2C2C2E;">
              <img src="${avatarSrc}" alt="avatar" loading="lazy" />
            </div>
            <span class="mini-app-badge" style="background:${brand.badgeColor};">${brand.label}</span>
          </div>
        `;
      }
      return `
        <div class="avatar-wrap">
          <div class="app-icon-box" style="background:${brand.bg};">
            ${brand.svg || `<span>${escapeHtml(brand.label)}</span>`}
          </div>
        </div>
      `;
    }

    function renderPhotoGalleryGridHtml(mediaItems) {
      const cells = [];
      for (const item of mediaItems.slice(0, 60)) {
        const b64 = getItemMediaB64(item);
        if (!b64) continue;
        const src = formatB64Src(b64);
        cells.push(`
          <div class="photo-grid-item" onclick="openLightbox('${escapeAttr(src)}')">
            <img src="${src}" alt="${escapeAttr(item.title)}" loading="lazy" />
            <div class="photo-grid-caption">${escapeHtml(item.appName)} • ${escapeHtml(item.title)}</div>
          </div>
        `);
      }
      if (cells.length === 0) return "";
      return `
        <div class="mgmt-section" style="padding:14px;">
          <div class="mgmt-section-title" style="font-size:14px;margin-bottom:10px;">
            <span>Bộ sưu tập Ảnh đính kèm (${cells.length})</span>
            <label class="smart-chip" style="color:#64D2FF;cursor:pointer;margin:0;">
              + Thêm ảnh iOS
              <input type="file" accept="image/*" style="display:none;" onchange="handleQuickIosPhotoUpload(event)" />
            </label>
          </div>
          <div class="photo-gallery-grid">${cells.join("")}</div>
        </div>
      `;
    }

    function renderNotificationCardHtml(item) {
      const body = getDisplayBody(item);
      const otp = extractOtp(item);
      const tx = extractBankTransaction(item);
      const extracted = extractLinksPhonesEmails(item);
      const avatarHtml = renderAppAvatarHtml(item, tx);

      const badges = [];
      if (item.isRevoked) {
        badges.push(`<span class="pill-badge badge-revoked">Đã thu hồi</span>`);
      }
      if (tx) {
        badges.push(
          tx.isIncome
            ? `<span class="pill-badge badge-bank-in">${escapeHtml(tx.bankName)} ${formatVnd(tx.amountVnd, true)}</span>`
            : `<span class="pill-badge badge-bank-out">${escapeHtml(tx.bankName)} ${formatVnd(-tx.amountVnd, true)}</span>`
        );
      }

      // Media Picture
      let mediaHtml = "";
      const mediaB64 = getItemMediaB64(item);
      if (mediaB64) {
        const src = formatB64Src(mediaB64);
        mediaHtml = `
          <div class="card-media-wrap" onclick="event.stopPropagation(); openLightbox('${escapeAttr(src)}')">
            <img class="card-media-img" src="${src}" alt="Ảnh đính kèm" loading="lazy" />
            <span class="media-zoom-pill">Xem ảnh</span>
          </div>
        `;
      }

      // Contextual Smart Chips (ONLY shown if there is an OTP, Phone, or Link!)
      const chips = [];
      if (otp) {
        chips.push(`
          <button class="otp-copy-btn" onclick="event.stopPropagation(); copyTextToClipboard('${escapeAttr(otp)}', 'Đã sao chép OTP: ${escapeAttr(otp)}')">
            Sao chép OTP: ${escapeHtml(otp)}
          </button>
        `);
      }
      for (const phone of extracted.phones.slice(0, 2)) {
        chips.push(`
          <a class="smart-chip" href="tel:${escapeAttr(phone)}" onclick="event.stopPropagation()">
            Gọi ${escapeHtml(phone)}
          </a>
        `);
      }
      for (const url of extracted.urls.slice(0, 1)) {
        let shortHost = url;
        try { shortHost = new URL(url).hostname.replace(/^www\\./, ""); } catch (e) {}
        chips.push(`
          <a class="smart-chip" href="${escapeAttr(url)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">
            Mở ${escapeHtml(shortHost)}
          </a>
        `);
      }

      const chipsBarHtml = chips.length > 0 ? `<div class="smart-actions-bar">${chips.join("")}</div>` : "";
      const starMark = item.isStarred ? `<span style="color:#FFD60A;font-size:13px;">★</span>` : "";

      return `
        <article class="noti-card ${item.isRevoked ? "revoked" : ""}" onclick="openNotificationDetail('${escapeAttr(item.uid)}')">
          <div class="noti-row">
            ${avatarHtml}
            <div class="noti-main">
              <div class="noti-header-line">
                <div class="card-title selectable">${escapeHtml(item.title || item.appName)}</div>
                <div class="card-time-wrap">
                  ${starMark}
                  <span class="card-time">${formatShortSmartTime(item.time)}</span>
                </div>
              </div>
              <div class="card-subline">
                <span class="app-name-label">${escapeHtml(item.appName)}</span>
                ${badges.join("")}
              </div>
              <div class="card-body selectable">${escapeHtml(body)}</div>
              ${mediaHtml}
              ${chipsBarHtml}
            </div>
          </div>
        </article>
      `;
    }

    function openNotificationDetail(uid) {
      const item = allNotifications.find((n) => n.uid === uid);
      if (!item) return;
      const box = document.getElementById("detailModalContent");
      if (!box) return;

      // Tìm toàn bộ hội thoại cùng người gửi / cùng ứng dụng
      const related = allNotifications
        .filter((n) => (n.packageName || n.appName) === (item.packageName || item.appName) && n.title === item.title)
        .sort((a, b) => a.time - b.time);

      const threadItems = related.length > 0 ? related : [item];
      const bubblesHtml = threadItems.map((m) => {
        const mBody = getDisplayBody(m);
        const mMediaB64 = getItemMediaB64(m);
        const mMediaHtml = mMediaB64
          ? `<div class="card-media-wrap" style="margin-top:8px;" onclick="openLightbox('${escapeAttr(formatB64Src(mMediaB64))}')"><img class="card-media-img" src="${formatB64Src(mMediaB64)}" /></div>`
          : "";
        const activeCls = m.uid === item.uid ? "active-bubble" : "";
        const revCls = m.isRevoked ? "revoked-bubble" : "";
        return `
          <div class="chat-bubble ${activeCls} ${revCls}">
            <div class="chat-bubble-meta">
              <span>${escapeHtml(m.appName)} ${m.isRevoked ? "• <strong style='color:#FF6961;'>Đã thu hồi</strong>" : ""}</span>
              <span>${formatDateTime(m.time)}</span>
            </div>
            <div class="chat-bubble-text selectable">${escapeHtml(mBody)}</div>
            ${mMediaHtml}
          </div>
        `;
      }).join("");

      box.innerHTML = `
        <div class="sheet-title">
          <div style="display:flex;align-items:center;gap:10px;min-width:0;">
            ${renderAppAvatarHtml(item, null)}
            <div style="min-width:0;">
              <div style="font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(item.title || item.appName)}</div>
              <div style="font-size:12px;color:var(--text-secondary);font-weight:500;">${escapeHtml(item.appName)} • ${threadItems.length} tin nhắn</div>
            </div>
          </div>
          <button class="icon-btn" onclick="closeModal('detailModal')">✕</button>
        </div>

        <div class="sheet-action-grid">
          <button class="sheet-action-btn" onclick="copyNotificationByUid('${escapeAttr(item.uid)}')">
            <span>Sao chép</span>
          </button>
          <button class="sheet-action-btn" onclick="speakNotificationByUid('${escapeAttr(item.uid)}')">
            <span>Đọc loa</span>
          </button>
          <button class="sheet-action-btn" onclick="toggleStarByUid('${escapeAttr(item.uid)}'); openNotificationDetail('${escapeAttr(item.uid)}')">
            <span style="color:${item.isStarred ? '#FFD60A' : '#FFF'};">${item.isStarred ? 'Bỏ ghim ★' : 'Ghim ★'}</span>
          </button>
          <button class="sheet-action-btn" onclick="toggleRevokedByUid('${escapeAttr(item.uid)}'); openNotificationDetail('${escapeAttr(item.uid)}')">
            <span style="color:${item.isRevoked ? '#30D158' : '#FF6961'};">${item.isRevoked ? 'Bỏ thu hồi' : 'Báo thu hồi'}</span>
          </button>
          <button class="sheet-action-btn" onclick="deleteNotificationByUid('${escapeAttr(item.uid)}'); closeModal('detailModal')">
            <span style="color:#FF6961;">Xóa tin</span>
          </button>
        </div>

        <div style="font-size:12px;font-weight:700;color:var(--text-secondary);margin-bottom:4px;">
          DÒNG THỜI GIAN HỘI THOẠI (${threadItems.length})
        </div>
        <div class="chat-thread-box">
          ${bubblesHtml}
        </div>
      `;

      openModal("detailModal");
    }

    async function toggleRevokedByUid(uid)"""

if old_render_cards:
    html = html[:old_render_cards.start()] + new_render_cards + html[old_render_cards.end():]

# 5. Also refine renderManagementViewHtml() so each app row shows its crisp brand icon
if '<div class="app-mgmt-row">${renderAppAvatarHtml' not in html:
    html = html.replace(
        '<div class="app-mgmt-row">',
        '<div class="app-mgmt-row">${renderAppAvatarHtml({ appName: a.name, packageName: a.key }, null)}'
    )

html = html.replace(
    'voiceIcon.textContent = on ? "🔊" : "🔇";',
    'voiceIcon.innerHTML = on ? `<svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>` : `<svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>`;'
)

if 'visibilityState === "visible"' not in html:
    html = html.replace(
        'checkOtaUpdate(false);',
        'checkOtaUpdate(false);\n      document.addEventListener("visibilitychange", () => {\n        if (document.visibilityState === "visible") {\n          checkOtaUpdate(false);\n          syncNow(false);\n        }\n      });',
        1
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully upgraded WebApp_PWA/index.html to iOS 18 Luxe UI! Size:", os.path.getsize(path))
