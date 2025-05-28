# VRChat VR環境専用最適化ツール 🥽

VRヘッドセット（Oculus/Meta Quest、SteamVR、WMR等）およびVirtual Desktop環境でのVRChat最適化に特化したツールセットです。

## 🎯 概要

このツールセットは、VR環境でのVRChat体験を大幅に改善するために設計されています：

- **VR FPS向上**: 20-40%のパフォーマンス向上
- **フレームドロップ軽減**: VR酔い防止
- **ネットワーク遅延軽減**: Virtual Desktop環境での快適性向上
- **VRヘッドセット別最適化**: 各デバイスに特化した設定
- **リアルタイム監視**: Streamlitダッシュボードによる詳細監視
- **自動復旧機能**: Virtual Desktop・SteamVR自動復旧サービス
- **🆕 電源断復旧**: Windows起動時のVR環境自動起動
- **🆕 統合管理**: 全機能を一つのツールで管理

## 📁 ファイル構成

### 🔧 最適化スクリプト
- `VRChat_VR_Optimizer_Clean.ps1` - VR環境用最適化スクリプト（クリーン版）
- `VRChat_VR_Optimizer_Fixed.ps1` - VR環境用最適化スクリプト（修正版）
- `VirtualDesktop_VRChat_Optimizer_Clean.ps1` - Virtual Desktop専用最適化

### 📊 監視・分析ツール
- `VRChat_VR_Performance_Monitor.ps1` - VR環境用パフォーマンス監視
- `vrchat_vr_fps_analyzer.py` - VR環境用FPS分析ツール（Python）
- `vr_system_monitor.py` - Streamlitダッシュボード（リアルタイム監視）
- `vr_auto_recovery_service.py` - VR自動復旧サービス（強化版）
- `vr_startup_manager.py` - VR環境スタートアップマネージャー
- **🆕 `vr_integrated_manager.py` - VR環境統合管理ツール（オールインワン）**

### 🚀 起動用バッチファイル
- `VR監視ダッシュボード起動.bat` - Streamlitダッシュボード起動
- `VR自動復旧サービス起動.bat` - 自動復旧サービス起動
- `VR環境スタートアップ設定.bat` - スタートアップマネージャー起動
- **🆕 `VR統合管理ツール起動.bat` - 統合管理ツール起動**

### 📖 ガイド・設定
- `VR環境専用ガイド.txt` - VR環境専用使用ガイド
- `Virtual Desktop専用ガイド.txt` - Virtual Desktop使用ガイド
- `requirements.txt` - Python依存関係

## 🚀 クイックスタート

### 🆕 統合管理ツール（推奨）

```bash
# 統合管理ツール起動（すべての機能を一つで管理）
VR統合管理ツール起動.bat

# または直接実行
py -3 vr_integrated_manager.py
```

**統合管理ツールの機能:**
- VR環境の即座起動
- Windows起動時の自動実行設定/解除
- 自動復旧監視の開始/停止
- アプリケーション検出状況の確認
- 統合されたメニューインターフェース

**コマンドライン引数:**
```bash
# Windows起動時の自動実行（内部使用）
py -3 vr_integrated_manager.py --startup

# 自動実行設定
py -3 vr_integrated_manager.py --install

# 自動実行解除
py -3 vr_integrated_manager.py --uninstall

# 設定状態確認
py -3 vr_integrated_manager.py --status

# 起動シーケンステスト
py -3 vr_integrated_manager.py --test

# 自動復旧監視開始
py -3 vr_integrated_manager.py --monitor
```

### 1. VRヘッドセット環境

```powershell
# 管理者権限でPowerShellを起動
# VR専用最適化実行
.\VRChat_VR_Optimizer_Clean.ps1

# パフォーマンス監視
.\VRChat_VR_Performance_Monitor.ps1 -Monitor

# FPS分析（Python）
py -3 vrchat_vr_fps_analyzer.py
```

### 2. Virtual Desktop環境

```powershell
# Virtual Desktop専用最適化
.\VirtualDesktop_VRChat_Optimizer_Clean.ps1

# 最適化後はPC再起動推奨
```

### 3. リアルタイム監視ダッシュボード

