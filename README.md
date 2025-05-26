# VRChat VR環境専用最適化ツール 🥽

VRヘッドセット（Oculus/Meta Quest、SteamVR、WMR等）およびVirtual Desktop環境でのVRChat最適化に特化したツールセットです。

## 🎯 概要

このツールセットは、VR環境でのVRChat体験を大幅に改善するために設計されています：

- **VR FPS向上**: 20-40%のパフォーマンス向上
- **フレームドロップ軽減**: VR酔い防止
- **ネットワーク遅延軽減**: Virtual Desktop環境での快適性向上
- **VRヘッドセット別最適化**: 各デバイスに特化した設定

## 📁 ファイル構成

### 🔧 最適化スクリプト
- `VRChat_VR_Optimizer_Clean.ps1` - VR環境用最適化スクリプト（クリーン版）
- `VRChat_VR_Optimizer_Fixed.ps1` - VR環境用最適化スクリプト（修正版）
- `VirtualDesktop_VRChat_Optimizer_Clean.ps1` - Virtual Desktop専用最適化

### 📊 監視・分析ツール
- `VRChat_VR_Performance_Monitor.ps1` - VR環境用パフォーマンス監視
- `vrchat_vr_fps_analyzer.py` - VR環境用FPS分析ツール（Python）

### 📖 ガイド・設定
- `VR環境専用ガイド.txt` - VR環境専用使用ガイド
- `Virtual Desktop専用ガイド.txt` - Virtual Desktop使用ガイド
- `requirements.txt` - Python依存関係

## 🚀 クイックスタート

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

### Python環境（FPS分析ツール用）
```bash
# 依存関係インストール
pip install -r requirements.txt
```

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

## ⚠️ 重要な注意点

- **管理者権限**での実行が必須
- VRヘッドセット**装着前**に最適化実行
- VRChatは必ず**VRモード**で起動
- 他のVRアプリケーションは終了
- 最適化後は**PC再起動**推奨

## 🔄 定期メンテナンス

### 週1回
- 一時ファイルクリーンアップ
- VRChatキャッシュクリア
- Virtual Desktopキャッシュクリア

### 月1回
- 最適化スクリプト再実行
- ドライバー更新確認
- VRソフトウェアアップデート確認

## 📞 サポート

詳細な設定方法やトラブルシューティングについては、以下のガイドファイルを参照してください：

- `VR環境専用ガイド.txt` - VR環境全般の詳細ガイド
- `Virtual Desktop専用ガイド.txt` - Virtual Desktop環境の詳細設定

---

**注意**: このツールはVR環境専用です。通常のPC環境での使用は想定されていません。 