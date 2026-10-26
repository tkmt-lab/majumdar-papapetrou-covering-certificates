# R029 独立確認の開始記録

依頼67dcf3e2を2026-10-25 17:55 UTCに受理。8時間の上限は安全側に初回送信17:35:07 UTCから数え、2026-10-26 01:35:07 UTCまで。Mac計算はcanonical queue、1本2GiB・最大4core、合計60分以内。R015 next40の既存Colab制御とwatchを維持する。

入力はcommit15a879de859aのCLAIMS.json、SPEC.md、DESIGN.mdの4.1.1・4.1.2だけ。hset-check、report-next2、DESIGN4.1.3以降/5節、SUBAGENTS、verify_hsetsは読まない。許された抜粋内の軌道診断数値は証明に使わない。

3箱・5部分帯を十進有理数で固定した。check_geometry.pyで枠の非退化・q射影の分離・同じ箱内の部分帯の分離を再計算。5辺の行列についてQ(phi)上の正固有ベクトルを厳密に確かめ、rho=phiを得た。これは被覆と最初の帰還の全条件が通った場合のentropy下界だけであり、C1/C2の成功ではない。

## CAPDの準備

固定source37057e589...は既存R015キャッシュにありclean。Macはarm64、既存GCC16はaarch64-apple-darwin25。既存Macビルドは未完成でcapd-configがない。FILIB設定はソースのCMakeがApple ARMを拒否するが、同じ固定sourceにNATIVEのARM64丸め実装がある。研究用の隔離した.cache/buildにNATIVE設定でビルドする。主計算はMPFRのMpInterval/C1-Lohnerを使い、doubleの区間演算へ精度を落とさない。新しいruntime・compiler・サービス・外部cloud・システムinstallは追加しない。局所的で可逆なビルド設定に限定し、最初に多倍長の包含・丸めと既知解で動作を検査する。互換性問題が残れば別方式へ黙って移らず報告する。

ビルドはqueue経由、2core/2GiB、540秒上限。実時間をMac60分枠へ算入する。成功後の数値計画は、元null初期グラフを含む相関つき集合、全tubeのD内包含、z=0での最初の上向き帰還の隔離と横断性、可変帰還時刻での(x,vx)包含を順に検査する。点・角だけの成功で全C1/C2を主張しない。

## 現在の待機点（2026-10-25 18:15 UTC）

CAPD buildとMPFR/既知調和帰還/模型対称点/接触の拒否controlはPASS。commit1f8e773e7、d149e1414。粗いO全帯/左右辺はtime上限またはtube横断性未確定だったため、未実施分を打ち切って保存した。新設定の160bit/24次、刻み選択1e-20、maxStep0.2でs16分割の最初のcellを5辺×C1/L/Rで確認する300秒の試行がcanonical queue1026-031426-a43aで実行中。終了通知後にrefined-pilot-result.jsonを読み、必要な全域細分と残り計算枠を判断する。これは全域の最終判定ではない。完了済みジョブを保守的な開始-終了差で計上すると484秒、現在の試行に300秒を予約。上限3600秒と初回送信から8時間は維持。R015監視継続、最新C0audit5248。

## 現在の待機点（2026-10-25 18:32 UTC）

15cell pilotと17cell refinementの全出力を回収。MVT追加実装のcontrolはPASSだが、実際の6cellでは全て未判定で、区間の幅は改善しなかった（保存済み）。改善を確認した従来のaffine包含の細分を採用する。

canonical queue1026-033052-443aに1ジョブ4core/2GiBで登録。run_coverage.py が独立した数値プロセスを最大4本だけ実行し、O→O・B→AのC1をu4/s32、O→A・B→Oをu8/s32、これら4辺のC2左右をs16で全域走査する。計896 root cells、同じsourceで既にPASSしたcellはhashを照合して再利用。未確定cellはu16/s64までの限定細分。A→Bは別途未確定のまま残す。開始後2100秒で必ず止まり、これまでの保守的なMacジョブ経過1209秒＋次の2100秒＋終了検知余裕60秒=3369秒<3600秒。これは承認済みの4core・1ジョブ・2GiB内の数値計算で、agentの起動ではない。

終了通知後にmailbox67dcf3e2をretry/acceptし、coverage-result.jsonの完了・入力hashとcheck_coverage.pyの厳密有理数unionを確認する。PASSしたcellの有限閉長方形が帯全域を覆うことを別に数え、点の成功やジョブ終了コードだけでC1/C2を成立にしない。A→Bを含む全5辺が未確認なら黄金比のentropy下界は条件付きのまま報告する。時間枠を超える追加計算は統括へ相談する。

R015は同一worker15115でC1-prefix referenceに進行（18:23 UTCに128件）、既存watchとdeadlineは維持。

## この依頼の最終判定（2026-10-25 19:10 UTC以降）

queue1026-033052-443aは全作業を終えてexit0。新規916cell(900PASS/16未確定後に細分)+再利用12cell。check_coverage.pyでOO/OA/BO/BAのC1面積と左右辺の被覆長を各1と確認し、4遷移のC1/C2を成立と判定。A→BはC1面積0・左右の被覆長各1/128で未判定。全5辺が未確認なのでentropy下界は条件付きのまま。報告は ../report-next3-2026-10-26.md。追加計算枠/設計は統括の次指示待ちとし、この依頼の3値判定・成果物保存を完了する。Mac保守的合計3213秒(53分33秒)、上限内。R015監視は別に継続。

## 気づき

- 全帯を一度に運ぶとCAPDでも断面近くのtubeが膨らみ、横断性の包含が未確定になる。細分で改善するかは未確認。
- 可変帰還時刻の微分を組み込んだ平均値形式は、今回の区間行列では過大評価が大きく、直接のaffine包含より広くなった。