```bash
# Streamlitダッシュボード起動
VR監視ダッシュボード起動.bat

# ブラウザで http://localhost:8501 にアクセス
```

### 4. 自動復旧サービス

```bash
# Virtual Desktop・SteamVR自動復旧サービス起動
VR自動復旧サービス起動.bat

# バックグラウンドで監視・自動復旧を実行
```

### 5. 🆕 電源断復旧・スタートアップ設定

```bash
# VR環境スタートアップマネージャー起動
VR環境スタートアップ設定.bat

# Windows起動時の自動実行を設定
```

## 🆕 新機能: VR環境スタートアップマネージャー

### 🔄 電源断復旧機能
- **Windows起動時自動実行**: PC起動時にVR環境を自動起動
- **Steam自動起動**: SteamVRの前提条件として自動起動
- **SteamVR自動起動**: VR環境の中核として自動起動
- **Virtual Desktop自動起動**: ワイヤレスVR環境として自動起動
- **🆕 VRChat自動起動**: SteamVR起動確認後にVRモードで自動起動

### ⚙️ スタートアップ設定
- **自動実行設定**: Windows起動時の自動実行を設定
- **自動実行解除**: 自動実行設定を解除
- **設定状態確認**: 現在の自動実行設定を確認
- **テスト実行**: 起動シーケンスをテスト実行

### 🛡️ 復旧制御機能
- **起動遅延**: システム安定化のため30秒待機
- **リトライ機能**: 最大3回まで起動を試行
- **依存関係管理**: Steam → SteamVR → VRChat の順序で起動
- **プロセス監視**: 起動完了を確認してから次のステップ
- **VRモード確認**: SteamVR起動確認後にVRChatをVRモードで起動

### 📝 起動シーケンス
1. **システム安定化待機** (30秒)
2. **Steam起動** (SteamVRの前提条件)
3. **Virtual Desktop起動** (ワイヤレスVR用)
4. **SteamVR起動** (VR環境の中核)
5. **🆕 VRChat起動** (VRモードで自動起動)

## 🆕 新機能: Streamlitダッシュボード

### 📊 リアルタイム監視項目
- **CPU使用率・温度** - リアルタイムグラフ表示
- **メモリ使用率・使用量** - 詳細な使用状況
- **GPU使用率・温度** - NVIDIA/AMD GPU対応
- **VRAM使用率・使用量** - ビデオメモリ監視
- **VR関連プロセス状態** - VRChat、Virtual Desktop等の状態

### 🔧 ダッシュボード機能
- **リアルタイム更新** - 2秒間隔での自動更新
- **履歴グラフ表示** - 最新100データポイントの履歴
- **プロセス監視** - VR関連アプリケーションの実行状態
- **手動復旧ボタン** - Virtual Desktop手動再起動
- **自動復旧設定** - Virtual Desktop自動復旧の有効/無効

### 📈 監視画面の特徴
- **日本語対応** - 完全日本語インターフェース
- **VR特化設計** - VR環境に最適化された監視項目
- **美しいUI** - Streamlitによる直感的なダッシュボード
- **カラーコード表示** - 状態に応じた色分け表示

## 🆕 新機能: VR自動復旧サービス（強化版）

### 🔄 自動復旧機能
- **Virtual Desktop監視** - 30秒間隔での状態チェック
- **🆕 SteamVR監視** - SteamVRプロセスの監視・復旧
- **🆕 Steam監視** - SteamVR用Steamプロセスの監視
- **🆕 VRChat監視** - SteamVR起動時のVRChat監視・復旧
- **自動再起動** - プロセス停止時の自動復旧
- **復旧制限** - 過度な復旧試行を防ぐ制限機能
- **クールダウン** - 5分間の復旧間隔制御

### 📝 ログ機能
- **詳細ログ** - `vr_auto_recovery.log`に記録
- **復旧履歴** - 復旧試行の詳細記録
- **エラー追跡** - 問題発生時の詳細情報

### ⚙️ 復旧設定
- **最大試行回数**: 3回（1時間でリセット）
- **クールダウン期間**: 5分間
- **監視間隔**: 30秒
- **対象プロセス**: Virtual Desktop Streamer、SteamVR、Steam、VRChat

