# 独立した包含計算の契約

入力と独立性は PLAN.md/input-manifest.json。geometry.json の十進数は両端を MPFR の RoundDown/RoundUp で読む。2進浮動小数への丸めを経由しない。160 bit の MpInterval と CAPD 37057e5899bccaa6cd5701057b7e6ea5e232ef8b の MpITaylor（24次）/MpC1Rect2Set を使う。ステップ選択の tolerance 引数だけは CAPD API に合わせた double 1e-20 であり、証明の誤差上限そのものではない。包含の剰余は区間 Taylor 法が検査する。

## 模型と初期集合

lambda による SPEC の方程式を独立に式文字列へ構築する。U=1+1/rp+1/rm、grad U=(-x/rp^3-x/rm^3, -(z-1)/rp^3-(z+1)/rm^3)、v'=2/U*(grad U-v*(grad U dot v))。初期の null 曲面 (q,0,w,sqrt(1-w²)) を含む集合を作る。g(w)=sqrt(1-w²) とし、w=w0+dw、g(w) in g(w0)+g'(w0)*dw+g''(W)*dw²/2、g''(W)=-1/(1-W²)^(3/2)。q,w は (u,s) の affine な関数なので、その一次の相関を doubleton の C*r0 に保ち、二次剰余と係数の丸めを区間 x に入れる。このoverloadのconstructorは区間 x/C を保持する。固定sourceの OdeSolver.h computeTaylorCoefficients は x の区間係数をそのまま計算し、C0DoubletonSet.hpp move は y+剰余と区間行列の寄与を包含した後に split(result.m_x, data.y) と split(result.m_C, data.deltaC) で幅を誤差へ移す。constructorで幅を捨てる処理ではなく、初回stepでも区間 x/C の不確かさを残すことをソースで確認した。外側集合の非null点も含むが、その流れが元のnull初期グラフを包含すればよい。

## 帰還と tube

MpIPoincareMap（非区間の MpPoincareMap ではない）、座標断面 z=0、MinusPlus を使う。固定sourceの PoincareMap_templateMembers.h の integrateUntilSectionCrossing は初期断面を離れ、負側へ到達したのち最初の正向き交差まで進む。各stepで断面を含むtubeの法線速度が0を含めば checkTransversability は例外を投げる。したがって同じstep内の往復を黙って飛ばさない。独自 Audit 型は solver が呼ぶ move の両overloadを捕捉し、すべての getLastEnclosure（捨てた試行/帰還時刻の改良用stepも含む）で次を要求する。

- r±−1/5>0 と 64−x²−z²>0。
- tube が z=0 を含めば vz が0を含まない。
- move数<20000、lambda<100。これは計算停止の条件であり、不帰還の証明ではない。

初期は z=0, vz>0。最終は returnTime>0, return vz>0、途中の下向き交差の監査記録>0を要件にする。PoincareMap の affine coordinate overload は区間 Newton で囲った可変帰還時刻で A*(P-c) を評価する。固定時刻の像を P とみなさない。戻り値の第0,1座標を target (U,S) とし、第3座標は vz のまま保つ。A は指定された2次元枠の逆行列の区間包含。

## 刻み設定の履歴

v1は tolerance1e-35/maxStep0.1。O全帯は40秒上限、O左右全辺は516/517stepでtube横断性未確定。残りの粗い試行を打ち切って出力を保存した。v2は160bitと24次の区間剰余検査を保ち、刻み選択tolerance1e-20/maxStep0.2へ。既知解の包含と模型の対称点(2,0,0,1)での加速度−8/[5(sqrt5+2)]との整合を再検査した。まず各遷移のsを16分割した最初のcellでC1/L/Rの計算可能性を調べる。このsampleだけで全域の成功を主張しない。

## 判定

C1: 全 (u,s) cell の S 包含が (-1,1) 内。C2: 左辺全 s cell の U 上端<-1、右辺全 s cell の U 下端>1。全域を覆う閉cellの重複は問題ない。一つの失敗した包含だけで数学的な反例とはしない。CONTRARY は、非空cellの像全体が要求される領域の外に区間的に囲われた場合だけの反例候補。最終判定では元null初期集合の非空性・帰還の前提も確認する。ERROR/幅の広い包含は「判定できない」。追加細分を行う場合は残りのMac60分枠で止める。

## 道具の検査

外向き十進parse、除算、平方根の包含。調和振動子 z'=vz, vz'=-z の z=0,vz=1 からの上向き帰還について 2pi と既知の帰還点を含むこと、初期lambda=0を返していないこと、独自auditが上下の交差を捕捉することを確認する。vz=0を含むtubeの負の対照は拒否されなければならない。これらは模型のC1/C2成功を意味しない。

## 平均値形式による追加の囲い（M1）

return_mvt.cpp は同じ場・初期集合・全tube監査を使う。CAPD PoincareMap の dF overload が囲うのは可変時刻で評価した「固定時刻の流れ」の初期値微分 DΦ（SectionDerivativesEnclosure の derivativeOfFlow）。断面 z=0 の n=(0,1,0,0) とし、DP=[Id−f nᵀ/(nᵀf)]DΦDι。target座標行列 A を左から掛けて J=A[Id−f nᵀ/(nᵀf)]DΦDι を区間評価する。Dι は q,w の affine な列と g'(W)=−W/sqrt(1−W²) を用いる。これを全cellの初期集合からの厳密流れ微分で評価する。全cellで最初の帰還が存在し横断的であることを先に確認するため、その帰還枝は滑らかである。

別途、同じcellのパラメータ中心のnull初期点の帰還を affine coordinate overload で囲う。凸なパラメータ長方形の中心からの線分に平均値定理を適用し、P(cell) ⊂ P(center)+J*(cell−center) とする。この二つの積分に要した時間はともに計算枠へ算入する。通常のaffine像（C1）と平均値像（M1）は同じC1条件の別の十分判定であり、新しい科学的条件ではない。

追加controlは z'=vz,vz'=-z, x'=vx'=0 の帰還写像が(q,w)で恒等写像になることを用い、画像が入力長方形を含み、その導関数が単位行列を含むことを検査する。既存の丸め/模型/最初の帰還/接触拒否controlも再実行する。

## 気づき

- 固定CAPDのcapd-config/pkg-config出力は空白を含むworkspace pathを正しくquoteしないため、当環境ではpkg-configも未導入だった。数値計算に必要なライブラリは既にあるため、追加installせず、ビルド済みライブラリへの引数配列を明示した。
