# Candidate Patch: 2026-08-14 — 空 DNS 不關閉其它命名通道

Trigger:            材料裡出現「dev site」這類名字，DNS 查不到 A，副駕駛就不再測 HTTP Host／SNI，直到指揮點名 vhost／子域爆破
Class:              mindset
Raw-observation:    changelog 寫 integrated with dev site。已測：Host bruno.vl／brunodc、路徑 /dev /scan、DNS A dev.bruno.vl（無紀錄）。下一步改打 apex 的 10.10.100.55，之後寬度 batch 也只補 AD 漏埠／LDAP／SMB／Kerberos／RPC，沒有 Host: dev.bruno.vl，也沒有 vhost fuzz。指揮必須說「ffuf 進行 subdomain 爆破」才打出 Host:dev → 200／2719。IIS 認 Host，不需要該名有 A 紀錄。
Generalized-claim:  「名字在不在」不是單一事實。DNS A／AAAA、HTTP Host、TLS SNI、SPN／UPN 是不同通道。一條通道空（無 A、NXDOMAIN、路徑 404）只能關閉那一條，不能關閉「這個標籤不當名字用」。材料點到的短名，在放棄該假設前至少要點名測過仍未測的通道。
Sightings(n=1):     本場 dev site：有字、無 DNS A、有 IIS vhost
Reverse-test:       不會害事：多一次 Host: <hint>.<domain> 或一輪 vhost fuzz，比把假設整面關掉便宜。反例「對每個 404 路徑都當 vhost 爆破」才會膨脹——閘在「材料或證書已點名的標籤」與「仍有未測命名通道」，不是凡 web 必 ffuf。
De-specified:       問題軸：一個名字標籤在某一解析通道落空後，還有哪些通道沒測？
Target-file:        references/anti-blindspot.md（命名／表示軸）；htb-preflight 開局 HTTP 條可加 illustration
Consensus-tier:     中度
Status:             quarantined-needs-2nd-sighting
Subtraction:        升級時避免再寫「先 DNS 再 vhost」這種被讀成閘門的順序；DNS 只是其中一條通道

四態：quarantined-needs-2nd-sighting