## 🎮 対応VRヘッドセット

- **Oculus/Meta Quest** (Quest 2, Quest 3, Quest Pro)
  - ASW（Asynchronous SpaceWarp）最適化
  - Oculus Debug Tool設定
- **SteamVR対応デバイス**
  - モーションスムージング最適化
  - 高度なフレームタイミング
- **Windows Mixed Reality**
  - 90Hzモード最適化
  - 境界設定最適化
- **Pico VR**
  - 基本的なVR最適化対応

## 📈 期待される効果

### パフォーマンス向上
- ✅ VR FPS向上: 20-40%
- ✅ フレームドロップ大幅減少
- ✅ VR酔い軽減
- ✅ フレームタイム安定化

### VRヘッドセット別最適化
- ✅ 90Hz/120Hz対応最適化
- ✅ ASW/モーションスムージング最適化
- ✅ VRプロセス優先度最大化

### Virtual Desktop環境
- ✅ ネットワーク遅延軽減: 10-30ms
- ✅ Wi-Fi最適化
- ✅ ワイヤレスVR安定性向上
- ✅ 自動復旧による安定性向上

### 🆕 監視・復旧機能
- ✅ **リアルタイム性能監視**
- ✅ **自動復旧による稼働率向上**
- ✅ **詳細なログ記録**
- ✅ **プロアクティブな問題検出**

### 🆕 電源断復旧機能
- ✅ **Windows起動時の自動VR環境構築**
- ✅ **電源断からの完全自動復旧**
- ✅ **依存関係を考慮した起動順序**
- ✅ **起動失敗時のリトライ機能**
- ✅ **🆕 VRChat自動起動によるVR体験の即座開始**

## 🔧 最適化内容

### VR専用システム設定
- VR用電源管理最適化
- USB電源管理無効化
- VR専用GPU設定
- フレームタイム最適化

### ネットワーク最適化（Virtual Desktop）
- TCP/UDP低遅延設定
- Wi-Fi省電力機能無効化
- QoS設定によるVR優先化
- パケット優先度最適化

### メモリ・プロセス最適化
- VR用仮想メモリ設定
- VRプロセス高優先度設定
- 非VRプロセス優先度低下
- ガベージコレクション最適化

## 📊 VR専用監視項目

### FPS目標値
- **理想**: 90FPS（VRヘッドセット標準）
- **推奨**: 75FPS以上
- **最低**: 60FPS（VR酔い防止）

### フレームドロップ許容値
- **許容**: 5%以下
- **警告**: 10%以上
- **危険**: 15%以上（使用中止推奨）

### フレームタイム
- **理想**: 11.1ms (90FPS)
- **許容**: 13.3ms (75FPS)
- **限界**: 16.7ms (60FPS)

### システム監視項目
- **CPU温度**: 80°C以下推奨
- **GPU温度**: 85°C以下推奨
- **メモリ使用率**: 80%以下推奨
- **VRAM使用率**: 90%以下推奨

## ⚙️ VRChat推奨設定

### パフォーマンス設定
- Avatar Performance Ranking: **有効**
- Safety Settings: 適切に設定
- Graphics Quality: **Medium-High**
- Anti-Aliasing: **MSAA 2x**

### VR Comfort設定
- Comfort Turning: 必要に応じて
- Personal Space: 適切に設定
- Motion Sickness Reduction: **有効**

## 🌐 Virtual Desktop推奨設定

### ネットワーク環境
- **Wi-Fi 6 (802.11ax)** または **Wi-Fi 6E** 使用推奨
- **5GHz帯域**を使用（2.4GHz帯域は避ける）
- ルーターとPCを**有線接続**
- 他のWi-Fi機器の使用を最小限にする

### Virtual Desktop設定
- **ビットレート**: 50-150Mbps（環境に応じて調整）
- **解像度**: ヘッドセットの解像度に合わせる
- **リフレッシュレート**: 72Hz または 90Hz
- **コーデック**: H.264（安定性重視）またはHEVC（品質重視）

## 🛠️ 必要環境

