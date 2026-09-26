Trigger:            root 常駐行程啟動了可寫腳本，看起來像 root RCE，實際子行程已降權
Class:              mindset
Raw-observation:    auction_watcher.sh 以 root 跑，但 cmdline 是 `sudo -u www-data php …/auction_watcher.php`；改網站 PHP 仍是 www-data
Generalized-claim:  看到「root 父行程 + 可寫被載入檔」時，下一刀是觀測子行程的 uid／完整命令列，不是假設父行程權限等於執行權限
Sightings(n=1):     本場 watcher：root bash + sudo -u www-data php
Reverse-test:       不會害事；只是多一次 observe，避免過早改檔
De-specified:       問題軸（執行者權限以子行程為準，不是父 PID）
Target-file:        hunt-loop.md / H4 附近（若升級）
Consensus-tier:     中度
Status:             quarantined
Subtraction:        無（n=1，不 promote）
