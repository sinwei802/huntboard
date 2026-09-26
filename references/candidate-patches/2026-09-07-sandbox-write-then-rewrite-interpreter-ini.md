Trigger:            特權行程用 interpreter + 磁碟上的 ini 跑不信任程式碼；disable_functions 沒列到寫檔函式，且 ini 落在 basedir 內
Class:              route
Raw-observation:    gaveld 以 root 跑 php -c /opt/gavel/.config/php/php.ini；fopen/system 被禁但 file_put_contents 可寫 hs_probe；覆寫該 ini 後下一次 submit 的 system() 抄出 root.txt
Generalized-claim:  沙箱黑名單先盤「沒被禁的寫入函式」；若 interpreter 的設定檔在可寫 basedir 內，下一探是改那份設定再觸發同一載入器，不是換執行者
Sightings(n=1):     本場 gaveld __sandbox_eval + php.ini 在 open_basedir 內
Reverse-test:       在 ini 不在 basedir、或寫入函式也在黑名單時套用會空轉，不會害事
De-specified:       問題軸（黑名單差集 + 載入器設定檔是否落在寫入面）
Target-file:        tactical-search.md（身份／sandbox 搜尋鍵）
Consensus-tier:     中度
Status:             quarantined
Subtraction:        無（n=1，不 promote）