### Python環境（監視・分析ツール用）
```bash
# 依存関係インストール
pip install -r requirements.txt
```

### 追加依存関係
- `streamlit>=1.28.0` - ダッシュボード用
- `pandas>=1.5.0` - データ処理用
- `tqdm>=4.64.0` - 進行状況表示用

### 最低システム要件
- **CPU**: Intel i5-8400 / AMD Ryzen 5 2600以上
- **GPU**: GTX 1060 / RX 580以上
- **RAM**: 16GB以上
- **OS**: Windows 10/11

### 推奨システム要件
- **CPU**: Intel i7-10700K / AMD Ryzen 7 3700X以上
- **GPU**: RTX 3070 / RX 6700 XT以上
- **RAM**: 32GB以上
- **ネットワーク**: Wi-Fi 6 (802.11ax)以上

## 🚨 トラブルシューティング

### VRヘッドセット未検出
1. ヘッドセットドライバー再インストール
2. USBポート変更
3. VRソフトウェア再起動

### FPS低下
1. VRChat設定でAvatar制限
2. 他のVRアプリ終了
3. GPU温度確認
4. レンダリング解像度を下げる

### Virtual Desktop接続不安定
1. Wi-Fi環境確認（5GHz帯域使用）
2. ビットレート調整（低めから開始）
3. ルーター設定確認（QoS、ポート開放）

### VR酔い発生
1. FPS 60以下の場合は使用中止
2. フレームタイム確認
3. VRヘッドセット調整
4. Comfort設定有効化

### ダッシュボード・復旧サービス関連
1. **Streamlitが起動しない**
   - Python依存関係を再インストール
   - ポート8501が使用中でないか確認

2. **CPU/GPU温度が表示されない**
   - OpenHardwareMonitor/LibreHardwareMonitorをインストール
   - 管理者権限で実行

3. **自動復旧が動作しない**
   - Virtual Desktopのインストールパスを確認
   - ログファイル（vr_auto_recovery.log）を確認

### 🆕 スタートアップ関連
1. **自動起動が動作しない**
   - Windows起動時の自動実行設定を確認
   - ログファイル（vr_startup_manager.log）を確認

2. **SteamVRが起動しない**
   - Steamが先に起動しているか確認
   - SteamVRのインストールパスを確認

3. **起動順序の問題**
   - 起動遅延時間を調整（デフォルト30秒）
   - 各アプリケーションの起動完了を確認

4. **🆕 VRChatが起動しない**
   - SteamVRが正常に起動しているか確認
   - VRChatのインストールパスを確認
   - VRヘッドセットが正しく接続されているか確認

## ⚠️ 重要な注意点

- **管理者権限**での実行が必須
- VRヘッドセット**装着前**に最適化実行
- VRChatは必ず**VRモード**で起動
- 他のVRアプリケーションは終了
- 最適化後は**PC再起動**推奨
- **ダッシュボードは常時起動推奨**
- **自動復旧サービスはバックグラウンド実行推奨**
- **🆕 スタートアップ設定後はPC再起動で動作確認**
- **🆕 VRChatの自動起動にはSteamVRの正常起動が必要**

## 🔄 定期メンテナンス

### 週1回
- 一時ファイルクリーンアップ
- VRChatキャッシュクリア
- Virtual Desktopキャッシュクリア
- 自動復旧ログの確認
- **🆕 スタートアップログの確認**

### 月1回
- 最適化スクリプト再実行
- ドライバー更新確認
- VRソフトウェアアップデート確認
- Python依存関係の更新
- **🆕 スタートアップ設定の動作確認**

## 📞 サポート

詳細な設定方法やトラブルシューティングについては、以下のガイドファイルを参照してください：

- `VR環境専用ガイド.txt` - VR環境全般の詳細ガイド
- `Virtual Desktop専用ガイド.txt` - Virtual Desktop環境の詳細設定

### ログファイル
- `vr_auto_recovery.log` - 自動復旧サービスのログ
- `vr_startup_manager.log` - **NEW!** スタートアップマネージャーのログ
- Streamlitダッシュボードのブラウザコンソール

---

**注意**: このツールはVR環境専用です。通常のPC環境での使用は想定されていません。 